from typing import Dict, Any
import unittest
from unittest.mock import MagicMock
from fluxion_ai.workflows.agent_node import AgentNode
from fluxion_ai.core.agents.agent import Agent
from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxion_ai.models.message_model import Message, MessageHistory


class MockAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, messages: MessageHistory) -> MessageHistory:
        messages = messages.copy()
        messages.append(Message(role="assistant", content=f"Processed by {self.name}"))
        return messages

class TestAgentNode(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.mock_agent = MockAgent(name="MockAgent")
        self.node = AgentNode(name="TestNode", agent=self.mock_agent, inputs={"messages": "DependencyNode"})

    def test_execute_node_with_valid_inputs(self):
        """Test executing a node with valid inputs and no dependencies."""
        inputs = {"DependencyNode": MessageHistory(messages=[Message(role="user", content="Output from Node1")])}
        results = self.node.execute(inputs={}, results=inputs)
        self.assertEqual(results[-1].content, "Processed by MockAgent")
        self.assertEqual(results[-2].content, "Output from Node1")

    def test_execute_with_dependency_results(self):
        """Test executing a node with inputs resolved from dependencies."""
        dependency_node = AgentNode(
            name="DependencyNode", 
            agent=self.mock_agent, 
        )
        dependency_results = {"DependencyNode": MessageHistory(messages=[Message(role="assistant", content="dependency_value")])}
        inputs = {}

        results = self.node.execute(inputs=inputs, results=dependency_results)
        self.assertEqual(results[-1].content, "Processed by MockAgent")
        self.assertEqual(results[-2].content, "dependency_value")


    def test_execute_with_missing_dependency(self):
        """Test behavior when a required dependency result is missing."""
        dependency_node = AgentNode(
            name="MissingDependency",
            agent=self.mock_agent,
        )
        
        inputs = {}
        self.node.inputs = {"messages": "MissingDependency"}
        with self.assertRaises(KeyError):
            self.node.execute(inputs=inputs, results={})

    def test_execute_with_filtered_arguments(self):
        """Test that only supported arguments are passed to the agent."""
        class CustomAgent(Agent):
            def execute(self, messages: MessageHistory, supported_key: str) -> Message:
                messages = messages.copy()
                messages.append(Message(role="assistant", content=f"Processed by {self.name} with {supported_key}"))
                return messages


        custom_agent = CustomAgent(name="CustomAgent")
        node = AgentNode(
            name="CustomNode", 
            agent=custom_agent, 
            inputs={"messages": "DependencyNode"}
        )
        dependency_results = {"DependencyNode": MessageHistory(messages=[Message(role="assistant", content="filtered_value")])}

        results = node.execute(inputs={"supported_key": "Supported key"}, results=dependency_results)
        self.assertEqual(results[-1], Message(role="assistant", content="Processed by CustomAgent with Supported key"))
        self.assertEqual(results[-2], Message(role="assistant", content="filtered_value"))

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
        self.node.inputs = {"first_input": "DependencyNode", "second_input": "MissingDependency"}
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
            inputs={"messages": "DependencyNode"},
        )
        dependency_node = AgentNode(
            name="DependencyNode",
            agent=self.mock_agent,
        )
        dependency_results = {"DependencyNode": MessageHistory(messages=[Message(role="assistant", content="dependency_value")])}
        inputs = {"messages": MessageHistory(messages=[Message(role="user", content="Conflict value")])}

        node.inputs = {"messages": "DependencyNode"}
        results = node.execute(inputs=inputs, results=dependency_results)
     
        self.assertEqual(results[-1].content, "Processed by MockAgent")
        self.assertEqual(results[-2].content, "dependency_value")


if __name__ == "__main__":
    unittest.main()
