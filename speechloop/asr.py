import abc
import asyncio
import base64
import datetime
import json
import time
import warnings
import atexit
from os import environ

import docker
import requests
import websockets
from google.cloud import speech_v1 as speech

from speechloop.file_utils import valid_readable_file, disk_in_memory

try:
    DOCKER_CLIENT = docker.from_env()
except Exception as e:
    warnings.warn("Either docker is not installed OR the docker client cannot be connected to. This might be ok if not using a local ASR (just APIs) \n")


class AsrNotRecognized(Exception):
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
        launch_container(self.dockerhub_url, {"3200/tcp": 3200}, verbose=self.verbose)
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
        launch_container(self.dockerhub_url, {"3000/tcp": 3000}, verbose=self.verbose)
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
        launch_container(self.dockerhub_url, {"2700/tcp": 2800}, verbose=self.verbose)
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
            elif len(final_result) == 0:
                return all_partials[-1]
            else:
                return final_result


class Google(ASR):
    def __init__(self, apikey=None):
        class InvalidGoogleConfigPath(Exception):
            pass

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
                raise InvalidGoogleConfigPath

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


def launch_container(dockerhub_url, ports_dict, verbose=True):
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
        time.sleep(5)


def create_model_objects(wanted_asr: list) -> list:
    list_of_asr = []

    print(wanted_asr)
    for asr in wanted_asr:
        if asr == "all":
            list_of_asr = [Vosk(), Sphinx(), Coqui(), Google()]
        elif asr == "vs":
            list_of_asr.append(Vosk())
        elif asr == "sp":
            list_of_asr.append(Sphinx())
        elif asr == "cq":
            list_of_asr.append(Coqui())
        elif asr == "gg":
            list_of_asr.append(Google())
        else:
            raise AsrNotRecognized("ASR not recognised")

    return list_of_asr
