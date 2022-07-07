# !/usr/bin/env python

from __future__ import absolute_import
import datetime, sys
import os
from typing import List

if sys.version_info < (3, 6):
    print("SpeechLoop requires at least Python 3.6 to run.")
    sys.exit(1)

from speechloop.validate import validate_manditory_data, validate_optional_csv_data
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
    enable_wer: bool = False,
    enable_text_normalization: bool = False,
    enable_compute_hashes: bool = False,
    column_audiofile:str = 'filename',
    column_transcript:str = 'transcript',

) -> None:
    """

    :param wanted_asr: -- List of 2char strings representing each ASR
    :param input_csvs_str:
    :param sample_rate: -- integer corresponding to wav sample rate
    :param shell_script_mode: -- bool determines how to print output
    :param wav_delay: -- float delay
    :param quick_test -- perform test on small 5 subset sample
    :param home_dir: -- location for output
    :param enable_wer: bool = False,
    :param enable_text_normalization: bool = False,
    :param enable_compute_hashes: bool = False,
    :param column_audiofile:str = 'filename',
    :param column_transcript:str = 'transcript',
    :return: None
    """
    start_time = datetime.datetime.now().replace(microsecond=0)

    # IMPORT CSV(s)
    df = import_csvs(input_csvs_str, enable_wer, column_audiofile, column_transcript)

    if quick_test:
        df = df.sample(5, random_state=42)
        print(f"Using small quick test dataset: \n{df.head()}\n\n")

    # VALIDATE
    validate_manditory_data(df, sample_rate, column_audiofile)
    validate_optional_csv_data(df, enable_wer, column_transcript)

    if enable_compute_hashes:
        df = compute_hashes(df, enable_wer)

    list_of_asr = create_model_objects(wanted_asr)
    list_of_asr_names = [asr.name for asr in list_of_asr]

    if enable_text_normalization:
        wer_cols = [asr + "_cor" for asr in list_of_asr_names]

    # RUN & GET TRANSCRIPTIONS
    # todo tqdm has this functionality built in - check it
    if not shell_script_mode:
        tqdm.pandas()
    df_trans = add_transcriptions(df, list_of_asr, shell_script_mode, wav_delay)

    # COMMON CORRECTIONS
    # todo double check this logic
    wanted_asr_inc_trans = list_of_asr_names + [column_transcript] if enable_wer else list_of_asr_names

    if enable_text_normalization:
        cc = CommonCorrections(df_correction_suffix="_corrected")
        df_trans = cc.correct_df(df_trans, column_list=wanted_asr_inc_trans)

    if enable_wer:
        # ADD WER
        df_wer = add_wer(df_trans, wer_cols)
        # SUMMARY
        print_summary(list_of_asr, df_wer, start_time)
        # OUTPUT CSV
        save_output(home_dir, quick_test, list_of_asr_names, df_wer)

    else:
        # OUTPUT CSV
        save_output(home_dir, quick_test, list_of_asr_names, df_trans)
