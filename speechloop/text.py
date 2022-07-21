from speechloop.asr.errors import DEFAULT_ERROR
from simplepythonwer import wer
import pandas as pd
from typing import List


def add_wer(df_trans: pd.DataFrame, wer_cols: List[str], column_transcript: str) -> pd.DataFrame:
    # apply transcript to each member of list_of_asr
    for w in wer_cols:
        df_trans[w] = df_trans.apply(lambda row: wer_df(row, w, column_transcript), axis=1)
    return df_trans


def wer_df(row, asr, column_transcript):
    """

    Parameters
    ----------
    row: comes from dataframe apply
    asr: can be <shortcode>_cor_wer OR <shortcode>_wer
    column_transcript: name in the csv file for the column of transcripts

    Returns, value between 0 <--> 1.0
    -------

    """
    asr_result = str(row[asr[:-4]]).lower()
    ground_truth = str(row[column_transcript]).lower()

    # return an error
    if DEFAULT_ERROR.lower() in asr_result:
        return 1.0

    return min(wer(asr_result.strip(), ground_truth.strip()), 1.0)
