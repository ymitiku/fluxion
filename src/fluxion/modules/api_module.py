from abc import ABC, abstractmethod
from typing import Dict, Any
import requests

class ApiModule(ABC):
    def __init__(self, endpoint: str, headers: dict = {}, timeout: int = 10):
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
        output = response.json()
        if "error" in output:
            raise RuntimeError("API request failed: {}".format(output["error"]))
        return output
    
    
    
    @abstractmethod
    def post_process(self, response: Dict[str, Any], full_response: bool = False):
        pass


    @abstractmethod
    def execute(self, *args, **kwargs):
        pass