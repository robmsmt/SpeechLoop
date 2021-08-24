from simplepythonwer import wer
import pandas as pd
from typing import List


def add_wer(df_trans: pd.DataFrame, list_of_asr: List[str]) -> pd.DataFrame:
    # apply transcript to each member of list_of_asr
    for w in list_of_asr:
        wer_name = w + "_wer"
        df_trans[wer_name] = df_trans.apply(lambda x: wer_df(x, w), axis=1)
    return df_trans


def wer_df(row, asr):
    asr_result = str(row[asr]).lower()
    ground_truth = str(row["transcript"]).lower()

    # return an error
    if "<ERROR>".lower() in asr_result or asr_result == "":
        return 1.0

    # remove brackets (kaldi)
    # asr_result = re.sub("[\<\[].*?[\>\]]", "", asr_result)

    # remove any numbers from ASR resultv #todo ordinals + times + dates
    new_asr_string = " ".join([p.number_to_words(word) if word.isdigit() else word for word in asr_result.split()])
    new_gt_string = " ".join([p.number_to_words(word) if word.isdigit() else word for word in ground_truth.split()])

    # todo consider hyphens and spaces

    return min(wer(new_gt_string.strip(), new_asr_string.strip()), 1.0)
