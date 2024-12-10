import whisper
import speech_recognition as sr

class SpeechToText:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)
        self.recognizer = sr.Recognizer()

    def transcribe_audio(self, audio_file=None, use_fallback=True):
        """
        Transcribes audio to text using Whisper or SpeechRecognition.

        Args:
            audio_file (str): Path to the audio file (optional).
            use_fallback (bool): Whether to use SpeechRecognition as a fallback.

        Returns:
            str: Transcribed text.
        """
        try:
            if audio_file:
                result = self.model.transcribe(audio_file)
                return result["text"]
            else:
                with sr.Microphone() as source:
                    print("Listening...")
                    audio_data = self.recognizer.listen(source)
                    return self.model.transcribe(audio_data.get_wav_data())["text"]
        except Exception as e:
            if use_fallback:
                print(f"Whisper failed, falling back: {e}")
                return self._fallback_stt(audio_file)
            raise e

    def _fallback_stt(self, audio_file=None):
        if audio_file:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
        else:
            with sr.Microphone() as source:
                print("Listening (fallback)...")
                audio_data = self.recognizer.listen(source)
        return self.recognizer.recognize_google(audio_data)
