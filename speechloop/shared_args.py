from distutils.util import strtobool

"""These arguments are shared between the wizard cli that is invoked with just speechloop and the core program"""


def _add_all_arguments(parser):
    parser.add_argument(
        "--input_csv", help='the input CSVs comma delimited used to drive the ASR pipeline, require same headings ("filename","transcript") if multiple', required=True
    )
    parser.add_argument("--sample_rate", type=int, default=16000, help="sample rate used for audio - will assert fail if all audio are not of this type -1 disable")
    parser.add_argument("--quick_test", type=strtobool, default=False, help="quick test runs with only 5 random audios from the data")
    parser.add_argument("--wanted_asr", type=str, default="all", help="Comma delimited 2 letter acronym; gg=google vs=vosk -- see readme for full list")
    parser.add_argument("--home_dir", type=str, default=".", help="home directory for data/tempfiles and output results - maybe diff depending on pip install vs git clone")
    parser.add_argument(
        "--wav_delay",
        type=float,
        default=0.0,
        help="wav delay is the number of seconds to wait between each file. If this is too small it may overload the server(s) and corrupt results",
    )
    parser.add_argument(
        "--shell_script_mode",
        type=strtobool,
        default=False,
        help="if true (False default) is better for use with shellscripts. Turns off TQDM progress bar which is bad for log files",
    )
    parser.add_argument(
        "--disable_wer",
        type=strtobool,
        default=False,
        help="if true (False default) will disable all WER calculation and checks",
    )
    return parser
