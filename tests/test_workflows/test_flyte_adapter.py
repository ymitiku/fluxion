from typing import Dict, Any
import unittest
from unittest.mock import MagicMock, patch
from fluxion_ai.workflows.flyte_adapter import FlyteWorkflowAdapter, flyte_task, flyte_dynamic_workflow
from fluxion_ai.workflows.abstract_workflow import AbstractWorkflow
from fluxion_ai.workflows.agent_node import AgentNode
from fluxion_ai.core.agents.agent import Agent
from fluxion_ai.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def execute(self, **inputs: Dict[str, Any]):
        return {"result": f"Processed {inputs}"}


class MockWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(name="Node1", agent=MockAgent("Agent1"), outputs=["result"])
        node2 = AgentNode(name="Node2", agent=MockAgent("Agent2"), dependencies=[node1], outputs=["result"])
        self.add_node(node1)
        self.add_node(node2)
        self.initial_inputs = {"key1": "value1"}


class TestFlyteAdapter(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.workflow = MockWorkflow(name="MockWorkflow")
        self.workflow.define_workflow()
        self.adapter = FlyteWorkflowAdapter(workflow=self.workflow)


    @patch("fluxion_ai.workflows.flyte_adapter.flyte_task")
    @patch("fluxion_ai.workflows.flyte_adapter.flyte_dynamic_workflow")
    def test_generate_flyte_workflow(self, mock_dynamic_workflow, mock_task):
        mock_dynamic_workflow.return_value = lambda inputs: {
            "Node1": {"result": "Processed {'key1': 'value1'}"},
            "Node2": {"result": "Processed {'Node1': {'result': 'Processed key1'}}"}
        }
        mock_task.return_value = {"result": "Processed key1"}

        flyte_workflow = self.adapter.generate_flyte_workflow()
        self.assertIsNotNone(flyte_workflow)

        inputs = {"key1": "value1"}
        results = flyte_workflow(inputs)
        self.assertEqual(results["Node1"]["result"], "Processed {'key1': 'value1'}")
        self.assertEqual(results["Node2"]["result"], "Processed {'Node1': {'result': 'Processed key1'}}")

    def test_execute_flyte_workflow(self):
        mock_flyte_workflow = MagicMock()
        mock_flyte_workflow.return_value = {"Node1": {"result": "Processed key1"}, "Node2": {"result": "Processed Node1"}}
        self.adapter.generate_flyte_workflow = MagicMock(return_value=mock_flyte_workflow)

        inputs = {"key1": "value1"}
        results = self.adapter.execute(inputs)

        self.assertEqual(results["Node1"]["result"], "Processed key1")
        self.assertEqual(results["Node2"]["result"], "Processed Node1")

    def test_flyte_task_execution(self):
        mock_node_inputs = {"inputs": "inputs_value"}
        node_result = flyte_task(upstream_results={}, node_inputs=mock_node_inputs, node_name="Node1", workflow=self.workflow)
        self.assertEqual(node_result["result"], "Processed {'inputs': 'inputs_value'}")

    def test_circular_dependency(self):
        node1 = self.workflow.get_node_by_name("Node1")
        node2 = self.workflow.get_node_by_name("Node2")
        node1.dependencies.append(node2)

        with self.assertRaises(ValueError):
            self.workflow._validate_dependencies()


if __name__ == "__main__":
    unittest.main()
