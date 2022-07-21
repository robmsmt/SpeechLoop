from speechloop.asr.base_asr import ASR
from speechloop.asr.container_utils import launch_container

import base64
import requests


class Nemo(ASR):
    """
    Nemo
    """

    def __init__(self):
        super().__init__("nm", "docker-local")
        self.uri = "http://localhost:3500/transcribe"
        self.dockerhub_url = "robmsmt/sl-nemo-en-16k:latest"
        self.shortname = self.dockerhub_url.rsplit("/")[-1].rsplit(":")[0]
        self.longname = "nemo"
        launch_container(self.dockerhub_url, {"3500/tcp": 3500}, verbose=self.verbose, delay=8)
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
