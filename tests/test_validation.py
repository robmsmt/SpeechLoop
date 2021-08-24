import unittest
from speechloop.validate import is_en_ascii, valid_text, validate_audio


class TestNonAscii(unittest.TestCase):

    # -1. non-ascii -
    def test_non_ascii(self):
        self.assertEqual(is_en_ascii("the cat sat"), True)
        self.assertEqual(is_en_ascii("the öäüßÄÖÜ sat"), False)

    def test_valid_text(self):
        self.assertEqual(valid_text("", verbose=False), False)
        self.assertEqual(valid_text("the öäüßÄÖÜ sat", verbose=False), False)

    def test_valid_audio(self):

        self.assertEqual(validate_audio("tests/valid_audio.wav", 16000, verbose=False), True)
        self.assertEqual(validate_audio("tests/valid_audio.wav", 8000, verbose=False), False)
        self.assertEqual(validate_audio("tests/invalid_audio_stereo.wav", 16000, verbose=False), False)
