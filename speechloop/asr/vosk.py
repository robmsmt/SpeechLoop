from speechloop.asr.base_asr import ASR
from speechloop.asr.container_utils import launch_container
from speechloop.file_utils import disk_in_memory

import json
import asyncio

# ext packages
import websockets


class Vosk(ASR):
    """
    Vosk
    """

    def __init__(self):
        super().__init__("vs", "docker-local")
        self.uri = "ws://localhost:2800"
        self.dockerhub_url = "robmsmt/sl-vosk-en-16k:latest"
        self.shortname = self.dockerhub_url.rsplit("/")[-1].rsplit(":")[0]
        self.longname = "vosk"
        self.container_found = False
        launch_container(self.dockerhub_url, {"2700/tcp": 2800}, verbose=self.verbose, delay=5)
        self.finish_init()

    def execute_with_audio(self, audio):
        audio_file = disk_in_memory(audio)
        return asyncio.get_event_loop().run_until_complete(self.send_websocket(audio_file))

    async def send_websocket(self, audio_file):
        async with websockets.connect(self.uri) as websocket:
            all_finals = ""
            all_partials = []
            while True:
                partial = None
                data = audio_file.read(1024 * 16)
                if len(data) == 0:
                    break
                await websocket.send(data)
                try:
                    partial_json = json.loads(await websocket.recv())
                    partial = partial_json["partial"]
                    if partial:
                        all_partials.append(partial)
                except KeyError:
                    all_finals += partial_json["text"] + " "

            await websocket.send('{"eof" : 1}')
            final_result = json.loads(await websocket.recv())["text"]

            if len(all_finals) > 0 and len(final_result) == 0:
                return all_finals
            elif len(all_finals) > 0 and len(final_result) > 0:
                return all_finals + f" {final_result}"
            elif len(final_result) == 0 and len(all_partials) > 0:
                return all_partials[-1]
            else:
                return final_result
