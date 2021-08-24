import hashlib
import pandas as pd


def hash_audio(row):
    return hashlib.md5(open(row["filename"], "rb").read()).hexdigest()


def hash_file(f):
    return hashlib.md5(open(f, "rb").read()).hexdigest()


def hash_transcript(row):
    trans = str(row["transcript"]).encode("utf-8")
    # print(trans)
    return hashlib.md5(trans).hexdigest()


def compute_hashes(df: pd.DataFrame, disable_wer: bool = False) -> pd.DataFrame:
    df["audio_hash"] = df.apply(lambda x: hash_audio(x), axis=1)
    if not disable_wer:
        df["transcript_hash"] = df.apply(lambda x: hash_transcript(x), axis=1)
    return df
