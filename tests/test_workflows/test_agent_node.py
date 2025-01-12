from typing import Dict, Any
import unittest
from unittest.mock import MagicMock
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agents.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def __init__(self, output_key: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_key = output_key

    def execute(self, first_input: str, second_input:str = None) -> Dict[str, Any]:
        result = {"first_input": first_input}
        if second_input:
            result["second_input"] = second_input
        return {self.output_key: f"Processed {result}"}


class TestAgentNode(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.mock_agent = MockAgent(output_key="result", name="MockAgent")
        self.node = AgentNode(name="TestNode", agent=self.mock_agent, inputs={"first_input": "DependencyNode.output1"}, outputs=["result"])

    def test_execute_node_with_valid_inputs(self):
        """Test executing a node with valid inputs and no dependencies."""
        inputs = {"DependencyNode": {"output1": "value1"}}
        results = self.node.execute(inputs={}, results=inputs)
        self.assertEqual(results, {"result": "Processed {'first_input': 'value1'}"})

    def test_execute_with_dependency_results(self):
        """Test executing a node with inputs resolved from dependencies."""
        dependency_node = AgentNode(
            name="DependencyNode", 
            agent=self.mock_agent, 
            outputs=["result"]
        )
        dependency_results = {"DependencyNode": {"output1": "dependency_value"}}
        inputs = {}

        self.node.dependencies.append(dependency_node)
        results = self.node.execute(inputs=inputs, results=dependency_results)
        self.assertEqual(results, {"result": "Processed {'first_input': 'dependency_value'}"})

    def test_execute_with_missing_dependency(self):
        """Test behavior when a required dependency result is missing."""
        dependency_node = AgentNode(
            name="MissingDependency",
            agent=self.mock_agent,
            outputs=["output1"]
        )
        self.node.dependencies.append(dependency_node)

        inputs = {}
        with self.assertRaises(KeyError):
            self.node.execute(inputs=inputs, results={})

    def test_execute_with_filtered_arguments(self):
        """Test that only supported arguments are passed to the agent."""
        class CustomAgent(Agent):
            def execute(self, supported_key: str):
                return {"result": f"Processed {supported_key}"}

        custom_agent = CustomAgent(name="CustomAgent")
        node = AgentNode(
            name="CustomNode", 
            agent=custom_agent, 
            inputs={"supported_key": "DependencyNode.output1"}, outputs=["result"]
        )
        dependency_results = {"DependencyNode": {"output1": "filtered_value"}}

        results = node.execute(inputs={}, results=dependency_results)
        self.assertEqual(results, {"result": "Processed filtered_value"})

    def test_execute_without_inputs_or_dependencies(self):
        """Test executing a node without inputs or dependencies."""
        class NoInputAgent(Agent):
            def execute(self):
                return {"result": "Processed {}"}
        self.node.agent = NoInputAgent(name="NoInputAgent")
        self.node.inputs = {}
        results = self.node.execute(inputs={}, results={})
        self.assertEqual(results, {"result": "Processed {}"})

    def test_missing_inputs_handling(self):
        """Test behavior when required inputs are missing."""
        self.node.inputs = {"first_input": "DependencyNode.output1"}
        with self.assertRaises(KeyError):
            self.node.execute(inputs={}, results={})

    def test_repr_method(self):
        """Test the string representation of the node."""
        repr_output = repr(self.node)
        self.assertIn("AgentNode", repr_output)
        self.assertIn("MockAgent", repr_output)

    def test_execute_with_conflicting_input_names(self):
        """Test behavior when inputs have conflicting keys from results."""
        node = AgentNode(
            name="ConflictNode",
            agent=self.mock_agent,
            inputs={"first_input": "DependencyNode.output1"},
            outputs=["result"]
        )
        dependency_node = AgentNode(
            name="DependencyNode",
            agent=self.mock_agent,
            outputs=["output1"]
        )
        dependency_results = {"DependencyNode": {"output1": "dependency_value"}}
        inputs = {"first_input": "input_value"}

        node.dependencies.append(dependency_node)
        node.inputs = {"first_input": "DependencyNode.output1"}
        results = node.execute(inputs=inputs, results=dependency_results)
        self.assertEqual(results, {"result": "Processed {'first_input': 'dependency_value'}"})


if __name__ == "__main__":
    unittest.main()
