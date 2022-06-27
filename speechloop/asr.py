import abc
import asyncio
import base64
import datetime
import json
import time
import warnings
import atexit
from os import environ
from time import monotonic
from urllib.parse import urlencode

import requests
import websockets

try:
    from amazon_transcribe.client import TranscribeStreamingClient
    from amazon_transcribe.handlers import TranscriptResultStreamHandler
    from amazon_transcribe.model import TranscriptEvent
except ImportError as e:
    print(f"Amazon not imported, for reason:{e}")

try:
    from google.cloud import speech_v1 as speech
except ImportError as e:
    print(f"Google not imported, for reason:{e}")


from speechloop.file_utils import valid_readable_file, disk_in_memory

try:
    import docker
    DOCKER_CLIENT = docker.from_env()
except Exception as e:
    warnings.warn("Either docker is not installed OR the docker client cannot be connected to. " "This might be ok if using just APIs")


class AsrNotRecognized(Exception):
    pass


class InvalidConfigPath(Exception):
    pass


class APIKeyError(Exception):
    pass


class ASR(metaclass=abc.ABCMeta):
    """
    Args:
        name: The name of the model
        asrtype: The type of the speech rec
    """

    def __init__(self, name, asrtype, sr=16000):
        self.init_starttime = datetime.datetime.now()
        self.name = name
        self.asrtype = asrtype
        self.init_finishtime = None
        self.total_inf_time = datetime.datetime.now() - datetime.datetime.now()
        self.verbose = True
        self.kill_containers_on_quit = True
        self.sr = sr

        if self.asrtype == "docker-local" and self.kill_containers_on_quit:
            atexit.register(self.kill)

    def finish_init(self):
        self.init_finishtime = datetime.datetime.now()

    def add_time(self, time_to_add):
        self.total_inf_time += time_to_add

    def return_error(self, error_msg="<asr_error>"):
        return error_msg

    def kill(self):
        kill_container(self.dockerhub_url, verbose=self.verbose)

    @abc.abstractmethod
    def execute_with_audio(self, audio):
        pass

    def read_audio_file(self, path_to_audio):
        if valid_readable_file(path_to_audio):
            audio = open(path_to_audio, "rb").read()
            return self.execute_with_audio(audio)


class Coqui(ASR):
    """
    Coqui
    """

    def __init__(self):
        super().__init__("cq", "docker-local")
        self.uri = "http://localhost:3200/transcribe"
        self.dockerhub_url = "robmsmt/sl-coqui-en-16k:latest"
        self.shortname = self.dockerhub_url.rsplit("/")[-1].rsplit(":")[0]
        self.longname = "coqui"
        launch_container(self.dockerhub_url, {"3200/tcp": 3200}, verbose=self.verbose, delay=3)
        self.finish_init()

    def execute_with_audio(self, audio):
        b64 = base64.b64encode(audio).decode("utf-8")
        json_message = {"b64_wav": b64, "sr": 16000}
        r = requests.post(self.uri, json=json_message)
        if r.status_code == 200:
            try:
                response = r.json()["transcript"]
                return response
            except KeyError:
                return self.return_error()
        else:
            return self.return_error()


class Sphinx(ASR):
    """
    Vosk
    """

    def __init__(self):
        super().__init__("sp", "docker-local")
        self.uri = "http://localhost:3000/transcribe"
        self.dockerhub_url = "robmsmt/sl-sphinx-en-16k:latest"
        self.shortname = self.dockerhub_url.rsplit("/")[-1].rsplit(":")[0]
        self.longname = "sphinx"
        launch_container(self.dockerhub_url, {"3000/tcp": 3000}, verbose=self.verbose, delay=2)
        self.finish_init()

    def execute_with_audio(self, audio):
        b64 = base64.b64encode(audio).decode("utf-8")
        json_message = {"b64_wav": b64, "sr": 16000}
        r = requests.post(self.uri, json=json_message)
        if r.status_code == 200:
            try:
                response = r.json()["transcript"]
                return response
            except Exception as e:
                warnings.warn(f"Engine did not return transcript: {e}")
                return self.return_error()
        else:
            return self.return_error()


