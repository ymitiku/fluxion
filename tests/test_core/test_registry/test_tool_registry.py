import unittest
from typing import Dict, Any
from fluxion.core.registry.tool_registry import ToolRegistry, extract_function_metadata
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.registry.tool_registry import call_agent
from fluxion.core.agents.agent import Agent
from fluxion.models.message_model import ToolCall, MessageHistory
from pydantic import BaseModel

class TestToolRegistry(unittest.TestCase):
    def setUp(self):
        self.tool_registry = ToolRegistry()
        

        def example_tool(param1: int, param2: str = "default"):
            """
            Example tool function.

            :param param1: An integer parameter.
            :param param2: A string parameter.
            :return: A formatted string.
            """
            return f"Received {param1} and {param2}"

        self.example_tool = example_tool
        self.tool_registry.register_tool(example_tool)

    def tearDown(self):
        self.tool_registry.clear_registry()

    def test_metadata_extraction(self):
        metadata = extract_function_metadata(self.example_tool)
        expected_metadata = {
            "name": "test_tool_registry.example_tool",
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
        tools = self.tool_registry.list_tools()
        self.assertIn("test_tool_registry.example_tool", tools)
        self.assertEqual(tools["test_tool_registry.example_tool"]["name"], "test_tool_registry.example_tool")

    def test_invoke_tool_call_success(self):
        tool_call = ToolCall.from_llm_format({
            "function": {
                "name": "test_tool_registry.example_tool",
                "arguments": {
                    "param1": 42,
                    "param2": "hello",
                },
            }
        })
        result = self.tool_registry.invoke_tool_call(tool_call)
        self.assertEqual(result, "Received 42 and hello")

    def test_invoke_tool_call_missing_argument(self):
        tool_call = ToolCall.from_llm_format({
            "function": {
                "name": "test_tool_registry.example_tool",
                "arguments": {
                    "param2": "hello",
                },
            }
        })
        with self.assertRaises(ValueError) as context:
            self.tool_registry.invoke_tool_call(tool_call)
        self.assertIn("Missing required argument: param1", str(context.exception))

    def test_invoke_tool_call_invalid_tool(self):
        tool_call = ToolCall.from_llm_format({
            "function": {
                "name": "test_tool_registry.non_existent_tool",
                "arguments": {
                    "param1": 42,
                },
            }
        })
        with self.assertRaises(ValueError) as context:
            self.tool_registry.invoke_tool_call(tool_call)
        self.assertIn("Tool 'test_tool_registry.non_existent_tool' is not registered.", str(context.exception))

    def test_invoke_tool_call_type_error(self):
        tool_call = ToolCall.from_llm_format({
            "function": {
                "name": "test_tool_registry.example_tool",
                "arguments": {
                    "param1": "invalid_type",  # Should be int
                    "param2": "hello",
                },
            }
        })
        with self.assertRaises(TypeError) as context:
            self.tool_registry.invoke_tool_call(tool_call)
        self.assertIn("Argument 'param1' must be of type int.", str(context.exception))


class MockAgent(Agent):

    def execute(self, messages: MessageHistory) -> MessageHistory:
        value = int(messages[-1].content)
        return {"result": value * 2}


class TestCallAgent(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.agent = MockAgent("mock_agent")

    def tearDown(self):
        AgentRegistry.clear_registry()

    def test_call_agent_valid(self):
        messages = [{"role": "user", "content": "10"}]
        result = call_agent("mock_agent", messages)
        self.assertEqual(result, {"result": 20})

    def test_call_agent_not_registered(self):
        with self.assertRaises(ValueError):
            call_agent("non_existent_agent", {})

if __name__ == "__main__":
    unittest.main()
