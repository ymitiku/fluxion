import requests
from .api_module import ApiModule
class LLMIntegration(ApiModule):
    """
    Provides an interface for interacting with a locally hosted LLM via REST API.
    """
    def __init__(self, endpoint: str, model: str = None, headers: dict = None, timeout: int = 10):
        super().__init__(endpoint, headers, timeout)
        self.model = model
        
    def query(self, prompt: str, stream: bool = False):
        """
        Queries the LLM server with the given prompt.

        Args:
            prompt (str): The prompt to query the LLM with.
            stream (bool): Whether to stream the response.

        Returns:
            dict: The response from the server.
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
        }
        return self.get_response(data)

