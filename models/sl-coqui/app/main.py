from fastapi import FastAPI
from pydantic import BaseModel
import tempfile
from io import BytesIO
from base64 import b64decode
from stt import Model
import soundfile

app = FastAPI()


def disk_in_memory(wav_bytes):
    """
    this spooled wav was chosen because it's much more efficient than writing to disk,
    it effectively is writing to memory only and can still be read (by some applications) as a file
    """
    with tempfile.SpooledTemporaryFile() as spooled_wav:
        spooled_wav.write(wav_bytes)
        spooled_wav.seek(0)
        return BytesIO(spooled_wav.read())


class Audio(BaseModel):
    b64_wav: str
    sr: int = 16000


@app.get("/healthcheck")
async def healthcheck():
    return {"ok": "true"}


class ASREngine(object):
    def transcribe(self, bytes):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    @classmethod
    def create(cls):
        return Coqui()


class Coqui(ASREngine):
    def __init__(self):
        # https://stt.readthedocs.io/en/latest/_downloads/67bac4343abf2261d69231fdaead59fb/client.py
        self.asr = Model("coqui-stt-0.9.3-models.pbmm")

    def transcribe(self, bytes):

        wav_bytes = b64decode(bytes.encode("utf-8"))
        dm = disk_in_memory(wav_bytes)

        pcm, sample_rate = soundfile.read(dm, dtype="int16")
        assert sample_rate == 16000

        words = self.asr.stt(pcm)

        return words

    def __str__(self):
        return "Coqui"


engine = ASREngine.create()


@app.post("/transcribe")
async def transcribe(audio: Audio):

    try:
        transcript = engine.transcribe(audio.b64_wav)
        return {"transcript": transcript}
    except:
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3200)
