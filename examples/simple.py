from speechloop.asr.vosk import Vosk
from speechloop.asr.google import Google
from speechloop.asr.sphinx import Sphinx
from speechloop.asr.coqui import Coqui

vs = Vosk()
sp = Sphinx()
cq = Coqui()
gg = Google()

# read file directly
print(f'file {vs.longname} -> {vs.read_audio_file("../speechloop/data/simple_test/wavs/109862_airplane_ch0_16k.wav")}')
print(f'file {sp.longname} -> {sp.read_audio_file("../speechloop/data/simple_test/wavs/109862_airplane_ch0_16k.wav")}')
print(f'file {cq.longname} -> {cq.read_audio_file("../speechloop/data/simple_test/wavs/109862_airplane_ch0_16k.wav")}')
print(f'file {gg.longname} -> {gg.read_audio_file("../speechloop/data/simple_test/wavs/109862_airplane_ch0_16k.wav")}')

# read in raw audio
raw_audio_file = open("../speechloop/data/simple_test/wavs/109862_airplane_ch0_16k.wav", "rb").read()
print(f"raw {vs.longname} -> {vs.execute_with_audio(raw_audio_file)}")
print(f"raw {sp.longname} -> {sp.execute_with_audio(raw_audio_file)}")
print(f"raw {cq.longname} -> {cq.execute_with_audio(raw_audio_file)}")
print(f"raw {gg.longname} -> {gg.execute_with_audio(raw_audio_file)}")
