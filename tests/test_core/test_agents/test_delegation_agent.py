import unittest
from unittest.mock import MagicMock, patch
from fluxion.core.agents.agent import Agent
from fluxion.core.agents.delegation_agent import DelegationAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.registry.agent_delegation_registry import AgentDelegationRegistry
from fluxion.core.modules.llm_modules import LLMChatModule
from fluxion.models.message_model import MessageHistory, Message
import json

class TestDelegationAgent(unittest.TestCase):

    def setUp(self):
        # Mock LLMChatModule
        AgentRegistry.clear_registry()
        self.mock_llm_module = MagicMock(spec=LLMChatModule)
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"agent_name": "DataSummarizer"}'}
        

        # Mock Generic Agent
        class MockGenericAgent(Agent):
            def __init__(self, name="GenericAgent"):
                super().__init__(name=name)

            def execute(self, messages: MessageHistory) -> MessageHistory:
                return MessageHistory(messages=[{"role": "assistant", "content": "Task handled by generic agent."}])
            

        self.generic_agent = MockGenericAgent()

        # Initialize DelegationAgent
        self.agent = DelegationAgent(
            name="TestDelegationAgent",
            llm_module=self.mock_llm_module,
            generic_agent=self.generic_agent
        )

        # Mock AgentRegistry
        self.mock_agent_metadata = {
            "name": "DataSummarizer",
            "description": "Summarizes the given data.",
        }

        # Mock DelegationRegistry
        self.agent.delegation_registry = MagicMock(spec=AgentDelegationRegistry)
        self.mock_data_summarizer = MagicMock(metadata=lambda: self.mock_agent_metadata, execute=lambda messages: MessageHistory(messages=[Message(role="assistant", content="Summarized successfully.")]))

    def test_delegate_task(self):
        self.agent.delegation_registry.add_delegation = MagicMock()

        task_description = "Summarize the sales report."
        agent_name = "DataSummarizer"

        self.agent.delegate_task(task_description, agent_name)

        self.agent.delegation_registry.add_delegation.assert_called_once_with(agent_name, task_description)

    def test_decide_and_delegate_successful(self):
        

        self.agent.delegation_registry.list_delegations.return_value = {
            "DataSummarizer": {
                "task_description": "Summarize the sales report.",
                "agent_metadata": self.mock_agent_metadata
            }
        }.items()
        self.agent.delegation_registry.get_delegation.return_value = {
            "task_description": "Summarize the sales report.",
            "agent_metadata": self.mock_agent_metadata
        }

        with patch.object(AgentRegistry, "get_agent", return_value=self.mock_data_summarizer):
            result = self.agent.decide_and_delegate(messages=MessageHistory(messages=[Message(role="user", content="Analyze the sales report.")]))
        
        self.assertEqual(result, MessageHistory(messages=[Message(role="assistant", content="Summarized successfully.")]))
        self.mock_llm_module.execute.assert_called_once()

    def test_decide_and_delegate_generic_agent(self):
        # Mock LLM response to indicate fallback to generic agent
        self.mock_llm_module.execute.return_value = {"role": "assistant", "content": '{"agent_name": "generic_agent"}'}
        
        messages = MessageHistory(messages=[Message(role="user", content="Analyze an unstructured task.")])
        result = self.agent.decide_and_delegate(messages=messages)
        

        self.assertEqual(result, MessageHistory(messages=[Message(role="assistant", content="Task handled by generic agent.")]))
        self.mock_llm_module.execute.assert_called_once()

    def test_execute_agent(self):
        agent_instance = MagicMock()
        agent_instance.execute.return_value = MessageHistory(messages=[Message(role="assistant", content="Summarized successfully.")])

        with patch.object(AgentRegistry, "get_agent", return_value=agent_instance):
            result = self.agent.execute_agent("DataSummarizer", MessageHistory(messages=[Message(role="user", content="Analyze the sales report.")]))   
        self.assertEqual(result, MessageHistory(messages=[Message(role="assistant", content="Summarized successfully.")]))
        agent_instance.execute.assert_called_once_with(messages=MessageHistory(messages=[Message(role="user", content="Analyze the sales report.")]))

    def test_execute_agent_missing_agent(self):
        with patch.object(AgentRegistry, "get_agent", return_value=None):
            with self.assertRaises(ValueError) as context:
                self.agent.execute_agent("NonExistentAgent", {})

        self.assertIn("Agent 'NonExistentAgent' is not registered.", str(context.exception))

if __name__ == "__main__":
    unittest.main()