class Vosk(ASR):
    """
    Vosk
    """

    def __init__(self):
        super().__init__("vs", "docker-local")
        self.uri = "ws://localhost:2800"
        self.dockerhub_url = "robmsmt/sl-vosk-en-16k:latest"
        self.shortname = self.dockerhub_url.rsplit("/")[-1].rsplit(":")[0]
        self.longname = "vosk"
        self.container_found = False
        launch_container(self.dockerhub_url, {"2700/tcp": 2800}, verbose=self.verbose, delay=5)
        self.finish_init()

    def execute_with_audio(self, audio):
        audio_file = disk_in_memory(audio)
        return asyncio.get_event_loop().run_until_complete(self.send_websocket(audio_file))

    async def send_websocket(self, audio_file):
        async with websockets.connect(self.uri) as websocket:
            all_finals = ""
            all_partials = []
            while True:
                partial = None
                data = audio_file.read(1024 * 16)
                if len(data) == 0:
                    break
                await websocket.send(data)
                try:
                    partial_json = json.loads(await websocket.recv())
                    partial = partial_json["partial"]
                    if partial:
                        all_partials.append(partial)
                except KeyError:
                    all_finals += partial_json["text"] + " "

            await websocket.send('{"eof" : 1}')
            final_result = json.loads(await websocket.recv())["text"]

            if len(all_finals) > 0 and len(final_result) == 0:
                return all_finals
            elif len(all_finals) > 0 and len(final_result) > 0:
                return all_finals + f" {final_result}"
            elif len(final_result) == 0 and len(all_partials) > 0:
                return all_partials[-1]
            else:
                return final_result


class Azure(ASR):
    """
    Sign up to Speech service at: https://portal.azure.com
    create project and set one of the 2 keys to be passed in through OS ENV var: AZURE_KEY
    """

    def __init__(self, apikey=None):

        super().__init__("az", "cloud-api")
        self.longname = "azure"
        self.shortname = "az"
        self.key = apikey if apikey is not None else environ.get("AZURE_KEY")  # APIKEY param takes priority over ENV
        self.location = "eastus"
        self.language = "en-US"
        self.profanity = "False"
        self.start_time = monotonic()
        self.credential_url = f"https://{self.location}.api.cognitive.microsoft.com/sts/v1.0/issueToken"
        settings = urlencode({"language": self.language, "format": "simple", "profanity": self.profanity})
        self.url = f"https://{self.location}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?{settings}"

        self.renew_token()

        if self.verbose:
            print(f"Using {self.longname}")

    def now(self):
        return monotonic()

    def renew_token(self):
        try:
            cred_req = requests.post(
                self.credential_url,
                data=b"",
                headers={
                    "Content-type": "application/x-www-form-urlencoded",
                    "Content-Length": "0",
                    "Ocp-Apim-Subscription-Key": self.key,
                },
            )
            if cred_req.status_code == 200:
                self.access_token = cred_req.text
                self.azure_cached_access_token = self.access_token
                self.start_time = monotonic()
                self.azure_cached_access_token_expiry = (
                    self.start_time + 600
                )  # according to https://docs.microsoft.com/en-us/azure/cognitive-services/Speech-Service/rest-apis#authentication, the token expires in exactly 10 minutes
            else:
                raise APIKeyError("Cannot renew token")
        except APIKeyError as e:
            raise APIKeyError(f"Error renewing token: {e}")

    def execute_with_audio(self, audio):

        if self.now() > self.azure_cached_access_token_expiry:
            self.renew_token()

        req = requests.post(self.url, data=audio, headers={"Authorization": f"Bearer {self.access_token}", "Content-type": 'audio/wav; codec="audio/pcm"; samplerate=16000'})

        if req.status_code == 200:
            result = json.loads(req.text)
        else:
            return self.return_error

        if "RecognitionStatus" not in result or result["RecognitionStatus"] != "Success" or "DisplayText" not in result:
            return self.return_error

        res = result["DisplayText"].strip()
        final_result = res[:-1] if res.endswith(".") else res
        return final_result


