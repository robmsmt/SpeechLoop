# !/usr/bin/env python

from __future__ import absolute_import
import datetime, sys
import os
from typing import List

if sys.version_info < (3, 6):
    print("SpeechLoop requires at least Python 3.6 to run.")
    sys.exit(1)

from speechloop.validate import validate_data
from speechloop.file_utils import import_csvs, save_output
from speechloop.hash_utils import compute_hashes
from speechloop.model_runner import add_transcriptions
from speechloop.asr import create_model_objects
from speechloop.text import add_wer
from speechloop.summary import print_summary

from tqdm import tqdm
from commoncorrections import CommonCorrections


def benchmark(
    wanted_asr: List[str],
    input_csvs_str: str,
    sample_rate: int = 16000,
    shell_script_mode: bool = False,
    wav_delay: float = 0.0,
    quick_test: bool = False,
    home_dir: str = os.getcwd(),
    disable_wer: bool = False,
) -> None:
    """

    :param wanted_asr: -- List of 2char strings representing each ASR
    :param input_csvs_str:
    :param sample_rate: -- integer corresponding to wav sample rate
    :param shell_script_mode: -- bool determines how to print output
    :param wav_delay: -- float delay
    :param quick_test -- perform test on small 5 subset sample
    :param home_dir: -- location for output
    :param disable_wer -- removes wer calc and checks
    :return: None
    """
    start_time = datetime.datetime.now().replace(microsecond=0)

    # IMPORT CSV(s)
    df = import_csvs(input_csvs_str, disable_wer)
    if quick_test:
        df = df.sample(5, random_state=42)
        print(f"Using small quick test dataset: \n{df.head()}\n\n")

    # VALIDATE
    validate_data(df, sample_rate, disable_wer)
    df = compute_hashes(df, disable_wer)
    list_of_asr = create_model_objects(wanted_asr)
    list_of_asr_names = [asr.name for asr in list_of_asr]

    if not disable_wer:
        wer_cols = [asr + "_corrected" for asr in list_of_asr_names]

    # RUN & GET TRANSCRIPTIONS
    if not shell_script_mode:
        tqdm.pandas()
    df_trans = add_transcriptions(df, list_of_asr, shell_script_mode, wav_delay)

    # COMMON CORRECTIONS
    wanted_asr_inc_trans = list_of_asr_names + ["transcript"] if not disable_wer else list_of_asr_names
    cc = CommonCorrections(df_correction_suffix="_corrected")
    df_correct = cc.correct_df(df_trans, column_list=wanted_asr_inc_trans)

    if not disable_wer:
        # ADD WER
        df_wer = add_wer(df_correct, wer_cols)
        # SUMMARY
        print_summary(list_of_asr, df_wer, start_time)
        # OUTPUT CSV
        save_output(home_dir, quick_test, list_of_asr_names, df_wer)

    else:
        # OUTPUT CSV
        save_output(home_dir, quick_test, list_of_asr_names, df_correct)
