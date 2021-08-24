from io import BytesIO
import os, sys, datetime, csv, tempfile, argparse

import pandas as pd


def disk_in_memory(wav_bytes: bytes) -> BytesIO:
    """
    this spooled wav was chosen because it's much more efficient than writing to disk,
    it effectively is writing to memory only and can still be read (by some python modules) as a file
    """
    with tempfile.SpooledTemporaryFile() as spooled_wav:
        spooled_wav.write(wav_bytes)
        spooled_wav.seek(0)
        return BytesIO(spooled_wav.read())


def import_csvs(filepaths: str, disable_wer: bool = False) -> pd.DataFrame:

    if disable_wer:
        cols = ["filename"]
    else:
        cols = ["filename", "transcript"]

    df = pd.DataFrame(columns=cols)
    for csv in filepaths.split(","):
        df_new = pd.read_csv(csv, index_col=None)
        df_new = df_new[cols]
        df = pd.concat([df, df_new], sort=False)
    return df


def directory_writeable(path: str) -> bool:
    return os.access(path, os.W_OK | os.X_OK)


def valid_readable_file(filename: str, quiet=False) -> bool:
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return True
    else:
        if not quiet:
            print(f"The following file has issues loading: {filename}")
        return False


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def wavs_paths(list_path_to_wav):
    if all([valid_readable_file(wav) for wav in list_path_to_wav]) and all([x.endswith(".wav") for x in list_path_to_wav]):
        return list_path_to_wav
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{list_path_to_wav} is not a valid path")


def search_directory_for_audiofiles(d=".", file_type=".wav"):
    all_files = [os.path.join(path, f) for path, directories, files in os.walk(d) for f in files]
    all_valid_files = [os.path.abspath(f) for f in all_files if f.endswith(file_type)]
    return all_valid_files

def flush_buffers() -> None:
    sys.stdout.flush()
    sys.stderr.flush()


def save_output(home_dir, quick_test, wanted_asr, df_wer):
    date_str = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    qt = "QT_" if quick_test else ""
    asr_str = "-".join(wanted_asr)
    save_folder = os.path.join(home_dir, "output")
    os.makedirs(save_folder, exist_ok=True)
    output_path_name = f"{save_folder}/{qt}{date_str}_{asr_str}.csv"
    print(f"Output file: {output_path_name}")
    df_wer.to_csv(output_path_name, index=False, quoting=csv.QUOTE_ALL)
    print(f"Success!")
