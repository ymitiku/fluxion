from pydantic import BaseModel
from typing import Dict, Any
import unittest
from unittest.mock import patch, MagicMock
from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxion_ai.core.agents.agent import Agent, JsonInputOutputAgent
from fluxon.structured_parsing.exceptions import FluxonError
from fluxion_ai.core.registry.tool_registry import call_agent
from fluxion_ai.models.message_model import Message, MessageHistory, ToolCall

class MockAgent(Agent):
    def execute(self, messages: MessageHistory) -> Dict[str, Any]: 
        new_message = Message(role="assistant", content="Mock response")
        messages.append(new_message)
        return MessageHistory(messages=messages.messages)
class TestAgentBase(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.agent = MockAgent(name="TestAgent")

    def tearDown(self):
        AgentRegistry.clear_registry()

    def test_agent_registration(self):

        self.assertIn("TestAgent", AgentRegistry.list_agents())
        self.assertIs(AgentRegistry.get_agent("TestAgent"), self.agent)

    def test_agent_unregistration(self):

        self.agent.cleanup()  # Explicitly call cleanup() instead of relying on __del__
        self.assertNotIn("TestAgent", AgentRegistry.list_agents())

    def test_abstract_class_instantiation(self):
        with self.assertRaises(TypeError):
            Agent(name="AbstractAgent")  # Abstract class cannot be instantiated
    def test_call_agent_with_valid_metadata(self):
        inputs = MessageHistory(messages=[Message(role="user", content="Test message")])
        result = call_agent("TestAgent", inputs)[-1]
        self.assertEqual(result, Message(role="assistant", content="Mock response"))

    def test_call_agent_with_invalid_metadata(self):
        with self.assertRaises(ValueError) as context:
            call_agent("non_existent_agent", {})
        self.assertIn("Agent 'non_existent_agent' is not registered", str(context.exception))


class MockJsonInputOutputAgent(JsonInputOutputAgent):
    def execute(self, **kwargs):
        return "Execution successful"

class TestJsonInputOutputAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MockJsonInputOutputAgent()

    def test_parse_response_valid_json(self):
        response = '{"key": "value"}'
        result = self.agent.parse_response(response)
        self.assertEqual(result, {"key": "value"})

    @patch("fluxon.parser.parse_json_with_recovery")
    @patch("fluxon.structured_parsing.fluxon_structured_parser.FluxonStructuredParser")
    def test_parse_response_invalid_json_recovered(self, MockStructuredParser, mock_parse_json_with_recovery):
        response = '{"key": "value"'  # Missing closing brace

        mock_parse_json_with_recovery.return_value = '{"key": "value"}'
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = [{"key": "value"}]
        mock_parser_instance.render.return_value = '{"key": "value"}'
        MockStructuredParser.return_value = mock_parser_instance

        result = self.agent.parse_response(response)
        self.assertEqual(result, {"key": "value"})


    @patch("fluxon.parser.parse_json_with_recovery")
    def test_parse_response_fluxon_error(self, mock_parse_json_with_recovery):
        response = '{"key": "value"'  # Missing closing brace

        mock_parse_json_with_recovery.return_value = '{"key": "value"}'

        with patch("fluxon.structured_parsing.fluxon_structured_parser.FluxonStructuredParser.parse", side_effect=FluxonError):
            result = self.agent.parse_response(response)
            self.assertEqual(result, {"key": "value"})
            
    def test_parse_response_unrecoverable_error(self):
        response = '{"key": "value"}}'  # Double closing brace

        parsed = self.agent.parse_response(response)
        self.assertEqual(parsed, {})


    def test_parse_response_valid_json(self):
        response = '{"key": "value"}'
        result = self.agent.parse_response(response)
        self.assertEqual(result, {"key": "value"})

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_parse_response_recovery(self, mock_parse_json_with_recovery):
        response = '{"key": "value"'  # Missing closing brace
        mock_parse_json_with_recovery.return_value = {"key": "value"}

        result = self.agent.parse_response(response)
        self.assertEqual(result, {"key": "value"})


if __name__ == "__main__":
    unittest.main()
