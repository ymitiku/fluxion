import unittest
from unittest.mock import patch, MagicMock
from fluxion.core.agents.coordination_agent import CoordinationAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.modules.llm_modules import LLMChatModule
from fluxon.parser import parse_json_with_recovery
import json

class TestCoordinationAgent(unittest.TestCase):

    def setUp(self):
        # Mock the LLMChatModule
        AgentRegistry.clear_registry()
        self.mock_llm_module = MagicMock(spec=LLMChatModule)
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"function": {"name": "call_agent", "arguments": {"agent_name": "test_group.TestAgent", "inputs": {"input_name": "input_value"}}}}'}
        # Mock AgentRegistry
        AgentRegistry.get_agent_metadata = MagicMock(return_value=[
            {
                "name": "test_group.TestAgent",
                "description": "A test agent.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input_name": {"type": "string", "description": "Input for the test agent."}
                    },
                    "required": ["input_name"]
                },
                "output_schema": {
                    "type": "object",
                    "properties": {
                        "output_name": {"type": "string", "description": "Output from the test agent."}
                    },
                    "required": ["output_name"]
                }
            }
        ])

        # Initialize CoordinationAgent
        self.agent = CoordinationAgent(
            name="TestCoordinationAgent",
            llm_module=self.mock_llm_module,
            agents_groups=["test_group"]
        )

    def test_execute_success(self):
        messages = [
            {"role": "user", "content": "Task: Perform a test action."}
        ]

        result = self.agent.execute(messages)

        expected_result = {
            "function": {
                "name": "call_agent",
                "arguments": {
                    "agent_name": "test_group.TestAgent",
                    "inputs": {
                        "input_name": "input_value"
                    }
                }
            }
        }


        self.assertEqual(result, expected_result)
        self.mock_llm_module.execute.assert_called_once()

    def test_execute_invalid_json(self):
        # Mock LLM to return invalid JSON
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": "Invalid JSON response"}
        

        messages = [
            {"role": "user", "content": "Task: Perform a test action."}
        ]

        result = self.agent.execute(messages)

        self.assertEqual(result, {"error": "Failed to parse the response from the LLM."})
        self.mock_llm_module.execute.assert_called_once()

    def test_no_agents_available(self):
        # Mock AgentRegistry to return no agents
        AgentRegistry.get_agent_metadata.return_value = []

        messages = [
            {"role": "user", "content": "Task: Perform a test action."}
        ]
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"error": "No suitable agent found or inputs could not be generated."}'}

        result = self.agent.execute(messages)
        
        self.assertEqual(result, {"error": "No suitable agent found or inputs could not be generated."})
        self.mock_llm_module.execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()
