from abc import ABC, abstractmethod
from typing import Dict, Any
import requests

class ApiModule(ABC):
    def __init__(self, endpoint: str, headers: dict = None, timeout: int = 10):
        """ Initialize the API module. """
        self.headers = headers or {}
        self.timeout = timeout
        self.endpoint = endpoint

    def get_response(self, data: Dict[str, str], **kwargs) -> Dict[str, str]:
        """
        Sends a POST request to the LLM server.

        Args:
            endpoint (str): The endpoint to send the request to.
            data (dict): The data to send in the request.

        Returns:
            dict: The response from the server.
        """
        response = requests.post(self.endpoint, json=data, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    
    
    
    @abstractmethod
    def post_process(self, response: Dict[str, Any], full_response: bool = False):
        pass