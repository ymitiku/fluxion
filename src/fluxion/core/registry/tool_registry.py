import docstring_parser
import inspect
import logging
from typing import List, Dict, Any, Callable
from typing import Dict, Any

import logging
import time
from typing import Dict, Any, Callable, Optional
from pydantic import ValidationError, BaseModel
from fluxion.core.registry.agent_registry import AgentRegistry


logger = logging.getLogger("ToolRegistry")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


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
    logger.info(f"Starting agent call: {agent_name} with inputs: {inputs}")

    # Retrieve the agent from the registry
    agent = AgentRegistry.get_agent(agent_name)
    if not agent:
        error_message = f"Agent '{agent_name}' is not registered in the AgentRegistry."
        logger.error(error_message)
        raise ValueError(error_message)

    # Validate input
    try:
        validated_input = agent.validate_input(inputs)
        logger.debug(f"Input validated for agent '{agent_name}': {validated_input}")
    except ValidationError as e:
        error_message = f"Input validation failed for agent '{agent_name}': {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)

    # Retry mechanism
    retries = 0
    while retries <= max_retries:
        try:
            # Execute the agent
            if isinstance(validated_input, BaseModel):
                validated_input = validated_input.dict()

            result = agent.execute(**validated_input)
            logger.info(f"Agent '{agent_name}' executed successfully on attempt {retries + 1}")

            # Validate output
            validated_output = agent.validate_output(result)
            logger.debug(f"Output validated for agent '{agent_name}': {validated_output}")

            if isinstance(validated_output, BaseModel):
                validated_output = validated_output.dict()
            
            return validated_output

        except Exception as e:
            retries += 1
            logger.warning(
                f"Execution failed for agent '{agent_name}' on attempt {retries}: {str(e)}"
            )
            if retries > max_retries:
                if fallback:
                    logger.info(
                        f"Max retries exceeded for agent '{agent_name}'. Executing fallback."
                    )
                    fallback_result = fallback(inputs)
                    logger.info(f"Fallback executed successfully for agent '{agent_name}'")
                    return fallback_result
                error_message = (
                    f"Agent '{agent_name}' execution failed after {max_retries} retries: {str(e)}"
                )
                logger.error(error_message)
                raise RuntimeError(error_message)

            time.sleep(retry_backoff)
            logger.debug(f"Retrying agent '{agent_name}' after backoff: {retry_backoff}s")


def extract_function_metadata(func):
    """
    Extract metadata from a Python function.

    Args:
        func (function): The Python function to extract metadata from.

    Returns:
        dict: A dictionary containing function metadata.
    """
    signature = inspect.signature(func)
    docstring = docstring_parser.parse(func.__doc__)

    params_descriptions = {param.arg_name: param.description for param in docstring.params}


    parameters = {
        name: {
            "type": param.annotation.__name__ if param.annotation != inspect._empty else "unknown",
            "description": params_descriptions.get(name, "No description provided."),
        }
        for name, param in signature.parameters.items()
    }
    metadata = {
        "name": "{}.{}".format(func.__module__, func.__name__),
        "description": docstring.short_description or "No description provided.",
        "parameters": {
            "type": "object",
            "properties": parameters,
            "required": [
                name for name, param in signature.parameters.items() if param.default == inspect._empty
            ],
        },
    }
    return metadata




class ToolRegistry:
    """
    Instance-based registry for managing tools within an agent.
    """
    def __init__(self):
        self._registry: Dict[str, Callable] = {}

    def register_tool(self, func: Callable):
        """
        Register a tool function.

        Args:
            func (Callable): The tool function to register.
        """
        metadata = extract_function_metadata(func)
        tool_name = metadata["name"]
        if tool_name in self._registry:
            raise ValueError(f"Tool '{tool_name}' is already registered.")
        self._registry[tool_name] = {"func": func, "metadata": metadata}

    def get_tool(self, name: str) -> Dict[str, Any]:
        """
        Get a registered tool by name.

        Args:
            name (str): The name of the tool.

        Returns:
            Dict[str, Any]: The tool metadata.
        """
        if name not in self._registry:
            raise ValueError(f"Tool '{name}' is not registered.")
        return {
            "type": "function",
            "function": self._registry[name]["metadata"],
        }

    def list_tools(self) -> Dict[str, Any]:
        """
        List all registered tools.

        Returns:
            Dict[str, Any]: A dictionary of tool metadata.
        """
        return {name: tool["metadata"] for name, tool in self._registry.items()}

    def invoke_tool_call(self, tool_call: Dict[str, Any]) -> Any:
        """
        Invoke a registered tool dynamically.

        Args:
            tool_call (Dict[str, Any]): Tool call details including function name and arguments.

        Returns:
            Any: The result of the tool function.
        """
        func_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        metadata = self.get_tool(func_name)["function"]

        self.validate_arguments(metadata, arguments)

        tool = self._registry.get(func_name)
        if not tool:
            raise ValueError(f"Tool '{func_name}' is not registered.")

        func = tool["func"]
        return func(**arguments)
    
    def clear_registry(self):
        """
        Clear the tool registry.
        """
        self._registry.clear()

    def validate_arguments(cls, metadata, arguments):
        properties = metadata["parameters"]["properties"]
        required = metadata["parameters"]["required"]
        for arg in required:
            if arg not in arguments:
                raise ValueError(f"Missing required argument: {arg}")
            expected_type = properties[arg]["type"]
            if expected_type != "unknown" and not isinstance(arguments[arg], eval(expected_type)):
                raise TypeError(f"Argument '{arg}' must be of type {expected_type}.")