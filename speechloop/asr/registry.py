from speechloop.asr.errors import AsrNotRecognized
from speechloop.asr.vosk import Vosk
from speechloop.asr.sphinx import Sphinx
from speechloop.asr.coqui import Coqui
from speechloop.asr.google import Google
from speechloop.asr.aws import Aws
from speechloop.asr.azure import Azure


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
