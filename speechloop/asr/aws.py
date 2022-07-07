from speechloop.asr.base_asr import ASR
from speechloop.file_utils import disk_in_memory

import asyncio

try:
    from amazon_transcribe.client import TranscribeStreamingClient
    from amazon_transcribe.handlers import TranscriptResultStreamHandler
    from amazon_transcribe.model import TranscriptEvent
except ImportError as e:
    print(f"Amazon not imported, for reason:{e}")


class Aws(ASR):
    def __init__(self):

        super().__init__("aw", "cloud-api")
        # credentials will be auto retrieved from ~/.aws/credentials however in future should be overriden by param?

        self.longname = "aws"
        self.shortname = "aw"
        self.handler = None
        self.stream = None
        self.client = None

        if self.verbose:
            print(f"Using {self.longname}")

    def execute_with_audio(self, audio):
        audio_file = disk_in_memory(audio)
        return asyncio.get_event_loop().run_until_complete(self.write_chunks(audio_file))

    async def write_chunks(self, audio_file):

        self.client = TranscribeStreamingClient(region="us-east-1")
        self.stream = await self.client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
        )

        while True:
            data = audio_file.read(1024 * 16)
            if len(data) == 0:
                await self.stream.input_stream.end_stream()
                break
            await self.stream.input_stream.send_audio_event(audio_chunk=data)

        async for event in self.stream.output_stream:
            if isinstance(event, TranscriptEvent):
                result = await self.handle_transcript_event(event)
            else:
                print(event)

        # todo this is not a very good implementation but quick first attempt
        while True:
            # wait until generator has been iterated over
            await asyncio.sleep(0.1)
            if result[-1].is_partial == False:
                break

        # await asyncio.sleep(0.1)
        transcript = result[-1].alternatives[-1].transcript

        if transcript.endswith("."):
            # aws ends always with a period, let's kill it.
            transcript = transcript[:-1]

        return transcript

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        return results


