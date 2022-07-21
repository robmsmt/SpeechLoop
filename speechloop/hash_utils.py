import hashlib
import pandas as pd


def hash_audio(row, column_audiofile):
    return hashlib.md5(open(row[column_audiofile], "rb").read()).hexdigest()


def hash_file(f):
    return hashlib.md5(open(f, "rb").read()).hexdigest()


def hash_transcript(row, column_transcript):
    trans = str(row[column_transcript]).encode("utf-8")
    # print(trans)
    return hashlib.md5(trans).hexdigest()


def compute_hashes(df: pd.DataFrame, column_audiofile: str, column_transcript: str) -> pd.DataFrame:
    df[f"{column_audiofile}_hash"] = df.apply(lambda r: hash_audio(r, column_audiofile), axis=1)
    df[f"{column_transcript}_hash"] = df.apply(lambda x: hash_transcript(x, column_transcript), axis=1)
    return df
