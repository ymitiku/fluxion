import unittest
from unittest.mock import Mock, patch
from fluxion.utils.audio_utils import AudioUtils, SpeechToTextError, TextToSpeechError


class TestAudioUtils(unittest.TestCase):
    def setUp(self):
        # Mock the recognizer
        self.mock_recognizer = Mock()
        self.audio_utils = AudioUtils(recognizer=self.mock_recognizer, lang="en")

    @patch("fluxion.utils.audio_utils.play_audio")
    @patch("fluxion.utils.audio_utils.google_text_to_speech")
    @patch("tempfile.NamedTemporaryFile")
    @patch("os.unlink")
    def test_text_to_speech_success(self, mock_unlink, mock_tempfile, mock_save_audio, mock_play_audio):
        #

        # Mock tempfile behavior
        mock_tempfile.return_value.__enter__.return_value.name = "mock_tempfile.mp3"

        # Call text_to_speech
        self.audio_utils.text_to_speech(
            text="Test TTS"
        )

        # Assertions
        mock_save_audio.assert_called_once_with("Test TTS", "mock_tempfile.mp3")
        mock_play_audio.assert_called_once_with("mock_tempfile.mp3")
        mock_unlink.assert_called_once_with("mock_tempfile.mp3")


    @patch("fluxion.utils.audio_utils.load_audio")
    @patch("fluxion.utils.audio_utils.play_audio")
    @patch("fluxion.utils.audio_utils.google_text_to_speech")
    @patch("tempfile.NamedTemporaryFile")
    def test_text_to_speech_failure(self, mock_tempfile, mock_save_audio, mock_play_audio, mock_load_audio):
        mock_load_audio.side_effect = Exception("Mock TTS error")
       
        with self.assertRaises(TextToSpeechError) as cm:
            self.audio_utils.text_to_speech(
                text="Test TTS"
            )
        self.assertIn("Text-to-Speech conversion failed", str(cm.exception))


    @patch("fluxion.utils.audio_utils.load_audio")
    def test_transcribe_audio_success(self, mock_load_audio):
        # Mock audio data
        mock_audio = Mock()
        mock_load_audio.return_value = mock_audio
        self.mock_recognizer.recognize_google.return_value = "Test transcription"

        # Call transcribe_audio
        result = self.audio_utils.transcribe_audio()

        # Assertions
        self.mock_recognizer.recognize_google.assert_called_once_with(mock_audio)
        self.assertEqual(result, "Test transcription")

    def test_transcribe_audio_failure(self):
        # Mock audio data
        mock_audio = Mock()
        mock_load_audio_fn = Mock(return_value=mock_audio)
        self.mock_recognizer.recognize_google.side_effect = Exception("Mock STT error")

        with self.assertRaises(SpeechToTextError) as cm:
            self.audio_utils.transcribe_audio(mock_load_audio_fn)
        self.assertIn("Error during transcription", str(cm.exception))

    def test_transcribe_audio_invalid_loader(self):
        # Pass a loader that raises an exception
        mock_load_audio_fn = Mock(side_effect=Exception("Loader failed"))

        with self.assertRaises(SpeechToTextError) as cm:
            self.audio_utils.transcribe_audio(mock_load_audio_fn)
        self.assertIn("Error during transcription", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
