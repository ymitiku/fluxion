import unittest
from unittest.mock import patch, MagicMock
from fluxion.core.agents.agent import Agent
from fluxion.core.agents.coordination_agent import CoordinationAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.modules.llm_modules import LLMChatModule
from fluxon.parser import parse_json_with_recovery
from fluxion.models.message_model import MessageHistory, Message
import json

class MockAgent(Agent):
    def execute(self, messages: MessageHistory) -> Message:
        return Message(role="assistant", content="Mock response")
       

class TestCoordinationAgent(unittest.TestCase):
    

    def setUp(self):
        # Mock the LLMChatModule
        AgentRegistry.clear_registry()
        self.mock_llm_module = MagicMock(spec=LLMChatModule)
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"agent_name": "test_group.TestAgent"}'}
       
        test_agent = MockAgent(name="test_group.TestAgent")

        # Initialize CoordinationAgent
        self.agent = CoordinationAgent(
            name="TestCoordinationAgent",
            llm_module=self.mock_llm_module,
            agents_groups=["test_group"]
        )

    def test_execute_success(self):
        messages = MessageHistory(messages =  [Message(role="user", content="Task: Perform a test action.")])
        result = self.agent.coordinate_agents(messages)
        expected_result = Message(role="assistant", content="Mock response")

        self.assertEqual(result, expected_result)
        self.mock_llm_module.execute.assert_called_once()

    def test_execute_invalid_json(self):
        # Mock LLM to return invalid JSON
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": "Some invalid JSON response"}
    
        messages = MessageHistory(messages=[Message(role="user", content =  "Task: Perform a test action.")])
        result = self.agent.coordinate_agents(messages)
        self.assertIn("Invalid JSON response.", result.errors)
        self.mock_llm_module.execute.assert_called_once()

    @patch("fluxion.core.registry.agent_registry.AgentRegistry.get_agent_metadata")
    def test_no_agents_available(self, mock_get_agent_metadata):
        # Mock AgentRegistry to return no agents
        mock_get_agent_metadata .return_value = []
        messages = MessageHistory(messages=[Message(role="user", content =  "Task: Perform a test action.")])
       
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"error": "No suitable agent found or inputs could not be generated."}'}

        result = self.agent.coordinate_agents(messages)
        
        self.assertIn("No suitable agent found or inputs could not be generated.", result.errors)
        self.mock_llm_module.execute.assert_called_once()

if __name__ == "__main__":
    unittest.main()
