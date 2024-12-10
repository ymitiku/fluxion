import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, text):
        """
        Converts text to speech.

        Args:
            text (str): Text to convert.
        """
        self.engine.say(text)
        self.engine.runAndWait()
