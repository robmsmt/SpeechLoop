from speechloop.asr.base_asr import ASR
from speechloop.asr.container_utils import launch_container

import base64
import warnings

import requests


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
