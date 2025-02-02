"""
fluxion_ai.core.agent
~~~~~~~~~~~~~~~~~~

Defines the `Agent` class, which serves as the base class for agents in the Fluxion framework.

Agents represent intelligent components that can execute tasks, process inputs, and interact with the environment.
"""

from abc import ABC, abstractmethod
import json
from typing import Any, Dict, Type
from pydantic import BaseModel
import logging

from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxon.parser import parse_json_with_recovery
from fluxon.structured_parsing.fluxon_structured_parser import FluxonStructuredParser
from fluxon.structured_parsing.exceptions import FluxonError


class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement. It outlines the basic structure of an agent in the Fluxion framework.
    
    It provides the following attributes:
    - name: The unique name of the agent.
    - description: The description of the agent.
    - system_instructions: System instructions for the agent.

    Agent:
    Example usage::
        from fluxion_ai.core.agent import Agent
        class MyAgent(Agent):
            def execute(self, **kwargs):
                return "Hello, World!"
        my_agent = MyAgent(name="MyAgent", description="My first agent")
        result = my_agent.execute()
        print(result)
        # Hello, World!
    """

    def __init__(self, name: str, description: str = "", system_instructions: str = ""):
        """
        Initialize the agent and register it.

        Args:
            name (str): The unique name of the agent.
            description (str): The description of the agent (default: "").
            system_instructions (str): System instructions for the agent (default: "").
        Raises:
            ValueError: If the name is not unique.
        """
        self.name = name
        self.description = description
        self.system_instructions = system_instructions
        AgentRegistry.register_agent(name, self)
        
    @abstractmethod
    def execute(self, **kwargs: Dict[str, Any]) -> str:
        """
        Execute the agent logic.

        This method must be implemented by subclasses.

        Args:
            **kwargs (Dict[str, Any]): Arbitrary keyword arguments for task execution.

        Returns:
            str: The result or response from the agent.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass

    def __del__(self):
        """
        Unregister the agent when it is deleted.
        """
        self.cleanup()

    def cleanup(self):
        """
        Unregister the agent from the registry.
        """
        AgentRegistry.unregister_agent(self.name)

    def metadata(self) -> Dict[str, Any]:
        """
        Generate metadata for the agent.

        Returns:
            Dict[str, Any]: A dictionary containing the agent's metadata.
        """
        return {
            "name": self.name,
            "description": self.description,
        }

class JsonInputOutputAgent(ABC):
    """
    This class provides abstraction for agents the produce json output. It provides a method to parse the response into JSON data.

    JsonInputOutputAgent:
    Example usage::
        from fluxion_ai.core.agent import JsonInputOutputAgent
        class MyAgent(JsonInputOutputAgent):
            def execute(self, **kwargs):
                return self.parse_response("{\"message\": \"Hello, World!\"}")
        my_agent = MyAgent(name="MyAgent", description="My first agent")
        response = my_agent.execute()
        result = my_agent.parse_response(response)
        print(result)

    """

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the response into JSON.

        Args:
            response (str): The response to parse.

        Returns:
            Dict[str, Any]: The parsed JSON data.

        Raises:
            ValueError: If the response cannot be parsed.
        """
        try:
            logging.info("Trying to parse response using json.loads")
            return json.loads(response)
        except json.decoder.JSONDecodeError:
            try:
                logging.info("Json loads failed. Trying to parse response using structured parser")
                structured_parser = FluxonStructuredParser()
                parsed_tokens = structured_parser.parse(response)
                parsed_json = structured_parser.render(parsed_tokens, compact=True)
                return json.loads(parsed_json)
            except FluxonError as e:
                logging.info("Structured parser failed. Trying to parse response using recovery")
                return parse_json_with_recovery(response)

        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
            


class StructuredOutputAgent(ABC):
    def __init__(self, output_schema: Type[BaseModel]):
        self.output_schema = output_schema


    def validate_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.output_schema(**output).dict()
        except Exception as e:
            raise ValueError(f"Output validation failed: {str(e)}")
        
    def parse_to_schema(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """ Parse the response into a structured output format.

        Args:
            response (Dict[str, Any]): The response to parse. If content is not found or is empty raises ValueError. If the response contains "error" key, it will be propagated as a ValueError.

        raises: 
            ValueError: If the response contains an error key or content is not found or is empty.
        
        """
        if "error" in response:
            raise ValueError(response["error"])
        
        if "content" not in response or response["content"]  is None or response["content"].strip() == "":
            raise ValueError("Empty or missing content in response")
        
        return self.validate_output(response["content"])