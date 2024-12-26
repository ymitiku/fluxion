from typing import Dict, Any
import unittest
from unittest.mock import MagicMock
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def execute(self,  input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": f"Processed {input_data}"}


class TestAgentNode(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.mock_agent = MockAgent(name="MockAgent")
        self.node = AgentNode(name="TestNode", agent=self.mock_agent)

    def test_execute_node(self):
        inputs = {"input_data": "test"}
        results = self.node.execute(results = {}, inputs = inputs)

        self.assertEqual(results, {"result": "Processed test"})

    def test_execute_with_dependencies(self):
        dependency_node = AgentNode(name="DependencyNode", agent=self.mock_agent)
        dependency_results = {"DependencyNode": {"result": "Processed dependency"}}
        self.node.dependencies.append(dependency_node)

        inputs = {"input_data": "test"}
        combined_inputs = {**inputs, **dependency_results}
        results = self.node.execute(inputs = inputs, results = dependency_results)
        self.assertEqual(results, {"result": "Processed test"})

    def test_invalid_dependencies(self):
        # Simulate passing incompatible arguments to the agent
        mock_agent = MagicMock(spec=Agent)
        mock_agent.execute.side_effect = TypeError("Invalid arguments")
        node = AgentNode(name="InvalidNode", agent=mock_agent)

        with self.assertRaises(TypeError):
            node.execute({"unexpected_key": "value"})


if __name__ == "__main__":
    unittest.main()
