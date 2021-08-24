import argparse, sys
from speechloop.core import benchmark
from speechloop.shared_args import _add_all_arguments


def run_arguments(args=None):

    parser = argparse.ArgumentParser(description="SpeechLoop -> Benchmark ASR systems")
    parser = _add_all_arguments(parser)
    if args:
        parsed_args = parser.parse_args(args)
    else:
        parsed_args = parser.parse_args()

    print(f"Starting with following arguments: {str(parsed_args)} \nLoading dataset...")

    benchmark(
        parsed_args.wanted_asr.split(","),
        parsed_args.input_csv,
        parsed_args.sample_rate,
        parsed_args.shell_script_mode,
        parsed_args.wav_delay,
        parsed_args.quick_test,
        parsed_args.home_dir,
        parsed_args.disable_wer,
    )