class Aws(ASR):
    def __init__(self):

        super().__init__("aw", "cloud-api")
        # credentials will be auto retrieved from ~/.aws/credentials however in future should be overriden by param?

        self.longname = "aws"
        self.shortname = "aw"
        self.handler = None
        self.stream = None
        self.client = None

        if self.verbose:
            print(f"Using {self.longname}")

    def execute_with_audio(self, audio):
        audio_file = disk_in_memory(audio)
        return asyncio.get_event_loop().run_until_complete(self.write_chunks(audio_file))

    async def write_chunks(self, audio_file):

        self.client = TranscribeStreamingClient(region="us-east-1")
        self.stream = await self.client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )

        while True:
            data = audio_file.read(1024 * 16)
            if len(data) == 0:
                await self.stream.input_stream.end_stream()
                break
            await self.stream.input_stream.send_audio_event(audio_chunk=data)

        async for event in self.stream.output_stream:
            if isinstance(event, TranscriptEvent):
                result = await self.handle_transcript_event(event)
            else:
                print(event)

        # todo this is not a very good implementation but quick first attempt
        while True:
            # wait until generator has been iterated over
            await asyncio.sleep(0.1)
            if result[-1].is_partial == False:
                break

        # await asyncio.sleep(0.1)
        transcript = result[-1].alternatives[-1].transcript

        if transcript.endswith("."):
            # aws ends always with a period, let's kill it.
            transcript = transcript[:-1]

        return transcript

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        return results


class Google(ASR):
    def __init__(self, apikey=None):

        super().__init__("gg", "cloud-api")
        # Check GOOGLE_APPLICATION_CREDENTIALS

        if apikey and valid_readable_file(apikey, quiet=True):
            environ["GOOGLE_APPLICATION_CREDENTIALS"] = apikey
        else:
            if valid_readable_file("../models/google/google.json", quiet=True) and environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None:
                environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../models/google/google.json"
            if environ.get("GOOGLE_APPLICATION_CREDENTIALS") is None or not valid_readable_file(environ["GOOGLE_APPLICATION_CREDENTIALS"]):
                warnings.warn(
                    "INVALID CONFIG/PATH, please update env variable to where your GoogleCloud speech conf exists: \n "
                    "export GOOGLE_APPLICATION_CREDENTIALS=path/to/google.json \n"
                )
                raise InvalidConfigPath

        self.client = speech.SpeechClient()
        self.longname = "google"
        self.shortname = "gg"
        self.configpath = environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        self.recognition_config = speech.RecognitionConfig(
            dict(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.sr,
                language_code="en-US",
            )
        )
        if self.verbose:
            print(f"Using {self.longname} with config: {self.configpath}")

    def execute_with_audio(self, audio):

        rec_audio = speech.RecognitionAudio(content=audio)
        response = self.client.recognize(config=self.recognition_config, audio=rec_audio)

        transcript_list = []
        for result in response.results:
            transcript_list.append(result.alternatives[0].transcript)

        if len(transcript_list) == 0:
            transcript = self.return_error
        else:
            transcript = " ".join(transcript_list)

        return transcript


def kill_container(dockerhub_url, verbose=True):
    for container in DOCKER_CLIENT.containers.list():
        if len(container.image.tags) > 0 and container.image.tags[-1] == dockerhub_url:
            if verbose:
                print(f"Docker container: {dockerhub_url} found. Killing...")
            container.stop()


def launch_container(dockerhub_url, ports_dict, verbose=True, delay=5):
    container_running = False
    for container in DOCKER_CLIENT.containers.list():
        if len(container.image.tags) > 0 and container.image.tags[-1] == dockerhub_url:
            if verbose:
                print(f"Docker container: {dockerhub_url} found running")
            container_running = True

    if not container_running:
        if verbose:
            print(f"Docker container: {dockerhub_url} NOT found... downloading and/or running...")
        DOCKER_CLIENT.containers.run(
            dockerhub_url,
            detach=True,
            ports=ports_dict,
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
        )
        if verbose:
            print(f"{dockerhub_url} Downloaded. Starting container...")
        time.sleep(delay)


def create_model_objects(wanted_asr: list) -> list:
    list_of_asr = []

    print(wanted_asr)
    for asr in wanted_asr:
        if asr == "all":
            list_of_asr = [Vosk(), Sphinx(), Coqui(), Google(), Aws(), Azure()]
        elif asr == "vs":
            list_of_asr.append(Vosk())
        elif asr == "sp":
            list_of_asr.append(Sphinx())
        elif asr == "cq":
            list_of_asr.append(Coqui())
        elif asr == "gg":
            list_of_asr.append(Google())
        elif asr == "aw":
            list_of_asr.append(Aws())
        elif asr == "az":
            list_of_asr.append(Azure())
        else:
            raise AsrNotRecognized("ASR not recognised")

    return list_of_asr
