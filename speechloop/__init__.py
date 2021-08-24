# -*- coding: utf-8 -*-
"""Init SpeechLoop"""


__version__ = "0.0.1"
__author__ = "robmsmt <robmsmt@gmail.com>"
__license__ = "Apache2"

import argparse, sys

from speechloop.run_arguments import run_arguments
from speechloop.file_utils import valid_readable_file, dir_path, wavs_paths
from speechloop.wizard import wizard_main
from speechloop.shared_args import _add_all_arguments


def interactive_cli():
    """
    Main entry point for SpeechLoop CLI.

    This is really just a helper function for using the pip installed version of speechloop
    The argparseing done in speechloop.arguments.run_arguments and core.py is where things are really done

    The purpose of this program is to guide the user through a quickstart wizard.
    """

    # todo in the future even the CLI should be able to take args - i started this but wasn't pleased with the structure
    # parser = argparse.ArgumentParser(description="SpeechLoop -> Interactive quickstart wizard CLI")
    # group = parser.add_argument_group("optional cli switch", "various (mutually exclusive) ways to start CLI")
    # mxg = group.add_mutually_exclusive_group()
    # # option 1
    # mxg.add_argument("--test", action="store_true", help="run included test set")
    # # option 2
    # mxg.add_argument("--live", action="store_true", help="run live mic")
    # # option 3
    # mxg.add_argument("--dataset-download", action="store_true", help="jump to dataset download")
    # # option 4
    # mxg.add_argument("--audio_dir", type=dir_path, help="single path to a directory containing audio files - we'll find them recursively!")
    # mxg.add_argument("--wav_files", type=wavs_paths, help="comma separated list of wav files")
    # parser = _add_all_arguments(parser)
    # wizard_args = parser.parse_args()
    # x = sys.argv[1:]

    print("\nWelcome to the SpeechLoop CLI Wizard 🧙 \n\n")
    wizard_args = sys.argv[1:] + wizard_main()  # pass through any normal args
    run_arguments(wizard_args)
    print("CLI done")


if __name__ == "__main__":
    # used for debugging only
    interactive_cli()
