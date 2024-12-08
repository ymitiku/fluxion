import unittest
from fluxion.core.registry.tool_registry import ToolRegistry, extract_function_metadata


class TestToolRegistry(unittest.TestCase):
    def setUp(self):
        ToolRegistry._registry = {}  # Reset registry before each test

        def example_tool(param1: int, param2: str = "default"):
            """
            Example tool function.

            :param param1: An integer parameter.
            :param param2: A string parameter.
            :return: A formatted string.
            """
            return f"Received {param1} and {param2}"

        self.example_tool = example_tool
        ToolRegistry.register_tool(example_tool)

    def tearDown(self):
        ToolRegistry._registry = {}  # Reset registry after each test

    def test_metadata_extraction(self):
        metadata = extract_function_metadata(self.example_tool)
        expected_metadata = {
            "name": "example_tool",
            "description": "Example tool function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "int", "description": "An integer parameter."},
                    "param2": {"type": "str", "description": "A string parameter."},
                },
                "required": ["param1"],
            },
        }
        self.assertEqual(metadata, expected_metadata)

    def test_register_tool(self):
        tools = ToolRegistry.list_tools()
        self.assertIn("example_tool", tools)
        self.assertEqual(tools["example_tool"]["name"], "example_tool")

    def test_invoke_tool_call_success(self):
        tool_call = {
            "function": {
                "name": "example_tool",
                "arguments": {
                    "param1": 42,
                    "param2": "hello",
                },
            }
        }
        result = ToolRegistry.invoke_tool_call(tool_call)
        self.assertEqual(result, "Received 42 and hello")

    def test_invoke_tool_call_missing_argument(self):
        tool_call = {
            "function": {
                "name": "example_tool",
                "arguments": {
                    "param2": "hello",
                },
            }
        }
        with self.assertRaises(ValueError) as context:
            ToolRegistry.invoke_tool_call(tool_call)
        self.assertIn("Missing required argument: param1", str(context.exception))

    def test_invoke_tool_call_invalid_tool(self):
        tool_call = {
            "function": {
                "name": "non_existent_tool",
                "arguments": {
                    "param1": 42,
                },
            }
        }
        with self.assertRaises(ValueError) as context:
            ToolRegistry.invoke_tool_call(tool_call)
        self.assertIn("Tool 'non_existent_tool' is not registered.", str(context.exception))

    def test_invoke_tool_call_type_error(self):
        tool_call = {
            "function": {
                "name": "example_tool",
                "arguments": {
                    "param1": "invalid_type",  # Should be int
                    "param2": "hello",
                },
            }
        }
        with self.assertRaises(TypeError) as context:
            ToolRegistry.invoke_tool_call(tool_call)
        self.assertIn("Argument 'param1' must be of type int.", str(context.exception))


if __name__ == "__main__":
    unittest.main()
