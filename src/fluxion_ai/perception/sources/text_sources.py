from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Generator, Iterable
from fluxion_ai.perception.sources.perception_source import PerceptionSource


"""
fluxion_ai.perception.sources.text_sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module defines abstraction to sources that provide text data to the agent. It defines the logic to get text data from different sources, such as
files, string and string buffer. The text sources module provides the necessary tools for the agent to interact with these sources and acquire
text data for processing and analysis.
"""

class TextSource(PerceptionSource, ABC):


    def get_data(self, **kwargs: Dict[str, Any]):
        text = self.get_text(**kwargs)
        return {"text": text}

    """
    Abstract base class for text sources.
    """
    @abstractmethod
    def get_text(self, **kwargs: Dict[str, Any]) -> str:
        """
        Get the text data from the source.

        Args:
            **kwargs: Additional keyword arguments for the source.

        Returns:
            str: The text data from the source.
        """
        pass

class FileTextSource(TextSource):
    """
    Text source that reads text data from a file.
    """
    def __init__(self, file_path: str = None, **kwargs: Dict[str, Any]):
        """
        Initialize the FileTextSource with the file path.

        Args:
            file_path (str): The path to the text file
        """
        if "name" not in kwargs:
            kwargs["name"] = "FileTextSource"
        super().__init__(**kwargs)
        self.file_path = file_path

    def get_text(self, **kwargs: Dict[str, Any]) -> str:
        """
        Get the text data from the file.

        Args:
            **kwargs: Additional keyword arguments for the file source.

        Returns:
            str: The text data from the file.
        """
        if "file_path" in kwargs:
            self.file_path = kwargs.pop("file_path", None)
        if self.file_path is None:
            raise ValueError("File path is required for FileTextSource")
        try:
            with open(self.file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except IOError as e:
            raise IOError(f"Error reading file {self.file_path}: {e}")
            
class StringBufferSource(TextSource):
    """
    A text source that uses a buffer of strings.
    """
    def __init__(self, buffer: Union[str, Generator[str, str, str]] = None, **kwargs: Dict[str, Any]):
        if "name" not in kwargs:
            kwargs["name"] = "StringBufferSource"
        super().__init__(**kwargs)
        self.buffer = buffer

    def get_text(self, **kwargs: Dict[str, Any]) -> str:
        if "buffer" in kwargs:
            self.buffer = kwargs.pop("buffer", None)
        if self.buffer is None:
            raise ValueError("Buffer is required for StringBufferSource")
        if isinstance(self.buffer, str):
            return self.buffer
        elif isinstance(self.buffer, Iterable):
            return " ".join(list(self.buffer))
        else:
            raise ValueError("Buffer must be a string or an iterable of strings.")