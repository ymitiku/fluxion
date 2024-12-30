import unittest
from time import sleep
from fluxion.workflows.workflow_progress_tracker import WorkflowProgressTracker

class TestWorkflowProgressTracker(unittest.TestCase):
    def setUp(self):
        self.nodes = ["Node1", "Node2", "Node3"]
        self.tracker = WorkflowProgressTracker(self.nodes)

    def test_initialization(self):
        self.assertEqual(self.tracker.node_status, {node: "Pending" for node in self.nodes})
        self.assertEqual(self.tracker.node_times, {node: None for node in self.nodes})
        self.assertIsNone(self.tracker.start_time)

    def test_workflow_start(self):
        self.tracker.start_workflow()
        self.assertIsNotNone(self.tracker.start_time)

    def test_mark_node_running_and_completed(self):
        self.tracker.start_workflow()
        self.tracker.mark_node_running("Node1")
        self.assertEqual(self.tracker.node_status["Node1"], "Running")
        self.assertIsNotNone(self.tracker.node_times["Node1"])

        sleep(0.1)
        self.tracker.mark_node_completed("Node1")
        self.assertEqual(self.tracker.node_status["Node1"], "Completed")
        self.assertGreater(self.tracker.node_times["Node1"], 0)

    def test_get_progress(self):
        self.tracker.start_workflow()
        self.tracker.mark_node_running("Node1")
        sleep(0.1)
        self.tracker.mark_node_completed("Node1")

        progress = self.tracker.get_progress()
        self.assertEqual(progress["node_status"]["Node1"], "Completed")
        self.assertEqual(progress["progress_percentage"], (1 / len(self.nodes)) * 100)
        self.assertGreater(progress["elapsed_time"], 0)

    def test_invalid_node(self):
        with self.assertRaises(ValueError):
            self.tracker.mark_node_running("InvalidNode")

        with self.assertRaises(ValueError):
            self.tracker.mark_node_completed("InvalidNode")

if __name__ == "__main__":
    unittest.main()
