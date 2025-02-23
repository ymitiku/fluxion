""" 
fluxion_ai.perception.sources.perception_source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides the base class for perception sources.

Classes:
    - PerceptionSource: Abstract base class for perception sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class PerceptionSource(ABC):
    
    def __init__(self, name: str, **kwargs: Dict[str, Any]):
        """ Initialize the PerceptionSource with the name of the source.
        Args:
            name (str): The name of the source
            kwargs: Additional keyword arguments for the source
        """
        self.name = name


    @abstractmethod
    def get_data(self, **kwargs) -> Dict[str, Any]:
        """ Get the data from the source. 

        Args:
            **kwargs: Additional keyword arguments for the source.
        Returns:
            Dict[str, Any]: The data from the source.
        """
        pass