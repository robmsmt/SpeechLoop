import time

from speechloop.file_utils import valid_readable_file, disk_in_memory
from speechloop.asr.container_utils import kill_container
from speechloop.asr.errors import DEFAULT_ERROR

import abc
import datetime
import atexit


class ASR(metaclass=abc.ABCMeta):
    """
    Args:
        name: The name of the model
        asrtype: The type of the speech rec
    """

    def __init__(self, name, asrtype, sr=16000):
        self.init_starttime = datetime.datetime.now()
        self.name = name
        self.asrtype = asrtype
        self.init_finishtime = None
        self.total_inf_time = datetime.datetime.now() - datetime.datetime.now()
        self.verbose = True
        self.kill_containers_on_quit = True
        self.sr = sr

        if self.asrtype == "docker-local" and self.kill_containers_on_quit:
            atexit.register(self.kill)

    def finish_init(self):
        self.init_finishtime = datetime.datetime.now()

    def add_time(self, time_to_add):
        self.total_inf_time += time_to_add

    def return_error(self, error_msg=DEFAULT_ERROR):
        return error_msg

    def kill(self):
        kill_container(self.dockerhub_url, verbose=self.verbose)

    @abc.abstractmethod
    def execute_with_audio(self, audio):
        pass

    def read_audio_file(self, path_to_audio):
        if valid_readable_file(path_to_audio):
            audio = open(path_to_audio, "rb").read()
            return self.execute_with_audio(audio)

