from speechloop.asr.base_asr import ASR
from speechloop.asr.errors import APIKeyError

import json
from time import monotonic
from os import environ
from urllib.parse import urlencode

import requests


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

