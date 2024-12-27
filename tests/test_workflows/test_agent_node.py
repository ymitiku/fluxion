from typing import Dict, Any
import unittest
from unittest.mock import MagicMock
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def execute(self, **input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": f"Processed {input_data}"}


class TestAgentNode(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.mock_agent = MockAgent(name="MockAgent")
        self.node = AgentNode(name="TestNode", agent=self.mock_agent)

    def test_execute_node_with_inputs(self):
        """Test executing a node with valid inputs."""
        inputs = {"input_data": "test"}
        results = self.node.execute(results={}, inputs=inputs)
        self.assertEqual(results, {"result": "Processed {'input_data': 'test'}"})

    def test_execute_with_dependencies(self):
        """Test executing a node with dependencies."""
        dependency_node = AgentNode(name="DependencyNode", agent=self.mock_agent)
        dependency_results = {"DependencyNode": {"result": "Processed dependency"}}
        self.node.dependencies.append(dependency_node)

        inputs = {"input_data": "test"}
        results = self.node.execute(inputs=inputs, results=dependency_results)
        self.assertEqual(results, {"result": "Processed {'input_data': 'test'}"})

    def test_missing_dependency_result(self):
        """Test behavior when a dependency's result is missing."""
        dependency_node = AgentNode(name="MissingDependency", agent=self.mock_agent)
        self.node.dependencies.append(dependency_node)

        inputs = {"input_data": "test"}
        with self.assertRaises(KeyError):
            self.node.execute(inputs=inputs, results={})


    def test_execute_with_unsupported_arguments(self):
        """Test handling of unsupported arguments."""
        mock_agent = MagicMock(spec=Agent)
        mock_agent.execute.side_effect = TypeError("Unsupported arguments")
        node = AgentNode(name="InvalidNode", agent=mock_agent)

        inputs = {"unsupported_key": "value"}
        with self.assertRaises(TypeError):
            node.execute(inputs=inputs, results={})

    def test_execute_with_filtered_arguments(self):
        """Test that only supported arguments are passed to the agent."""
        class CustomAgent(Agent):
            def execute(self, supported_key: str):
                return {"result": f"Processed {supported_key}"}

        custom_agent = CustomAgent(name="CustomAgent")
        node = AgentNode(name="CustomNode", agent=custom_agent)

        inputs = {"supported_key": "value", "unsupported_key": "value"}
        results = node.execute(inputs=inputs, results={})
        self.assertEqual(results, {"result": "Processed value"})

    def test_execute_without_inputs_or_dependencies(self):
        """Test executing a node without inputs or dependencies."""
        results = self.node.execute(inputs={}, results={})
        self.assertEqual(results, {"result": "Processed {}"})

    def test_repr_method(self):
        """Test the string representation of the node."""
        repr_output = repr(self.node)
        self.assertIn("AgentNode", repr_output)
        self.assertIn("MockAgent", repr_output)


if __name__ == "__main__":
    unittest.main()
