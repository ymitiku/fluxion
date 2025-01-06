"""
fluxion.core.agent
~~~~~~~~~~~~~~~~~~

Defines the `Agent` class, which serves as the base class for agents in the Fluxion framework.

Agents represent intelligent components that can execute tasks, process inputs, and interact with the environment.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxon.parser import parse_json_with_recovery
from fluxon.structured_parsing.fluxon_structured_parser import FluxonStructuredParser
from fluxon.structured_parsing.exceptions import FluxonError
import json


class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement.

    Attributes:
        name (str): The unique name of the agent.
        system_instructions (str): System instructions for the agent.
    """

    def __init__(self, name: str, system_instructions: str = ""):
        """
        Initialize the agent and register it.

        Args:
            name (str): The unique name of the agent.
            system_instructions (str): System instructions for the agent (default: "").

        Raises:
            ValueError: If the name is not unique.
        """
        self.name = name
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

class JsonInputOutputAgent(ABC):
    """
    Abstract base class for agents that output JSON data. It provides powerful interface for parsing LLM responses into JSON.
    It supports the following methods:
    - parse_response: Parse the response into JSON.
    - Error recovery: Automatically recover from JSON parsing errors.
    """

    def __init__(self, *args, input_schema: Dict[str, Any] = None, output_schema: Dict[str, Any] = None, **kwargs):
        """
        Initialize the agent.
        """
        super().__init__(*args, **kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
            


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
            return json.loads(response)
        except json.decoder.JSONDecodeError:
            structured_parser = FluxonStructuredParser()
            parsed_tokens = structured_parser.parse(parse_json_with_recovery(response))
            parsed_json = structured_parser.render(parsed_tokens, compact=True)
            return json.loads(parsed_json)
        except FluxonError as e:
            print("Response", response)
            parsed_json = parse_json_with_recovery(response)
            return json.loads(parsed_json)
        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
            
