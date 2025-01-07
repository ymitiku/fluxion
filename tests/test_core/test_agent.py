from pydantic import BaseModel
from typing import Dict, Any
import unittest
from unittest.mock import patch, MagicMock
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.agent import Agent, JsonInputOutputAgent, AgentCallingWrapper
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
    
    def test_validate_input(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        agent.input_schema = MagicMock()
        agent.validate_input({"key": "value"})
        agent.input_schema.assert_called_once_with(key="value")
    
    def test_validate_output(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        agent.output_schema = MagicMock()
        agent.validate_output({"key": "value"})
        agent.output_schema.assert_called_once_with(key="value")

class MockStructuredAgent(Agent):
    class InputSchema(BaseModel):
        value: int

    class OutputSchema(BaseModel):
        result: int

    def __init__(self, name: str):
        super().__init__(
            name=name,
            input_schema=MockStructuredAgent.InputSchema,
            output_schema=MockStructuredAgent.OutputSchema,
        )

    def execute(self, value: int) -> Dict[str, Any]:
        return {"result": value * 2}


class TestAgentCallingWrapper(unittest.TestCase):

    def setUp(self):
        AgentRegistry.clear_registry()
        self.agent = MockStructuredAgent("mock_agent")


    def tearDown(self):
        AgentRegistry.unregister_agent("mock_agent")

    def test_valid_call(self):
        inputs = {"value": 10}
        result = AgentCallingWrapper.call_agent("mock_agent", inputs)
        self.assertEqual(result, {"result": 20})

    def test_invalid_input(self):
        inputs = {"value": "invalid"}
        with self.assertRaises(ValueError) as context:
            AgentCallingWrapper.call_agent("mock_agent", inputs)
        self.assertIn("Input validation failed", str(context.exception))

    def test_missing_agent(self):
        with self.assertRaises(ValueError) as context:
            AgentCallingWrapper.call_agent("non_existent_agent", {})
        self.assertIn("Agent 'non_existent_agent' is not registered", str(context.exception))

    def test_execution_error(self):
        class FailingAgent(Agent):
            class InputSchema(BaseModel):
                pass

            class OutputSchema(BaseModel):
                pass

            def __init__(self, name: str):
                super().__init__(name=name, input_schema=None, output_schema=None)

            def execute(self, **kwargs):
                raise RuntimeError("Simulated failure")

        failing_agent = FailingAgent("failing_agent")

        with self.assertRaises(RuntimeError) as context:
            AgentCallingWrapper.call_agent("failing_agent", {})
        self.assertIn("execution failed", str(context.exception))

        AgentRegistry.unregister_agent("failing_agent")


    def test_retry_success_after_failure(self):
        with patch.object(self.agent, "execute", side_effect=[RuntimeError("Fail"), {"result": 10}]) as mock_execute:
            result = AgentCallingWrapper.call_agent("mock_agent", {"value": 5}, max_retries=2)
            self.assertEqual(result, {"result": 10})
            self.assertEqual(mock_execute.call_count, 2)

    def test_retry_with_fallback(self):
        def fallback_logic(inputs):
            return {"result": -1}

        with patch.object(self.agent, "execute", side_effect=RuntimeError("Fail")) as mock_execute:
            result = AgentCallingWrapper.call_agent(
                "mock_agent", {"value": 5}, max_retries=2, fallback=fallback_logic
            )
            self.assertEqual(result, {"result": -1})
            self.assertEqual(mock_execute.call_count, 3)  # 1 initial + 2 retries

    def test_exceed_retry_limit(self):
        with patch.object(self.agent, "execute", side_effect=RuntimeError("Fail")):
            with self.assertRaises(RuntimeError) as context:
                AgentCallingWrapper.call_agent("mock_agent", {"value": 5}, max_retries=1)
            self.assertIn("execution failed after 1 retries", str(context.exception))


    @patch("fluxion.core.agent_calling_wrapper.AgentCallingWrapper.logger")
    def test_logging_on_success(self, mock_logger):
        inputs = {"value": 5}
        result = AgentCallingWrapper.call_agent("mock_agent", inputs)
        self.assertEqual(result, {"result": 10})
        mock_logger.info.assert_any_call("Starting agent call: mock_agent with inputs: {'value': 5}")
        mock_logger.info.assert_any_call("Agent 'mock_agent' executed successfully on attempt 1")

    @patch("fluxion.core.agent_calling_wrapper.AgentCallingWrapper.logger")
    def test_logging_on_failure_and_fallback(self, mock_logger):
        def fallback_logic(inputs):
            return {"result": 0}

        with patch.object(MockAgent, "execute", side_effect=RuntimeError("Simulated failure")):
            result = AgentCallingWrapper.call_agent(
                "mock_agent", {"value": 5}, max_retries=2, fallback=fallback_logic
            )
            self.assertEqual(result, {"result": 0})
            mock_logger.warning.assert_called_with("Execution failed for agent 'mock_agent' on attempt 1")
            mock_logger.info.assert_any_call("Max retries exceeded for agent 'mock_agent'. Executing fallback.")





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


if __name__ == "__main__":
    unittest.main()
