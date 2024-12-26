from typing import Dict, Any
from abc import ABC, abstractmethod

from abc import ABC, abstractmethod


class AbstractWorkflow(ABC):
    """
    Abstract base class for workflows.

    Defines the structure for adding nodes, validating dependencies,
    determining execution order, and executing the workflow.
    """

    def __init__(self, name: str):
        """
        Initialize the workflow.

        Args:
            name (str): The name of the workflow.
        """
        self.name = name
        self.nodes = {}

    @abstractmethod
    def define_workflow(self):
        """
        Define the workflow by adding nodes and dependencies.
        Must be implemented in subclasses.
        """
        pass

    def get_node_by_name(self, name):
        """
        Get a node by name.

        Args:
            name (str): The name of the node to retrieve.

        Returns:
            AgentNode: The node with the given name.
        """
        if name not in self.nodes:
            raise ValueError(f"Node '{name}' does not exist in the workflow.")
        return self.nodes[name]

    def add_node(self, node):
        """
        Add a node to the workflow.

        Args:
            node (AgentNode): The node to add.
        """
        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists in the workflow.")
        self.nodes[node.name] = node

    def _validate_dependencies(self):
        """
        Validate the dependencies for all nodes in the workflow.

        Raises:
            ValueError: If a node has an invalid dependency or a circular dependency is detected.
        """
        visited = set()
        stack = set()

        def visit(node_name):
            if node_name in stack:
                raise ValueError(f"Circular dependency detected involving '{node_name}'.")
            if node_name in visited:
                return

            stack.add(node_name)
            visited.add(node_name)

            node = self.nodes.get(node_name)
            node_names = [node.name for node in self.nodes.values()]
            
            if not node:
                raise ValueError(f"Node '{node_name}' does not exist in the workflow.")
            
            for dependency in node.dependencies:
                if dependency.name not in node_names:
                    raise ValueError(f"Dependency '{dependency}' for node '{node_name}' does not exist in the workflow.")
                visit(dependency.name)

            stack.remove(node_name)

        for node_name in self.nodes:
            visit(node_name)

    def determine_execution_order(self):
        """
        Determine the execution order of nodes based on dependencies.

        Returns:
            List[str]: A list of node names in the order they should be executed.
        """
        order = []
        visited = set()

        def dfs(node_name):
            if node_name in visited:
                return
            visited.add(node_name)
            for dependency in self.nodes[node_name].dependencies:
                dfs(dependency.name)
            order.append(node_name)

        for node_name in self.nodes:
            dfs(node_name)

        return order

    def execute(self, inputs=None):
        """
        Execute the workflow.

        Args:
            inputs (dict, optional): A dictionary of inputs for the workflow.

        Returns:
            dict: The results of the workflow execution.
        """
        self._validate_dependencies()
        execution_order = self.determine_execution_order()
        results = {}

        for node_name in execution_order:
            node = self.nodes[node_name]
            
            results[node_name] = node.execute(results=results, inputs=inputs)

        return results
