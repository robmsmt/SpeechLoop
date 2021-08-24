#!/usr/bin/env python
"""
An example of reading from a microphone (blocking) and running all the results on given ASRs
"""

import argparse
import os
import queue
import sys
import tempfile
import time
from subprocess import call

import sounddevice as sd
import soundfile as sf

from speechloop.asr import create_model_objects

Q = queue.Queue()
RECORDING = None


def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    Q.put(indata.copy())


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def clear_screen():
    _ = call("clear" if os.name == "posix" else "cls")


def simple_transcribe(asr_list, filename, keep_audio=False):
    raw_audio_file = open(filename, "rb").read()
    print(f"Selected ASRs: ")
    for asr in asr_list:
        transcript = asr.execute_with_audio(raw_audio_file)
        print(f"{asr.longname} -> {transcript}")

    input("\nPress any key to continue...")  # todo keep y/n or work out GT&WER would be good

    if not keep_audio:
        os.remove(filename)


def live_main(wanted_asr, device=None, samplerate=16000, channels=1, subtype=None):
    asr_list = create_model_objects(wanted_asr)
    newline = "\n"
    while True:
        global RECORDING
        RECORDING = True
        clear_screen()
        print(f"Selected ASRs: {newline}{f'{newline}'.join([a.longname for a in asr_list])}{newline}")
        ans = input("Press enter to start recording and ctrl+c to stop.")

        if ans == "":
            try:
                # clear_screen()
                if samplerate == 0:
                    device_info = sd.query_devices(device, "input")
                    samplerate = int(device_info["default_samplerate"])

                filename = tempfile.mktemp(prefix="live_audio_", suffix=".wav", dir="")
                # Make sure the file is opened before recording anything:
                with sf.SoundFile(filename, mode="x", samplerate=samplerate, channels=channels, subtype=subtype) as file:
                    with sd.InputStream(samplerate=samplerate, device=device, channels=channels, callback=callback):
                        print("#" * 80)
                        print("RECORDING... press Ctrl+C to stop")
                        print("#" * 80)
                        while RECORDING:
                            file.write(Q.get())

            except KeyboardInterrupt:
                RECORDING = False
                clear_screen()
                print("Stopping recording. \n")
                time.sleep(1)
                simple_transcribe(asr_list, filename)


if __name__ == "__main__":

    # many of these args were taken from: https://python-sounddevice.readthedocs.io/en/latest/examples.html
    parser = argparse.ArgumentParser(description="SpeechLoop -> LIVE")
    parser.add_argument("--wanted_asr", type=str, default="all", help="Comma delimited 2 letter acronym; gg=google vs=vosk -- see readme for full list")
    parser.add_argument("-l", "--list-devices", action="store_true", help="show list of audio devices and exit")
    parser.add_argument("-d", "--device", type=int_or_str, help="input device (numeric ID or substring)")
    parser.add_argument("-sr", "--samplerate", type=int, default=16000, help="sampling rate")
    parser.add_argument("-c", "--channels", type=int, default=1, help="number of input channels")
    parser.add_argument("-t", "--subtype", type=str, help='sound file subtype (e.g. "PCM_24")')
    parsed_args = parser.parse_args()

    if parsed_args.list_devices:
        print(sd.query_devices())
        parser.exit(0)

    live_main(parsed_args.wanted_asr.split(","), parsed_args.device, parsed_args.samplerate, parsed_args.channels, parsed_args.subtype)
