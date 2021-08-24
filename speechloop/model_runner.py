import datetime, time
import pandas as pd
from speechloop.file_utils import flush_buffers, valid_readable_file

MAX_RETRIES = 3


def add_transcriptions(df: pd.DataFrame, list_of_asr: list, shell_script_mode: bool, wav_delay: float) -> pd.DataFrame:
    """
    Responsible for driving the wav_run_manager and adding transcriptions

    :param:
    df: Input dataframe that needs following headers: text, wav_filename
    list_of_asr: list of ASR to test the file against

    :returns: out_df that is returned which contains extra columns for each ASR transcript
    """
    if shell_script_mode:
        # when in shell script mode we don't want the weird progress bar to ruin the logs
        trans_df = df.apply(lambda row: wav_run_manager(row, list_of_asr, wav_delay), axis=1)
    else:
        trans_df = df.progress_apply(lambda row: wav_run_manager(row, list_of_asr, wav_delay), axis=1)
    renamecol = {k: v.name for k, v in enumerate(list_of_asr)}
    trans_df.rename(columns=renamecol, inplace=True)
    out_df = pd.concat([df, trans_df], axis=1, sort=False)

    return out_df


def wav_run_manager(row: dict, list_of_asr: list, wav_delay: float) -> pd.Series:
    """

    Function responsible for checking that file is valid and readable, then send it to every one of the ASRs

    :param row: row is a path to a wav file
    :param list_of_asr: list of ASR to test the file against
    :return: Pandas Series that contains ASR results from row WAV that is the size of the number of ASRs
    """
    flush_buffers()

    wav_file = row["filename"]
    result = []

    # loop through every ASR
    if valid_readable_file(wav_file):
        audio_bytes = open(wav_file, "rb").read()
        for asr in list_of_asr:
            asr_start = datetime.datetime.now()

            text = asr.execute_with_audio(audio_bytes)
            attempts = 1

            # checks that if an error is received the run is repeated until MAX_RETRIES is reached
            while text == asr.return_error() and attempts < MAX_RETRIES:
                time.sleep(1)
                print(f"{text} ---> attempt:{attempts}")
                text = asr.execute_with_audio(audio_bytes)
                attempts += 1

            result.append(text)
            asr.add_time(datetime.datetime.now() - asr_start)
            time.sleep(wav_delay)

        return pd.Series(result)
    else:
        return pd.Series(["<Missing file error>"] * len(list_of_asr))
