""" 
fluxion_ai.perception.sources.audio_sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Audio sources for perception.

Classes:
    - AudioSource: Abstract base class for audio sources.
    - AudioFileSource: Audio source for audio files.
    - AudioRecordingSource: Audio source for audio recordings.

Examples:
    - AudioFileSource: 
        audio_source = AudioFileSource(audio_path="path/to/audio/file")
        audio_data = audio_source.get_data()
        print(audio_data)
    - AudioRecordingSource:
        audio_source = AudioRecordingSource()
        audio_data = audio_source.get_data()
        print(audio_data)

"""

from abc import abstractmethod
import numpy as np
from fluxion_ai.perception.sources.perception_source import PerceptionSource

class AudioSource(PerceptionSource):
    def __init__(self, **kwargs):
        """
        Initialize the AudioSource with the audio path.

        Args:
            audio_path (str): The path to the audio file
        """
        if "name" not in kwargs:
            kwargs["name"] = "AudioSource"
        super().__init__(**kwargs)
    
    def get_data(self, **kwargs) -> str:
        audio = self.get_audio(**kwargs)
        processed_audio = self.process_audio(audio)
        return {"audio": processed_audio}
    
    @abstractmethod
    def get_audio(self, **kwargs) -> np.ndarray:
        """
        Get the audio data from the source.

        Args:
            **kwargs: Additional keyword arguments for the source.

        Returns:
            np.ndarray: The audio data from the source.
        """
        pass

    @abstractmethod
    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Process the audio data.

        Args:
            audio (np.ndarray): The audio data as a numpy array

        Returns:
            np.ndarray: The processed audio data as a numpy array
        """
        pass

class AudioFileSource(AudioSource):
    def get_audio(self, **kwargs) -> np.ndarray:
        audio_path = kwargs.pop("audio_path", None)
        if audio_path is None:
            raise ValueError("Audio path is required for AudioFileSource")
        try:
            return np.load(audio_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        return audio
    
class AudioRecordingSource(AudioSource):
    def get_audio(self, **kwargs) -> np.ndarray:
        try:
            import sounddevice as sd
        except ImportError:
            raise ImportError("Sounddevice is required for AudioRecordingSource (pip install sounddevice)")
        duration = kwargs.pop("duration", 1)
        frequency = kwargs.pop("frequency", 44100)
        channels = kwargs.pop("channels", 1)
        recordig = sd.rec(int(duration * frequency), samplerate=frequency, channels=channels)
        sd.wait()
        return recordig
        
    
    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        return audio
    

