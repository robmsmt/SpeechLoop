from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import tempfile
from io import BytesIO
from base64 import b64decode
import soundfile

# from pocketsphinx import get_model_path
# from pocketsphinx.pocketsphinx import Decoder
# from pocketsphinx import AudioFile
import os
from pocketsphinx import get_model_path
from pocketsphinx.pocketsphinx import Decoder
import numpy as np

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
        return CMUPocketSphinxASREngine()


class CMUPocketSphinxASREngine(ASREngine):
    def __init__(self):
        # https://github.com/cmusphinx/pocketsphinx-python/blob/master/example.py
        config = Decoder.default_config()
        config.set_string("-logfn", "/dev/null")
        config.set_string("-hmm", os.path.join(get_model_path(), "en-us"))
        config.set_string("-lm", os.path.join(get_model_path(), "en-us.lm.bin"))
        config.set_string("-dict", os.path.join(get_model_path(), "cmudict-en-us.dict"))

        self._decoder = Decoder(config)

    def transcribe(self, bytes):

        wav_bytes = b64decode(bytes.encode("utf-8"))
        dm = disk_in_memory(wav_bytes)

        pcm, sample_rate = soundfile.read(dm)
        assert sample_rate == 16000
        pcm2 = (np.iinfo(np.int16).max * pcm).astype(np.int16).tobytes()

        self._decoder.start_utt()
        self._decoder.process_raw(pcm2, no_search=False, full_utt=True)
        self._decoder.end_utt()

        words = []
        for seg in self._decoder.seg():
            word = seg.word

            # Remove special tokens.
            if word == "<sil>" or word == "<s>" or word == "</s>":
                continue

            word = "".join([x for x in word if x.isalpha()])

            words.append(word)

        return " ".join(words)

    def __str__(self):
        return "CMUPocketSphinx"


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

    uvicorn.run(app, host="0.0.0.0", port=3000)
