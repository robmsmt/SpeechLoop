from speechloop.file_utils import valid_readable_file

import re
import wave
from typing import List

import pandas as pd


def is_en_ascii(input_str: str) -> bool:
    # https://www.asciitable.com/ limit to space + basic symbols - plus upperchars
    # todo could reduce further e.g. remove brackets colons etc
    return all(31 < ord(char.upper()) < 91 for char in input_str)


# todo what about non-english chars - jump to utf8?
def valid_text(text: str, verbose=True) -> bool:
    if len(text) > 0 and is_en_ascii(text):
        return True
    else:
        if verbose:
            print(f"Problem with the text:'{text}' is not valid ASCII")
        return False


def passes_regex(text: str) -> bool:
    # this is a duplicate of is_en_ascii? why check twice
    if re.fullmatch("[a-z '.0-9]+", text.lower()):
        # if re.fullmatch("(\w| )+", text.lower()):
        """
        regex containing a capture group
        \w match any word character in any script
        ' ' matches the space character
        """
        return True
    else:
        print(f"Problem with the text:'{text}' does not match the Regex")
        return False


def validate_manditory_data(df: pd.DataFrame, wanted_asr: List[str], sr: int, column_audiofile: str = 'filename'):
    print(f"Validating dataset CSV contains: {df.shape[0]} rows of files")

    # 0. check that at least 1 ASR is in wanted_asr
    assert len(wanted_asr) >= 1
    # 1. check that required columns exist: filename
    assert column_audiofile in df.columns
    # 2. check that >=1 row of data
    assert df.shape[0] >= 1
    # 3. check that all files are valid readable files that exist
    assert all(df[column_audiofile].apply(valid_readable_file).tolist())
    # 4. pass through data and check that SampleRate is all same value as set in args
    if sr != -1:
        assert all(df[column_audiofile].apply(lambda f: validate_audio(f, sr)).tolist())

    print("All manditory validation tests passed. Data looks ok.")


def validate_optional_csv_data(df: pd.DataFrame, enable_wer: bool, column_transcript: str,
                               enable_text_normalization: bool):
    '''
    Here we can check that all config options are compatible
    '''

    if enable_wer:
        # dw1. check that required columns exist transcript
        assert column_transcript in df.columns
        # dw2. check that len of all transcripts > 0 and is ascii
        assert all(df[column_transcript].apply(valid_text).tolist())
        # dw3. check that transcripts contain only allowed regex]
        assert all(df[column_transcript].apply(passes_regex).tolist())

    if enable_text_normalization:
        # should check that if text normalization is enabled the we must have transcript field
        assert column_transcript in df.columns

    print("Any optional validation tests passed. Data looks ok.")


def validate_audio(filename: str, sr: int, verbose=True) -> bool:
    with wave.open(filename, "rb") as wf:
        found_sr = wf.getframerate()
        channels = wf.getnchannels()

    # can only handle mono currently
    if found_sr == sr and channels == 1:
        return True
    else:
        if verbose:
            print(f"The following file does not have correct SR:{sr} or channel count: {channels} -> {filename}")
        return False
