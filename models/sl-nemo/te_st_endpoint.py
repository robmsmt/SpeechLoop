#!/usr/bin/env python3

import json
import base64
import requests
import pprint as pp


def main(endpoint, wav_location):

    b64audio = base64.b64encode(open(wav_location, "rb").read()).decode("utf-8")
    print(f"Length of b64 data is:{len(b64audio)}")

    json_message = {"b64_wav": b64audio, "sr": 16000}

    r = requests.post(endpoint, json=json_message)
    print(f"Status code: {r.status_code}")
    try:
        response = r.json()
        pp.pprint(response, indent=2)
    except:
        print("err")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="This file reads in a wav file and prints a CURL best to be piped to a file")
    parser.add_argument("--endpoint", default="/transcribe", type=str)
    parser.add_argument("--host", default="http://localhost:3500", type=str)
    parser.add_argument("--wav", default="../../speechloop/data/simple_test/wavs/109938_zebra_ch0_16k.wav", type=str)
    args = parser.parse_args()
    url = args.host + args.endpoint
    main(url, args.wav)
