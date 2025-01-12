from typing import Dict, Any
import unittest
import os
from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agents.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry

class MockAgent(Agent):
    def __init__(self, output_key: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_key = output_key
    def execute(self, optional_param: str = None) -> Dict[str, Any]:
        result = {"optional_param": optional_param} if optional_param else {}
        return {self.output_key: f"Processed {result}"}


class MockWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(
            name="Node1",
            agent=MockAgent("result", "Agent1"),
            outputs=["result"]
        )
        node2 = AgentNode(
            name="Node2",
            agent=MockAgent("result", "Agent2"),
            dependencies=[node1],
            inputs={"optional_param": "Node1.result"},
            outputs=["result"]
        )
        self.add_node(node1)
        self.add_node(node2)


class TestAbstractWorkflow(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.workflow = MockWorkflow(name="TestWorkflow")
        self.workflow.define_workflow()

    def test_add_node(self):
        self.assertEqual(len(self.workflow.nodes), 2)
        workflow_node_names = [node.name for node in self.workflow.nodes.values()]
        self.assertIn("Node1", workflow_node_names)
        self.assertIn("Node2", workflow_node_names)

    def test_execute_workflow(self):
        inputs = {"random_input": "test_value"}
        results = self.workflow.execute(inputs)

        self.assertIn("Node1", results)
        self.assertIn("Node2", results)
        self.assertEqual(results["Node1"]["result"], "Processed {}")
        self.assertEqual(results["Node2"]["result"], "Processed {'optional_param': 'Processed {}'}")

    def test_cycle_detection(self):
        # Add a cycle by making Node1 dependent on Node2
        node1 = self.workflow.nodes.get("Node1")
        node2 = self.workflow.nodes.get("Node2")
        node1.dependencies.append(node2)
        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()

    def test_missing_dependencies(self):
        node3 = AgentNode(
            name="Node3",
            agent=MockAgent("result", "Agent3"),
            inputs={"missing_key": "Node4.output"}
        )
        self.workflow.add_node(node3)
        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()

    def test_dependency_resolution(self):
        node1 = self.workflow.nodes.get("Node1")
        node2 = self.workflow.nodes.get("Node2")
        dependency = node2.inputs["optional_param"]
        self.assertEqual(dependency, "Node1.result")

    def test_execution_order(self):
        execution_order = self.workflow.determine_execution_order()
        self.assertEqual(execution_order, ["Node1", "Node2"])

    def test_workflow_with_missing_inputs(self):
        class MockAgentWithRequiredInput(Agent):
            def execute(self, required_input: str) -> Dict[str, Any]:
                return {"result": f"Processed {required_input}"}

        inputs = {}  # Missing input for Node2
        node1  = self.workflow.nodes.get("Node1")
        node1.agent = MockAgentWithRequiredInput("Agent3")
        with self.assertRaises(KeyError):
            self.workflow.execute(inputs)

    def test_workflow_execution_with_conflicting_keys(self):
        inputs = {"Node1.output1": "value_from_inputs", "optional_param": "conflict_value"}
        results = self.workflow.execute(inputs)
        self.assertEqual(results["Node2"]["result"], "Processed {'optional_param': \"Processed {'optional_param': 'conflict_value'}\"}")


    def test_visualize(self):
        output_file = self.workflow.visualize(output_path="test_workflow_graph", format="png")
        self.assertTrue(os.path.exists(output_file))
        os.remove(output_file)  # Clean up after test


if __name__ == "__main__":
    unittest.main()
