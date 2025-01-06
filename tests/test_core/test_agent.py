import unittest
from unittest.mock import patch, MagicMock
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.agent import JsonInputOutputAgent
from fluxon.structured_parsing.exceptions import FluxonError



class TestAgentBase(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()

    def tearDown(self):
        AgentRegistry.clear_registry()

    def test_agent_registration(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        self.assertIn("TestAgent", AgentRegistry.list_agents())
        self.assertIs(AgentRegistry.get_agent("TestAgent"), agent)

    def test_agent_unregistration(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        agent.cleanup()  # Explicitly call cleanup() instead of relying on __del__
        self.assertNotIn("TestAgent", AgentRegistry.list_agents())

    def test_abstract_class_instantiation(self):
        with self.assertRaises(TypeError):
            Agent(name="AbstractAgent")  # Abstract class cannot be instantiated





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
        mock_parse_json_with_recovery.assert_called_once_with(response)
        mock_parser_instance.parse.assert_called_once()
        mock_parser_instance.render.assert_called_once()

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_parse_response_fluxon_error(self, mock_parse_json_with_recovery):
        response = '{"key": "value"'  # Missing closing brace

        mock_parse_json_with_recovery.return_value = '{"key": "value"}'

        with patch("fluxon.structured_parsing.fluxon_structured_parser.FluxonStructuredParser.parse", side_effect=FluxonError):
            result = self.agent.parse_response(response)
            self.assertEqual(result, {"key": "value"})
            mock_parse_json_with_recovery.assert_called_once_with(response)

    def test_parse_response_unrecoverable_error(self):
        response = '{"key": "value"'  # Missing closing brace

        with patch("fluxon.parser.parse_json_with_recovery", side_effect=ValueError("Recovery failed")):
            with self.assertRaises(ValueError) as context:
                self.agent.parse_response(response)
            self.assertIn("Failed to parse response", str(context.exception))


if __name__ == "__main__":
    unittest.main()
