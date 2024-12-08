import inspect
from typing import List
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



def invoke_tool_call(tool_call: Dict[str, Any]):
    """
    Invoke a tool call dynamically using the tool registry.

    Args:
        tool_call (dict): The tool call data, including function name and arguments.

    Returns:
        Any: The result of the function call.
    """
    func_name = tool_call["function"]["name"]
    arguments = tool_call["function"]["arguments"]

    tool = ToolRegistry.get_tool(func_name)
    if not tool:
        raise ValueError(f"Function '{func_name}' is not registered.")

    func = tool["func"]
    return func(**arguments)






class ToolRegistry:
    _registry = {}

    @classmethod
    def register_tool(cls, func):
        metadata = extract_function_metadata(func)
        cls._registry[metadata["name"]] = {"func": func, "metadata": metadata}

    @classmethod
    def get_tool(cls, name):
        if name not in cls._registry:
            raise ValueError(f"Tool '{name}' is not registered.")
        tool = cls._registry.get(name)
        return {
            "type": "function",
            "function": tool["metadata"],
        }

    @classmethod
    def get_tool_func(self, name):
        if name not in self._registry:
            raise ValueError(f"Tool '{name}' is not registered.")
        return self._registry.get(name)["func"]
    
    @classmethod
    def get_tool_names(cls):
        return list(cls._registry.keys())
    
    
    

    @classmethod
    def list_tools(cls):
        return {name: tool["metadata"] for name, tool in cls._registry.items()}
    
    @classmethod
    def invoke_tool_call(cls, tool_call: Dict[str, Any]):
        """
        Invoke a tool call dynamically using the tool registry.

        Args:
            tool_call (dict): The tool call data, including function name and arguments.

        Returns:
            Any: The result of the function call.
        """
        func_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        metadata = ToolRegistry.get_tool(func_name)["function"]

        cls.validate_arguments(metadata, arguments)

        tool = ToolRegistry.get_tool(func_name)
        if not tool:
            raise ValueError(f"Function '{func_name}' is not registered.")

        func = cls.get_tool_func(func_name)
        try :
            return func(**arguments)
        except Exception as e:
            raise RuntimeError(f"Error invoking function '{func_name}': {e}")
    
    @classmethod
    def validate_arguments(cls, metadata, arguments):
        properties = metadata["parameters"]["properties"]
        required = metadata["parameters"]["required"]
        for arg in required:
            if arg not in arguments:
                raise ValueError(f"Missing required argument: {arg}")
            expected_type = properties[arg]["type"]
            if expected_type != "unknown" and not isinstance(arguments[arg], eval(expected_type)):
                raise TypeError(f"Argument '{arg}' must be of type {expected_type}.")

    @classmethod
    def clear_registry(cls):
        cls._registry.clear()
    





if __name__ == "__main__":
    
    # Example function
    def get_current_weather(location: str, format: str = "celsius"):
        """Get the current weather for a location.
        
        :param location: The location to get the weather for.
        :param format: The temperature format (default: celsius).
        :return: The current weather
        """
        return "The current weather is 25 degrees celsius in Paris."

    registry = ToolRegistry()
    registry.register_tool(get_current_weather)
    print(registry.list_tools())

    tool_call = {"function":{"name":"get_current_weather","arguments":{"format":"celsius","location":"Paris"}}}
    

    result = registry.invoke_tool_call(tool_call)
    print(result)