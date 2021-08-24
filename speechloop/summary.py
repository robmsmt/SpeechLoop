import datetime


def print_summary(list_of_asr, df_wer, start_time):
    wer_cols = [c for c in df_wer.columns if "wer" in c]

    for w in wer_cols:
        print("-" * 30)
        print(f"Average value of {w} is {df_wer[w].mean():.4f}\n")

    for asr in list_of_asr:
        print(f"Total inference time taken for {asr.name} is {asr.total_inf_time}")

    print("-" * 30)
    print("-" * 30)
    end_time = datetime.datetime.now().replace(microsecond=0)
    print(f"Finished, with total runtime: {end_time - start_time}")
    print(f"For testing {len(list_of_asr)} ASR types")
    print(f"For a dataset of {df_wer.shape[0]} wav files")
    print(f"With an average of {((end_time - start_time).total_seconds() / df_wer.shape[0] ):.2f} secs per wav file")
