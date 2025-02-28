from typing import Dict, Any
import unittest
import os
from fluxion_ai.workflows.abstract_workflow import AbstractWorkflow
from fluxion_ai.workflows.agent_node import AgentNode
from fluxion_ai.core.agents.agent import Agent
from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxion_ai.models.message_model import Message, MessageHistory

class MockAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def execute(self, messages: MessageHistory) -> MessageHistory:
        messages = messages.copy()
        messages.append(Message(role="agent", content=f"Processed by {self.name}"))
        return messages


class MockWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(
            name="Node1",
            agent=MockAgent("Agent1"),
        )
        node2 = AgentNode(
            name="Node2",
            agent=MockAgent("Agent2"),
            inputs={"messages": "Node1"},
        )
        nodes3 = AgentNode(
            name="Node3",
            agent=MockAgent("Agent3"),
            inputs={"messages": "Node2"},
        )
        self.add_node(node1)
        self.add_node(node2)
        self.add_node(nodes3)


class TestAbstractWorkflow(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.workflow = MockWorkflow(name="TestWorkflow")
        self.workflow.define_workflow()

    def test_add_node(self):
        self.assertEqual(len(self.workflow.nodes), 3)
        workflow_node_names = [node.name for node in self.workflow.nodes.values()]
        self.assertIn("Node1", workflow_node_names)
        self.assertIn("Node2", workflow_node_names)
        self.assertIn("Node3", workflow_node_names)

    def test_execute_workflow(self):
        inputs = {"messages": MessageHistory(messages = [Message(role="user", content="Hello")])}
        results = self.workflow.execute(inputs)

        print("Results:")
        print(results["Node1"].messages)
        print(results["Node2"].messages)
        print(results["Node3"].messages)

        self.assertIn("Node1", results)
        self.assertIn("Node2", results)
        self.assertEqual(results["Node1"].messages[-1].content, "Processed by Agent1")
        self.assertEqual(results["Node2"].messages[-1].content, "Processed by Agent2")
        self.assertEqual(results["Node2"].messages[-2].content, "Processed by Agent1")


    def test_cycle_detection(self):
        # Add a cycle by making Node1 dependent on Node2
        node1 = self.workflow.nodes.get("Node1")
        node1.inputs = {"messages": "Node2"}
        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()

    def test_missing_dependencies(self):
        node = AgentNode(
            name="Node4",
            agent=MockAgent("Agent4"),
            inputs={"missing_key": "Node5"},
        )
        with self.assertRaises(ValueError):
            self.workflow.add_node(node)

    def test_dependency_resolution(self):
        
        node = AgentNode(
            name="Node4",
            agent=MockAgent("Agent4"),
            inputs={"messages": "Node2"},
        )
        
        self.workflow.add_node(node)
        self.workflow._validate_dependencies()
        print("Node4 dependencies:")
        print(node.get_parents(self.workflow.nodes))
        self.assertEqual(node.get_parents(self.workflow.nodes), [self.workflow.nodes.get("Node2")])

    def test_execution_order(self):
        execution_order = self.workflow.determine_execution_order()
        self.assertEqual(execution_order, ["Node1", "Node2", "Node3"])


    def test_workflow_execution_with_conflicting_keys(self):
        node = AgentNode(
            name="Node3",
            agent=MockAgent("Agent4"),
            inputs={"messages": "Node1"}
        )
        with self.assertRaises(ValueError):
            self.workflow.add_node(node)

    def test_visualize(self):
        output_file = self.workflow.visualize(output_path="test_workflow_graph", format="png")
        self.assertTrue(os.path.exists(output_file))
        os.remove(output_file)  # Clean up after test


if __name__ == "__main__":
    unittest.main()
