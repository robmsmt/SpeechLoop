# SpeechLoop
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
![GitHub](https://img.shields.io/github/license/robmsmt/SpeechLoop)
[![Documentation Status](https://readthedocs.org/projects/speechloop/badge/?version=latest)](https://speechloop.readthedocs.io/en/latest/?badge=latest)
___
 >One can judge from experiment, or one can blindly accept authority.

 *Robert A. Heinlein*

A "keep it simple" collection of many speech recognition engines focusing on inference only. We take the best and most well-known models, pick sensible defaults (if they don't already exist) and make them really easy to evaluate & use.


## Overview

We've standardized some common ASR engines to make analysis of which speech recognition engine is the best for a given speech dataset. Selecting and discovering what ASR works well for a given scenario can be complicated since it depends on many factors.
The standardization this repo provides should make it easier for researchers who want to compare their SoTA models to production systems, both cloud and local, or for people curious and are just getting started looking at speech recognition.

### Features
 - Simple API to run an ASR, with CLI for quick testing with live mic or your chosen WAVs
 - Supports a growing number of local and cloud ASRs
 - Simple modular python interface using Pandas dataframes - easy to extend and change.
 - Evaluation is driven by a line in the dataframe - want to evaluate more speech wavs? Add more lines.
 - Automatic WER calculation with punctuation removal, word corrections (e.g. 1 -> one)
 - Simple CSV output

## Example
<img class="img-fluid" src="https://robmsmt.github.io/public/images/cli_fast.gif" alt="cli" width="700">

## Quicklyiest Quick start
```bash

# make a virtualenv
python3 -m venv ~/venv/speechloop

# activate virtualenv
source ~/venv/speechloop/bin/activate

pip install speechloop
# cd to a directory with WAVs or use the examples!

speechloop
```

Want to use a specific ASR in your own script? No problem
```python
from speechloop.asr import Vosk

raw_audio_file = open("path/to/your/mono_16k.wav", "rb").read()

vs = Vosk()
print(f"{vs.longname} -> {vs.execute_with_audio(raw_audio_file)}")
```

### ASRs

| Short Code |    Model      |   Licence   |       Type       |
|------------|---------------|-------------|------------------|
| ✅ sp       | CMU Sphinx    | Open Source | Offline - docker |
| ✅ vs       | Alphacep Vosk | Open Source | Offline - docker |
| ✅ cq       | Coqui         | Open Source | Offline - docker |
| ✅ gg       | Google        | Proprietary | API              |
| ❌ tbc      | Microsoft     | Proprietary | API              |
| ✅ aw       | Amazon        | Proprietary | API              |

** In general, if there's a simple python API (that requires no extra compilation steps or heavy libs) then it'll be included as-is otherwise we build a docker container


## Structure
The structure loosely follows the ![cookiecutter-data-science](http://drivendata.github.io/cookiecutter-data-science/) project:
```
├── docs
├── LICENSE
├── notebooks
│         └── eda.ipynb
├── README.md
├── requirements.txt
├── tests
└── speechloop
    ├── data
    │   ├── simple_test
    │   └── ...
    ├── output
    ├── asr.py
    ├── speechloop.py
    ├── audio.py
    ├── text.py
    └── validate.py
```

## Requirements
- Python3.6+
- x86_64
- Recommend having approximately X GB storage space for each model

## Developer - 2 Step Install

For developers - installation should be straight-forward and only take a number of minutes on most systems.

### Step 1 - Dev Install SpeechLoop
```bash
git clone https://github.com/robmsmt/SpeechLoop && cd SpeechLoop
python3 -m venv venv/py3
source venv/py3/bin/activate
pip install -r requirements-dev.txt
```

### Step 2 - Install Docker
Skip this step if it's already installed.
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```
Note it's important here that docker can run without root access. After this step has completed, you should check that you can type:
`docker images` and the list should be empty. If it requires that you type: `sudo docker images` then you should follow this [step](https://docs.docker.com/engine/install/linux-postinstall/)
Another good test is running: `docker run hello-world`

## RUNNING AS A DEVELOPER
```bash
cd speechloop
python main.py --input_csv='data/simple_test/simple_test.csv' --wanted_asr=vs,sp,cq
```

## TESTS
Run all tests with: `python3 -m unittest discover .`
