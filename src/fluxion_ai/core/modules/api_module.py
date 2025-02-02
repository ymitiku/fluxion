"""
fluxion_ai.modules.api_module
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an abstract base class for interacting with external APIs.

This module defines the `ApiModule` base class, which abstracts common API interaction patterns
such as sending POST requests and processing responses.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import requests


class ApiModule(ABC):
    """
    Abstract base class for interacting with APIs.

    This class provides common functionality for making POST requests and processing responses
    while allowing subclasses to define specific behavior via abstract methods.
    """

    def __init__(self, endpoint: str, headers: dict = None, timeout: int = 10):
        """
        Initialize the API module.

        Args:
            endpoint (str): The API endpoint URL.
            headers (dict, optional): Headers to include in the API requests. Defaults to an empty dictionary.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10 seconds.
        """
        self.headers = headers or {}
        self.timeout = timeout
        self.endpoint = endpoint

    def get_response(self, data: Dict[str, str], **kwargs) -> Dict[str, str]:
        """
        Sends a POST request to the API endpoint and returns the response.

        Args:
            data (dict): The data to send in the POST request.
            **kwargs: Additional arguments to pass to the requests library.

        Returns:
            dict: The parsed JSON response from the API.

        Raises:
            RuntimeError: If the API response contains an error key.
        """
        response = requests.post(self.endpoint, json=data, headers=self.headers, timeout=self.timeout)
        output = response.json()
        if "error" in output:
            raise RuntimeError("API request failed: {}".format(output["error"]))
        return output

    @abstractmethod
    def post_process(self, response: Dict[str, Any], full_response: bool = False):
        """
        Abstract method for post-processing API responses.

        Subclasses must implement this method to handle the processing of the raw response
        returned by the API.

        Args:
            response (dict): The raw response from the API.
            full_response (bool, optional): Whether to return the full response or a processed subset. Defaults to False.

        Returns:
            Any: The processed response data.
        """
        pass

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Abstract method for executing the API call.

        Subclasses must implement this method to define the logic for making API calls
        and processing the results.

        Args:
            *args: Positional arguments for the API call.
            **kwargs: Keyword arguments for the API call.

        Returns:
            Any: The result of the API call.
        """
        pass
