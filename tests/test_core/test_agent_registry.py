import unittest
from fluxion.core.agent_registry import AgentRegistry

class TestAgentRegistry(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()

    def test_register_agent(self):
        mock_agent = object()
        AgentRegistry.register_agent("TestAgent", mock_agent)
        self.assertIn("TestAgent", AgentRegistry.list_agents())
        self.assertIs(AgentRegistry.get_agent("TestAgent"), mock_agent)

    def test_register_duplicate_agent(self):
        mock_agent = object()
        AgentRegistry.register_agent("TestAgent", mock_agent)

        # Attempt to register another agent with the same name
        with self.assertRaises(ValueError):
            AgentRegistry.register_agent("TestAgent", object())

    def test_unregister_agent(self):
        mock_agent = object()
        AgentRegistry.register_agent("TestAgent", mock_agent)

        # Unregister the agent
        AgentRegistry.unregister_agent("TestAgent")
        self.assertNotIn("TestAgent", AgentRegistry.list_agents())

    def test_get_agent(self):
        mock_agent = object()
        AgentRegistry.register_agent("TestAgent", mock_agent)
        retrieved_agent = AgentRegistry.get_agent("TestAgent")
        self.assertIs(retrieved_agent, mock_agent)

        # Test retrieving a non-existent agent
        self.assertIsNone(AgentRegistry.get_agent("NonExistentAgent"))

    def test_list_agents(self):
        mock_agent1 = object()
        mock_agent2 = object()
        AgentRegistry.register_agent("Agent1", mock_agent1)
        AgentRegistry.register_agent("Agent2", mock_agent2)

        agents = AgentRegistry.list_agents()
        self.assertListEqual(agents, ["Agent1", "Agent2"])
