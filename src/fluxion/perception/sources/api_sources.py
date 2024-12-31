import requests
from typing import Dict, Any
from fluxion.core.perception.sources.perception_source import PerceptionSource



class APISource(PerceptionSource):
    """
    Text source that retrieves text data from an API endpoint.
    """
    def __init__(self, api_url: str = None, **kwargs: Dict[str, Any]):
        """
        Initialize the APITextSource with the API URL.

        Args:
            api_url (str): The URL of the API.
        """
        if "name" not in kwargs:
            kwargs["name"] = "APITextSource"
        
        super().__init__(**kwargs)
        self.api_url = api_url

   
    def get_data(self, **kwargs) -> str:
        """
        Get the text data from the API.

        Args:
            **kwargs: Additional keyword arguments for the API source.

        Returns:
            str: The text data from the API.
        """

        headers = kwargs.pop("headers", {})
        timeout = kwargs.pop("timeout", 5)
        method = kwargs.pop("method", "GET")
        data = kwargs.pop("data", None)
        if self.api_url is None:
            self.api_url = kwargs.pop("api_url", None)
        if self.api_url is None:
            raise ValueError("API URL is required for APITextSource")

        try:

            if method == "GET":
                response = requests.get(self.api_url, headers=headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(self.api_url, headers=headers, data=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get data from API: {e}") from e