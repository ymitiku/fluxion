from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional
import requests
from .api_module import ApiModule

"""
fluxion.modules.llm_modules
~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides an interface for interacting with a locally or remotely hosted LLM via REST API.

llm_modules:
Example-Usage::
    from fluxion.modules.llm_query_module import LLMQueryModule

    # Initialize the LLMQueryModule
    llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

    # Query the LLM
    response = llm_module.query(prompt="What is the capital of France?")
    print(response)
    ```

    ```python

    from fluxion.modules.llm_query_module import LLMChatModule

    # Initialize the LLMChatModule
    llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

    # Chat with the LLM
    response = llm_module.chat(messages= [{
        "role": "user",
        "content": "Hello!"
        },
        {
        "role": "assistant",
        "content": "Hello, how can I help you?"
        }]
    )

    print(response)
"""

class LLMApiModule(ApiModule, ABC):
    """
    Provides an interface for interacting with a locally hosted LLM via REST API.

    This class abstracts common patterns for interacting with an LLM via REST API.

    """
    def __init__(self, endpoint: str, model: str = None, headers: Dict[str, Any] = {}, timeout: int = 10, response_key: str = "response", temperature:  Optional[float] = None, seed: Optional[int] = None):
        """ Initialize the LLMApiModule.
        
        Args:
            endpoint (str): The API endpoint URL.
            model (str): The model name to use.
            headers (dict, optional): Headers to include in the API requests. Defaults to an empty dictionary.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10 seconds.
            response_key (str, optional): The key to use for the response. Defaults to "response"
            temperature (float, optional): The temperature parameter for the LLM. Defaults to None.
            seed (int, optional): The seed parameter for the LLM. Defaults to None.
    
        """
        super().__init__(endpoint, headers, timeout)
        self.model = model
        self.response_key = response_key
        self.temperature = temperature
        self.seed = seed
    
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """ Execute the LLM module. 

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Dict[str, Any]: The response from the LLM.
        """
        inputs = self.get_input_params(*args, **kwargs)
        full_response = kwargs.get("full_response", False)
        for key, value in inputs.items():
            if value is None or value == "":
                raise ValueError(f"Invalid input: {key} is empty.")
        return self.get_response(inputs, full_response)


    def get_input_params(self, *args, **kwargs) -> Dict[str, Any]:
        """ Get the input parameters for the LLM module.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Dict[str, Any]: The input parameters for the LLM module.
        """
        output = {
            "model": self.model,
            "stream": False
        }
        if self.temperature:
            output["temperature"] = self.temperature
        if self.seed:
            output["seed"] = self.seed
        return output
    

    def get_response(self, data, full_response=False) -> Dict[str, Any]:
        """ Send a POST request to the API endpoint and return the response.

        Args:
            data (Dict[str, str]): The data to send in the POST request.
            full_response (bool): Whether to return the full response or a processed subset.

        Returns:
            Dict[str, Any]: The parsed JSON response from the API.
        """
        try:
            response = super().get_response(data)
            return self.post_process(response, full_response)

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {e}"}
        
    def post_process(self, response: Dict[str, Any], full_response: bool = False):
        """ Post-process the API response.

        Args:
            response (Dict[str, Any]): The raw response from the API.
            full_response (bool): Whether to return the full response or a processed subset.

        Returns:
            Dict[str, Any]: The processed response data.
        """
        if not full_response and "error" not in response:
            response = response[self.response_key]
        return response




class LLMQueryModule(LLMApiModule):
    """
    A class to handle querying an LLM via REST API. 

    This class abstracts common patterns for querying an LLM via REST API.

    LLMQueryModule:
    example-usage::
        from fluxion.modules.llm_query_module import LLMQueryModule

        # Initialize the LLMQueryModule
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

        # Query the LLM
        response = llm_module.query(prompt="What is the capital of France?")
        print(response)
        
    """


    def get_input_params(self, prompt: str, **kwargs) -> Dict[str, str]:
        """
        Get the input parameters for the LLM query.

        Args:
            prompt (str): The prompt for the LLM.

        Returns:
            Dict[str, str]: The input parameters for the LLM query.
        """
        data = super().get_input_params(**kwargs)
        data["prompt"] = prompt
        return data
    
    def post_process(self, response: Union[str, Dict[str, Any]], full_response = False):
        if response is None:
            return {"error": "No response received."}
        elif type(response) == str:
            if response == "":
                return {"error": "No response received."}
            return {
                "content": response,
                "role": "assistant"
            }
        else:
            return super().post_process(response, full_response)
        

class LLMChatModule(LLMApiModule):
    """
    A class to handle chatting with an LLM via REST API.

    LLMChatModule:
    example-usage::
        from fluxion.modules.llm_query_module import LLMChatModule

        # Initialize the LLMChatModule
        llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

        # Chat with the LLM
        response = llm_module.chat(messages= [{
            "role": "user",
            "content": "Hello!"
            },
            {
            "role": "assistant",
            "content": "Hello, how can I help you?"
            }]
        )

        print(response)
    """
    def __init__(self, *args, response_key: str = "message", **kwargs):
        """ Initialize the LLMChatModule.
        
        Args:
            endpoint (str): The API endpoint URL.
            model (str): The model name to use.
            headers (dict, optional): Headers to include in the API requests. Defaults to an empty dictionary.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10 seconds.
            response_key (str, optional): The key to use for the response. Defaults to "message"
        """
        super().__init__(*args, response_key=response_key, **kwargs)

    def get_input_params(self, *args, messages: List[str], tools: List[Dict[str, str]] = {}, **kwargs) -> Dict[str, Any]:
        """
        Get the input parameters for the LLM chat.

        Args:
            messages (List[str]): The messages to chat with the LLM.

        Returns:
            Dict[str, str]: The input parameters for the LLM chat.
        """
        data = super().get_input_params(*args, **kwargs)
        data["messages"] = messages
        data["tools"] = tools or []
        return data
    
    def post_process(self, response, full_response = False):
        if response is None:
            return {"error": "No response received."}
        elif type(response) == dict and "error" in response:
            return response
        elif type(response) == dict and self.response_key in response:
            return response[self.response_key]
        return super().post_process(response, full_response)

