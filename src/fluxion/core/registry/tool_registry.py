import inspect
from typing import List, Dict, Any, Callable
import docstring_parser
from typing import Dict, Any

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
        "name": func.__name__,
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