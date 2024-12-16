import tempfile
import os

from gtts import gTTS
from playsound import playsound
import speech_recognition as sr

class AudioUtilsError(Exception):
    """Base exception for AudioUtils errors."""
    pass


class SpeechToTextError(AudioUtilsError):
    """Exception raised for Speech-to-Text errors."""
    pass


class TextToSpeechError(AudioUtilsError):
    """Exception raised for Text-to-Speech errors."""
    pass


def google_text_to_speech(text: str, filepath: str, lang: str = "en"):
    """
    Converts text to speech and saves it as an audio file.

    Args:
        text (str): Text to be converted to speech.
        filepath (str): Path where the audio file will be saved.
        lang (str): Language code for the TTS (default: "en").
    """
    tts = gTTS(text=text, lang=lang)
    tts.save(filepath)


def play_audio(filepath: str):
    """
    Plays an audio file.

    Args:
        filepath (str): Path to the audio file to be played.
    """
    playsound(filepath)


def load_audio(recognizer: sr.Recognizer, audio_path: str = None):
    """
    Loads audio data from a file or microphone.

    Args:
        audio_path (str): Path to the audio file. If None, loads audio from the microphone.

    Returns:
        speech_recognition.AudioData: The loaded audio data.
    """
    if audio_path:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
    else:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
    return audio


class AudioUtils:
    """
    A utility class for handling audio-related tasks such as
    speech-to-text (STT) and text-to-speech (TTS).
    """
    def __init__(self, recognizer=None, lang="en"):
        """
        Initialize the AudioUtils.

        Args:
            recognizer: An external speech recognizer instance for dependency injection (default: None).
            lang (str): Language code for TTS and STT (default: "en").
        """
        self.lang = lang
        self.recognizer = recognizer  # External recognizer injected for testing

    def transcribe_audio(self, audio_path: str = None) -> str:
        """
        Transcribes audio to text using a provided load function.

        Args:
            load_audio_fn (callable): Function to load audio, returning an audio object.

        Returns:
            str: Transcribed text.

        Raises:
            SpeechToTextError: If transcription fails.
        """
        try:
            audio = load_audio(self.recognizer, audio_path)  # Function handles loading audio
            if not self.recognizer:
                raise SpeechToTextError("No recognizer provided for speech transcription.")
            return self.recognizer.recognize_google(audio)
        except Exception as e:
            raise SpeechToTextError(f"Error during transcription: {e}")

    def text_to_speech(self, text: str):
        """
        Converts text to speech and plays the audio using provided save and play functions.

        Args:
            text (str): Text to convert to speech.
            save_fn (callable): Function to save TTS output to a file.
            play_fn (callable): Function to play the audio file.

        Raises:
            TextToSpeechError: If text-to-speech conversion fails.
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                google_text_to_speech(text, tmp_file.name)
                play_audio(tmp_file.name)
            os.unlink(tmp_file.name)
        except Exception as e:
            raise TextToSpeechError(f"Text-to-Speech conversion failed: {e}")
