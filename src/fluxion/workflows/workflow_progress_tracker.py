import time
from typing import Dict, List, Any

class WorkflowProgressTracker:
    """
    Tracks the progress of workflow execution.
    """

    def __init__(self, node_names: List[str]):
        """
        Initialize the progress tracker with nodes.

        Args:
            node_names (List[str]): List of all node names in the workflow.
        """
        self.node_status = {node: "Pending" for node in node_names}
        self.node_times = {node: None for node in node_names}
        self.start_time = None

    def start_workflow(self):
        """
        Mark the start of the workflow execution.
        """
        self.start_time = time.time()

    def mark_node_running(self, node_name: str):
        """
        Mark a node as running.

        Args:
            node_name (str): Name of the node.
        """
        if node_name not in self.node_status:
            raise ValueError(f"Node '{node_name}' is not part of the workflow.")
        self.node_status[node_name] = "Running"
        self.node_times[node_name] = time.time()

    def mark_node_completed(self, node_name: str):
        """
        Mark a node as completed and record its execution time.

        Args:
            node_name (str): Name of the node.
        """
        if node_name not in self.node_status:
            raise ValueError(f"Node '{node_name}' is not part of the workflow.")
        if self.node_status[node_name] != "Running":
            raise ValueError(f"Node '{node_name}' was not running.")
        self.node_status[node_name] = "Completed"
        self.node_times[node_name] = time.time() - self.node_times[node_name]

    def get_progress(self) -> Dict[str, Any]:
        """
        Get the current progress of the workflow.

        Returns:
            Dict[str, Any]: Progress details including node status and overall percentage.
        """
        completed_nodes = sum(1 for status in self.node_status.values() if status == "Completed")
        total_nodes = len(self.node_status)
        progress_percentage = (completed_nodes / total_nodes) * 100 if total_nodes > 0 else 0

        return {
            "node_status": self.node_status,
            "node_times": self.node_times,
            "progress_percentage": progress_percentage,
            "elapsed_time": time.time() - self.start_time if self.start_time else None
        }
