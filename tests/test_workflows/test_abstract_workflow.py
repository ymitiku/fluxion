from typing import Dict, Any
import unittest
from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"result": f"Processed {input_data}"}
    
class MockWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(name="Node1", agent=MockAgent("Agent1"))
        node2 = AgentNode(name="Node2", agent=MockAgent("Agent2"), dependencies=[node1])
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
        inputs = {"input_data": "test"}
        results = self.workflow.execute(inputs)
        self.assertIn("Node1", results)
        self.assertIn("Node2", results)
        self.assertEqual(results["Node1"]["result"], "Processed test")
        self.assertEqual(results["Node2"]["result"], "Processed test")

    def test_cycle_detection(self):
        # Add a cycle by making Node1 dependent on Node2
        node1 = self.workflow.nodes.get("Node1")
        node2 = self.workflow.nodes.get("Node2")
        node1.dependencies.append(node2)
        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()

    def test_missing_dependencies(self):
        node3 = AgentNode(name="Node3", agent=MockAgent("Agent3"))
        node4 = AgentNode(name="Node4", agent=MockAgent("Agent4"))
        node3.dependencies.append(node4)  # Node2 not added to the workflow
        self.workflow.add_node(node3)
        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()


if __name__ == "__main__":
    unittest.main()
