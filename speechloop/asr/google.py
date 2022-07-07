from speechloop.asr.base_asr import ASR
from speechloop.file_utils import valid_readable_file
from speechloop.asr.errors import InvalidConfigPath

from os import environ
import warnings


try:
    from google.cloud import speech_v1 as speech
except ImportError as e:
    print(f"Google not imported, for reason:{e}")


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
