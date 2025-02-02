""" 
fluxion_ai.perception.perception
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides the base class for perceptions.

Classes:
    - Perception: Abstract base class for perceptions.
    - RawPerception: Perception for raw data.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from fluxion_ai.perception.sources.perception_source import PerceptionSource


class Perception(ABC):
    def __init__(self, name: str, perception_source: PerceptionSource):
        """
        Initialize the perception with the name of the perception.

        Args:
            name (str): The name of the perception.
        """
        self.name = name
        self.perception_source = perception_source


    def perceive(self, **kwargs) -> Dict[str, Any]:
        """
        Perceive the data from the source.

        Args:
            **kwargs: Additional keyword arguments for the perception.
        """
        data = self.perception_source.get_data(**kwargs)
        return self.process_data(data)
    

    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the data from the source.

        Args:
            data (Dict[str, Any]): The data from the source.

        Returns:
            Dict[str, Any]: The processed data.
        """
        pass


class RawPerception(Perception):
    def __init__(self, name: str, perception_source: PerceptionSource):
        """
        Initialize the raw perception with the name of the perception.

        Args:
            name (str): The name of the perception.
        """
        super().__init__(name, perception_source)


    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw data from the source.

        Args:
            data (Dict[str, Any]): The data from the source.

        Returns:
            Dict[str, Any]: The processed data.
        """
        return data