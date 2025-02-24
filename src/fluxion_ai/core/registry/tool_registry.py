import docstring_parser
from functools import wraps
import inspect
import logging
from pydantic import BaseModel, Field
from pydoc import locate
from typing import List, Dict, Any, Callable, Optional, Union, Literal

import logging
import time
from typing import Dict, Any, Callable, Optional
from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxion_ai.models.message_model import ToolCall, MessageHistory, Message



logger = logging.getLogger("ToolRegistry")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def call_agent(
    agent_name: str,
    messages: Union[str, List[Dict[str, Any]]],
    max_retries: int = 1,
    retry_backoff: float = 0.5,
    fallback: Optional[Callable] = None,
) -> Any:
    """
    Call another agent by name with retry and fallback logic.

    Args:
        agent_name (str): The name of the agent to invoke.
        messages (List[Dict[str, Any]]): The messages to pass to the agent. All messages must be in JSON format with the following structure: [{"role": "user|system|assistant|tool", "content": "message content"}].
        max_retries (int, optional): Maximum number of retries (default: 1).
        retry_backoff (float, optional): Backoff time (in seconds) between retries (default: 0.5).
        fallback (Callable, optional): A fallback function to execute if retries fail.

    Returns:
        Any: The result of the agent's execution or the fallback result.

    Raises:
        ValueError: If the agent is not registered or validation fails.
        RuntimeError: If execution fails after retries and no fallback is provided.
    """
    logger.info(f"Starting agent call: {agent_name}")

    # Retrieve the agent from the registry
    agent = AgentRegistry.get_agent(agent_name)
    if not agent:
        error_message = f"Agent '{agent_name}' is not registered in the AgentRegistry."
        logger.error(error_message)
        raise ValueError(error_message)

    if type(messages) == str:
        messages = MessageHistory.parse_raw(messages).messages
    elif type(messages) == list:
        messages = MessageHistory(messages = [Message.from_dict(message) for message in messages])
    else:
        assert isinstance(messages, MessageHistory), "messages must be a string, a list of dictionaries, or a MessageHistory object. Found: {}".format(type(messages))

    # Retry mechanism
    retries = 0
    while retries <= max_retries:
        try:
            result = agent.execute(messages=messages)
            logger.info(f"Agent '{agent_name}' executed successfully on attempt {retries + 1}")

            # Validate output
            logger.debug(f"Output validated for agent '{agent_name}': {result}")

            return result

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
                    fallback_result = fallback(messages)
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


class ToolProperty(BaseModel):
    description: str
    type: str

    def to_dict(self):
        return {
            "description": self.description,
            "type": self.type
        }

class ToolParameters(BaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, ToolProperty] = Field(..., description="The properties of the tool")
    required: List[str] = Field(..., description="The required parameters of the tool")

    def to_dict(self):
        return {
            "type": self.type,
            "properties": {key: value.to_dict() for key, value in self.properties.items()},
            "required": self.required
        }

class Tool:
    def __init__(self, name: str, description: str, parameters: ToolParameters, func_reference: Callable[..., Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func_reference = func_reference

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.to_dict()
        }
    
    def validate_args(self, args: Dict[str, Any]):
        for key in self.parameters.required:
            if key not in args:
                raise ValueError(f"Missing required argument: {key}")
        for key, value in args.items():
            if key not in self.parameters.properties:
                raise ValueError(f"Unexpected argument: {key}")
            property_type = locate(self.parameters.properties[key].type)

            if not isinstance(value, property_type):
                # raise TypeError(f"Expected {property_type} for argument {key}, got {type(value)}")
                raise TypeError(f"Argument '{key}' must be of type {property_type.__name__}.")
        return True
    
    def invoke(self, args: Dict[str, Any]):
        self.validate_args(args)
        return self.func_reference(**args)
    



def tool(func: Callable[..., Any]) -> Tool:
    """ Decorator for creating a Tool object from a function

    Args:
        func (Callable[..., Any]): The function to create a tool from
    
    Returns:
        Tool: The tool object created from the function    
    """

    

    metadata = extract_function_metadata(func)

    return Tool(
        name=metadata["name"],
        description=metadata["description"],
        parameters=ToolParameters(**metadata["parameters"]),
        func_reference=func
    )



class ToolRegistry:
    """
    Instance-based registry for managing tools within an agent.

    ToolRegistry:
    Example usage::
        from fluxion_ai.core.registry.tool_registry import ToolRegistry
        tool_registry = ToolRegistry()
        tool_registry.register_tool(my_tool_function)
        tool_registry.invoke_tool_call(tool_call)
    """
    def __init__(self):
        self._registry: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool):
        """
        Register a tool function.

        Args:
            tool (Tool): The tool object to register.
        """
        tool_name = tool.name
        if tool_name in self._registry:
            raise ValueError(f"Tool '{tool_name}' is already registered.")
        self._registry[tool_name] = tool

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
        tool = self._registry[name]
        return {
            "type": "function",
            "function": tool.to_dict()
        }

    def list_tools(self) -> Dict[str, Any]:
        """
        List all registered tools.

        Returns:
            Dict[str, Any]: A dictionary of tool metadata.
        """
        return {name: tool.to_dict() for name, tool in self._registry.items()}

    def invoke_tool_call(self, tool_call:ToolCall) -> Any:
        """
        Invoke a registered tool dynamically.

        Args:
            tool_call (Dict[str, Any]): Tool call details including function name and arguments.

        Returns:
            Any: The result of the tool function.
        """
        func_name = tool_call.name
        arguments = tool_call.arguments

        tool = self._registry.get(func_name)
        if not tool:
            raise ValueError(f"Tool '{func_name}' is not registered.")
        
        return tool.invoke(arguments)
    
    def clear_registry(self):
        """
        Clear the tool registry.
        """
        self._registry.clear()