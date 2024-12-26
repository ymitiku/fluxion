from typing import Dict, Any
import unittest
from unittest.mock import MagicMock, patch
from fluxion.workflows.flyte_adapter import FlyteWorkflowAdapter, flyte_task, flyte_dynamic_workflow
from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.workflows.agent_node import AgentNode
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry


class MockAgent(Agent):
    def execute(self, inputs: Dict[str, Any]):
        return {"result": f"Processed {inputs}"}


class MockWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(name="Node1", agent=MockAgent("Agent1"))
        node2 = AgentNode(name="Node2", agent=MockAgent("Agent2"), dependencies=[node1])
        self.add_node(node1)
        self.add_node(node2)
        self.initial_inputs = {"key1": "value1"}


class TestFlyteAdapter(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.workflow = MockWorkflow(name="MockWorkflow")
        self.adapter = FlyteWorkflowAdapter(workflow=self.workflow)

    @patch("fluxion.workflows.flyte_adapter.flyte_task")
    @patch("fluxion.workflows.flyte_adapter.flyte_dynamic_workflow")
    def test_generate_flyte_workflow(self, mock_dynamic_workflow, mock_task):
        # Mock the Flyte dynamic workflow and task
        def mock_dynamic_execution(inputs):
            # Simulate dynamic workflow execution based on input
            return {
                "Node1": {"result": "Processed {'key1': 'value1'}"},
                "Node2": {"result": "Processed {'Node1': {'result': 'Processed key1'}}"}
            }
        
        mock_dynamic_workflow.return_value = mock_dynamic_execution
        mock_task.return_value = {"result": "Processed key1"}
    
        flyte_workflow = self.adapter.generate_flyte_workflow()
        self.assertIsNotNone(flyte_workflow)
    
        # Verify the workflow generates Flyte-compatible callable
        inputs = {"key1": "value1"}
        results = flyte_workflow(inputs)  # This should now be callable
        self.assertEqual(results["Node1"]["result"], "Processed {'key1': 'value1'}")
        self.assertEqual(results["Node2"]["result"], "Processed {'Node1': {'result': 'Processed key1'}}")


    def test_execute_flyte_workflow(self):
        # Mock the Flyte workflow's execution
        mock_flyte_workflow = MagicMock()
        mock_flyte_workflow.return_value = {"Node1": {"result": "Processed key1"}, "Node2": {"result": "Processed Node1"}}
        self.adapter.generate_flyte_workflow = MagicMock(return_value=mock_flyte_workflow)

        inputs = {"key1": "value1"}
        results = self.adapter.execute(inputs)

        self.assertEqual(results["Node1"]["result"], "Processed key1")
        self.assertEqual(results["Node2"]["result"], "Processed Node1")

    def test_flyte_task_execution(self):
        # Test the standalone Flyte task for executing an AgentNode
        mock_node_inputs = {"inputs": "inputs_value"}
        mock_workflow = MockWorkflow(name="MockWorkflow")
        mock_workflow.define_workflow()

        node_result = flyte_task(upstream_results = {}, node_inputs=mock_node_inputs, node_name="Node1", workflow=mock_workflow)
        self.assertEqual(node_result["result"], "Processed inputs_value")


if __name__ == "__main__":
    unittest.main()
