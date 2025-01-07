"""
fluxion.core.agent
~~~~~~~~~~~~~~~~~~

Defines the `Agent` class, which serves as the base class for agents in the Fluxion framework.

Agents represent intelligent components that can execute tasks, process inputs, and interact with the environment.
"""

from abc import ABC, abstractmethod
import json
import time
from typing import Any, Dict, Type, Optional, Callable
from pydantic import BaseModel, ValidationError
import logging

from fluxion.core.registry.agent_registry import AgentRegistry
from fluxon.parser import parse_json_with_recovery
from fluxon.structured_parsing.fluxon_structured_parser import FluxonStructuredParser
from fluxon.structured_parsing.exceptions import FluxonError



class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement.

    Attributes:
        name (str): The unique name of the agent.
        system_instructions (str): System instructions for the agent.
    """

    def __init__(self, name: str, system_instructions: str = "", input_schema: Type[BaseModel] = None, output_schema: Type[BaseModel] = None):
        """
        Initialize the agent and register it.

        Args:
            name (str): The unique name of the agent.
            system_instructions (str): System instructions for the agent (default: "").
            input_schema (Type[BaseModel], optional): The input schema for the agent (default: None).
            output_schema (Type[BaseModel], optional): The output schema for the agent (default: None).

        Raises:
            ValueError: If the name is not unique.
        """
        self.name = name
        self.system_instructions = system_instructions
        self.input_schema = input_schema
        self.output_schema = output_schema
        AgentRegistry.register_agent(name, self)

    def validate_input(self, input_data: Dict[str, Any]):
        """
        Validate input data against the defined input schema.

        Args:
            input_data (Dict[str, Any]): The input data to validate.

        Raises:
            ValidationError: If the input data does not match the schema.
        """
        if self.input_schema:
            return self.input_schema(**input_data)
        
    def validate_output(self, output_data: Any):
        """
        Validate output data against the defined output schema.

        Args:
            output_data (Any): The output data to validate.

        Raises:
            ValidationError: If the output data does not match the schema.
        """
        if self.output_schema:
            return self.output_schema(**output_data)
        
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
            print("Trying to parse response using json.loads")
            return json.loads(response)
        except json.decoder.JSONDecodeError:
            try:
                print("Json loads failed. Trying to parse response using structured parser")
                structured_parser = FluxonStructuredParser()
                parsed_tokens = structured_parser.parse(response)
                parsed_json = structured_parser.render(parsed_tokens, compact=True)
                return json.loads(parsed_json)
            except FluxonError as e:
                print("Structured parser failed. Trying to parse response using recovery")
                return parse_json_with_recovery(response)

        except Exception as e:
            raise ValueError(f"Failed to parse response: {str(e)}")
            



class AgentCallingWrapper:
    """
    A wrapper for invoking other agents as part of a plan or workflow.
    """

    logger = logging.getLogger("AgentCallingWrapper")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


    @staticmethod
    def call_agent(
        agent_name: str,
        inputs: Dict[str, Any],
        max_retries: int = 1,
        retry_backoff: float = 0.5,
        fallback: Optional[Callable] = None,
    ) -> Any:
        """
        Call another agent by name with retry and fallback logic.

        Args:
            agent_name (str): The name of the agent to invoke.
            inputs (Dict[str, Any]): Input data for the agent.
            max_retries (int, optional): Maximum number of retries (default: 1).
            retry_backoff (float, optional): Backoff time (in seconds) between retries (default: 0.5).
            fallback (Callable, optional): A fallback function to execute if retries fail.

        Returns:
            Any: The result of the agent's execution or the fallback result.

        Raises:
            ValueError: If the agent is not registered or validation fails.
            RuntimeError: If execution fails after retries and no fallback is provided.
        """
        AgentCallingWrapper.logger.info(f"Starting agent call: {agent_name} with inputs: {inputs}")

        # Retrieve the agent from the registry
        agent = AgentRegistry.get_agent(agent_name)
        if not agent:
            error_message = f"Agent '{agent_name}' is not registered in the AgentRegistry."
            AgentCallingWrapper.logger.error(error_message)
            raise ValueError(error_message)

        # Validate input
        try:
            validated_input = agent.validate_input(inputs)
            AgentCallingWrapper.logger.debug(f"Input validated for agent '{agent_name}': {validated_input}")
        except ValidationError as e:
            error_message = f"Input validation failed for agent '{agent_name}': {str(e)}"
            AgentCallingWrapper.logger.error(error_message)
            raise ValueError(error_message)

        # Retry mechanism
        retries = 0
        while retries <= max_retries:
            try:
                # Execute the agent
                result = agent.execute(**validated_input.dict())
                AgentCallingWrapper.logger.info(f"Agent '{agent_name}' executed successfully on attempt {retries + 1}")

                # Validate output
                validated_output = agent.validate_output(result)
                AgentCallingWrapper.logger.debug(f"Output validated for agent '{agent_name}': {validated_output}")
                return validated_output.dict()

            except Exception as e:
                retries += 1
                AgentCallingWrapper.logger.warning(
                    f"Execution failed for agent '{agent_name}' on attempt {retries}: {str(e)}"
                )
                if retries > max_retries:
                    if fallback:
                        AgentCallingWrapper.logger.info(
                            f"Max retries exceeded for agent '{agent_name}'. Executing fallback."
                        )
                        fallback_result = fallback(inputs)
                        AgentCallingWrapper.logger.info(f"Fallback executed successfully for agent '{agent_name}'")
                        return fallback_result
                    error_message = (
                        f"Agent '{agent_name}' execution failed after {max_retries} retries: {str(e)}"
                    )
                    AgentCallingWrapper.logger.error(error_message)
                    raise RuntimeError(error_message)

                time.sleep(retry_backoff)
                AgentCallingWrapper.logger.debug(f"Retrying agent '{agent_name}' after backoff: {retry_backoff}s")
