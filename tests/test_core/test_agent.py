import unittest
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


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




if __name__ == "__main__":
    unittest.main()
