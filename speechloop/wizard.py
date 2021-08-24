import os
import sysconfig
import datetime
from pathlib import Path

import pandas as pd
import questionary
from questionary import Separator
from speechloop.live import live_main
from speechloop.file_utils import valid_readable_file, directory_writeable

HOME = str(Path.home())

"""
This wizard/cli code is my first attempt at writing a CLI/Wizard with Questions. I wasn't sure about a lot of design decisions; it's quite likely
that this will change a lot over the coming versions and that a lot could be improved/refactored.
"""


class HomeDirectoryError(Exception):
    pass


def write_path_to_point(path, home_pointer_file):
    with open(home_pointer_file, "w") as f:
        p = os.path.abspath(os.path.expanduser(path))
        print(f"Saving: {p} in file: {home_pointer_file}")
        f.write(p)


def attempt_read_pointer(home_pointer_file):
    try:
        with open(home_pointer_file, "r") as f:
            home_location = f.read().replace("\n.", "")

        if os.path.isdir(home_location) and directory_writeable(home_location):
            print(f"Found and using: {home_location}")
            return home_location
        else:
            raise HomeDirectoryError
    except (FileNotFoundError, HomeDirectoryError) as e:
        print(f"Error: {e}, we will attempt setup")


def select_home_directory(default_local, home_pointer_file):
    # Q0 - HOME PATH SETUP
    if questionary.confirm(
        f"Do you want to use {HOME}/SpeechLoop for the results output and any temp and data files? "
        f"This is recommended for pip installed use. "
        f"(for git clone use, it might be preferable to change to the current working directory: {os.getcwd()})"
    ).ask():
        os.makedirs(default_local, exist_ok=True)
        assert os.path.isdir(default_local)
        write_path_to_point(default_local, home_pointer_file)
        return default_local
    else:
        while True:
            q0_path = questionary.path(
                "Enter your preferred path for SpeechLoop. Any folders that do not exist we will create them. "
                "We append a folder called SpeechLoop: ", only_directories=True
            ).ask()
            new_path = os.path.join(os.path.abspath(os.path.expanduser(q0_path)), "SpeechLoop")
            if questionary.confirm(new_path).ask():
                os.makedirs(new_path, exist_ok=True)
                assert os.path.isdir(new_path)
                write_path_to_point(new_path, home_pointer_file)
                return new_path


def wizard_main():
    arg_list = []

    """
    The reason for this next part of path mapping is that users can install with pip or run source from github in any random location,
    we create a SpeechLoop home directory which is used for storing data and results. The pointer to home `lib/python-x/site-packages/speechloop/.home_pointer`

    When installing and running source from git (if you follow instructions) it means you have used `pip install -e .` that creates a .egg-link where the package
    would be in site-packages

    """

    default_local = os.path.join(HOME, "SpeechLoop")
    package_dir = sysconfig.get_paths()["purelib"]
    print(f"Pip package directory: {package_dir}")
    speechloop_path = os.path.join(package_dir, "speechloop")
    print(f"SpeechLoop path: {speechloop_path}")
    home_pointer_file = os.path.join(speechloop_path, ".home_pointer")
    egglink = speechloop_path + ".egg-link"

    if valid_readable_file(egglink, quiet=True):
        home_location = attempt_read_pointer(egglink)
    elif valid_readable_file(home_pointer_file, quiet=True):
        # second let's look inside .home_pointer for SpeechLoop home path
        print(f"SpeechLoop Home detected: {home_pointer_file}... Attempting to read the file")
        home_location = attempt_read_pointer(home_pointer_file)
        if not home_location:
            home_location = select_home_directory(default_local, home_pointer_file)
    else:
        home_location = select_home_directory(default_local, home_pointer_file)
    arg_list.append(f"--home_dir={home_location}")

    # Q1 - MODE
    q1 = questionary.select(
        "How do you want to proceed with SpeechLoop?",
        choices=[
            "1. Run with the provided ~70 small test audios (with WER)",
            "2. Use live with the microphone (without WER)",
            "3. Use some data I already have by finding recursively in this current directory (without WER)",
            "4. Use some data I already have based on CSV pointing to each file (with WER)",
            # "5. Download some opensource datasets", # todo tbc
        ],
    ).ask()[0]

    # Q2 - ASR SELECTION
    q2 = questionary.checkbox(
        "Select ASRs:",
        choices=[
            Separator("---Local Docker ASRs---"),
            "vs - Alphacep Vosk",
            "sp - CMU Sphinx",
            "cq - Coqui stt",
            Separator("---Cloud ASRs---"),
            "gg - Google Cloud - (requires api key)",  # todo maybe ask for this or grey it out if not provided?
        ],
    ).ask()

    asr_codes = [asr[:2] for asr in q2]
    arg_list.append(f"--wanted_asr={','.join(asr_codes)}")

    if q1 == "1":
        print("Running test WAVs")
        """todo this is hacky temporary method to chdir - couple of open questions
        q1 )it would be better to download separately the test wavs.
        q2) will paths work in windows?"""
        if os.path.isdir(speechloop_path):
            os.chdir(speechloop_path)
            test_csv = os.path.join(package_dir, "speechloop/data/simple_test/simple_test.csv")
        else:  # handle case where user has installed with pip install -e .
            os.chdir("./speechloop")  # git clone
            test_csv = "data/simple_test/simple_test.csv"

        arg_list.append(f"--input_csv={test_csv}")
    elif q1 == "2":
        live_main(wanted_asr=asr_codes)
    elif q1 == "3":
        print("\n We will begin by recursively looking at the current working directory")
        all_valid_files = search_directory_for_audiofiles()
        print(f"We have found: {len(all_valid_files)} wav files")
        print(
            f"It's important to note that WER calculation is not possible without the ground truth, without it "
            f"it still can be valuable to look at the transcripts generated and to see how they vary"
        )

        a3 = questionary.confirm(
            f"Do you want to continue and use the {len(all_valid_files)} audios that were found in the current directory (without WER calc)?",
        ).ask()

        if a3:
            path_to_csv = build_csv_from_found_wavs(all_valid_files, home_location)
            arg_list.append(f"--input_csv={path_to_csv}")
            arg_list.append(f"--disable_wer=True")
        else:
            print("Rerun the command in a different directory")
            exit(2)

    elif q1 == "4":
        a4 = questionary.path("Select the path to the CSV: \n Note - it should contain columns 'filename' and 'transcript' and row for each file. ", validate=valid_csv_file).ask()
        full_path_to_csv = os.path.abspath(os.path.expanduser(a4))
        print(f"Selected: {full_path_to_csv}")
        arg_list.append(f"--input_csv={full_path_to_csv}")

    return arg_list


def valid_csv_file(s):
    if s.endswith(".csv"):
        # and valid_readable_file(s, quiet=True):
        return True
    else:
        return False


def build_csv_from_found_wavs(
    all_valid_files,
    home_location,
    cwd=".",
):
    df = pd.DataFrame({"filename": all_valid_files})
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    output_path_name = f"{date_str}_autogenerated_from_{len(all_valid_files)}_wavs.csv"

    q1 = questionary.select(
        "Where would you like to store the CSV we have generated?",
        choices=["1. In current working directory with the data?", f"2. With Output in SpeechLoop home directory: {home_location} ?"],
    ).ask()[0]

    if q1 == "1":
        file_path = os.path.join(cwd, output_path_name)
    elif q1 == "2":
        file_path = os.path.join(home_location, output_path_name)

    df.to_csv(file_path, index=None)
    return file_path
