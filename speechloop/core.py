# !/usr/bin/env python

from __future__ import absolute_import

from speechloop.validate import validate_manditory_data, validate_optional_csv_data
from speechloop.file_utils import import_csvs, save_output
from speechloop.hash_utils import compute_hashes
from speechloop.model_runner import add_transcriptions
from speechloop.asr.registry import create_model_objects
from speechloop.text import add_wer
from speechloop.summary import print_wer_summary

import datetime, time
import sys
import os
from typing import List

if sys.version_info < (3, 6):
    print("SpeechLoop requires at least Python 3.6 to run.")
    sys.exit(1)

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
    enable_wer: bool = True,
    enable_text_normalization: bool = True,
    enable_compute_hashes: bool = False,
    column_audiofile: str = "filename",
    column_transcript: str = "transcript",
    normalization_suffix: str = "_cor",
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
    df = import_csvs(input_csvs_str)

    if quick_test:
        df = df.sample(5, random_state=42)
        print(f"Using small quick test dataset: \n{df.head()}\n\n")

    # VALIDATE
    validate_manditory_data(df, wanted_asr, sample_rate, column_audiofile)
    validate_optional_csv_data(df, enable_wer, column_transcript, enable_text_normalization)

    if enable_compute_hashes:
        df = compute_hashes(df, column_audiofile, column_transcript)

    list_of_asr = create_model_objects(wanted_asr)
    list_of_asr_names = [asr.name for asr in list_of_asr]

    # RUN & GET TRANSCRIPTIONS
    if not shell_script_mode:
        tqdm.pandas()
    df_trans = add_transcriptions(df, list_of_asr, shell_script_mode, wav_delay)

    if enable_text_normalization:
        # USE COMMON CORRECTIONS
        df_trans = text_normalization(df_trans, list_of_asr_names, column_transcript, normalization_suffix)

    if enable_wer:
        # ADD WER
        wer_substring = f"{normalization_suffix}_wer" if enable_text_normalization else "_wer"
        trans_substring = column_transcript + normalization_suffix if enable_text_normalization else column_transcript
        wer_cols = [asr + wer_substring for asr in list_of_asr_names]
        df_wer = add_wer(df_trans, wer_cols, trans_substring)
        # SUMMARY
        print_wer_summary(list_of_asr, df_wer, start_time)
        # OUTPUT CSV WITH WER
        save_output(home_dir, quick_test, list_of_asr_names, df_wer)
    else:
        # OUTPUT CSV - JUST TRANSCRIPTS
        save_output(home_dir, quick_test, list_of_asr_names, df_trans)

    print("Done.")
    time.sleep(2)


def text_normalization(df, list_of_asr_names, column_transcript, normalization_suffix):
    wanted_asr_inc_trans = list_of_asr_names + [column_transcript]
    cc = CommonCorrections(df_correction_suffix=normalization_suffix)
    df_trans = cc.correct_df(df, column_list=wanted_asr_inc_trans)
    return df_trans
