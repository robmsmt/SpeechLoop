
import os
from fastapi import FastAPI
from pydantic import BaseModel
import tempfile
from io import BytesIO
from base64 import b64decode
import argparse
# import soundfile
# import numpy as np
# import onnxruntime as rt
# import nemo
import nemo.collections.asr as nemo_asr
model = os.environ['MODELNAME']

app = FastAPI()
# nm = nemo_asr.models.EncDecCTCModel.from_pretrained(model_name="QuartzNet15x5Base-En")
# print(nemo_asr.models.EncDecRNNTBPEModel.list_available_models())
# nm = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name=args.model)
nm = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model)
#
#
# enc_dec_ctc_models = [(x.pretrained_model_name, nemo_asr.models.EncDecCTCModel.from_pretrained(model_name=x.pretrained_model_name)) for x in nemo_asr.models.EncDecCTCModel.list_available_models() if "en" in x.pretrained_model_name]
# enc_dec_ctc_bpe_models = [(x.pretrained_model_name, nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name=x.pretrained_model_name)) for x in nemo_asr.models.EncDecCTCModelBPE.list_available_models() if "en" in x.pretrained_model_name]
# enc_dec_rnn_t_bpe_models = [(x.pretrained_model_name, nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name=x.pretrained_model_name)) for x in nemo_asr.models.EncDecRNNTBPEModel.list_available_models() if "en" in x.pretrained_model_name]
# enc_dec_rnn_t_models = [(x.pretrained_model_name, nemo_asr.models.EncDecRNNTModel.from_pretrained(model_name=x.pretrained_model_name)) for x in nemo_asr.models.EncDecRNNTModel.list_available_models() if "en" in x.pretrained_model_name]
#
# all_models = enc_dec_ctc_models + enc_dec_ctc_bpe_models + enc_dec_rnn_t_bpe_models + enc_dec_rnn_t_models
# print(all_models)

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


# Next, we instantiate all the necessary models directly from NVIDIA NGC
# Speech Recognition model


@app.post("/transcribe")
async def transcribe(audio: Audio):

    try:
        wav_bytes = b64decode(audio.b64_wav.encode("utf-8"))

        # dm = disk_in_memory(wav_bytes)
        # pcm, sample_rate = soundfile.read(dm, dtype="int16")
        # todo cannot use disk memory since nemo lib needs file - in future replace with onnx: https://github.com/NVIDIA/NeMo/blob/main/tutorials/asr/ASR_with_NeMo.ipynb

        with tempfile.NamedTemporaryFile(mode='wb', delete=True, suffix='.wav') as f:
            f.write(wav_bytes)
            files_list = [f.name]
            print(files_list)
            transcript = nm.transcribe(paths2audio_files=files_list)

        return {"transcript": transcript[0][0]}
    except:
        raise


if __name__ == "__main__":
    import uvicorn
    print("starting...")
    uvicorn.run("main:app", host="0.0.0.0", port=3600)
