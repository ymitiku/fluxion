from typing import Dict, List, Any
from abc import ABC, abstractmethod
from fluxion.workflows.agent_node import AgentNode
from graphviz import Digraph



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
        self._nodes: Dict[str, AgentNode] = {}
        self.initial_inputs = {}

    @property
    def nodes(self):
        return self._nodes
    
    @nodes.setter
    def nodes(self, nodes):
        raise ValueError("Cannot set nodes directly. Use add_node method instead.")

    @abstractmethod
    def define_workflow(self):
        """
        Define the workflow by adding nodes and dependencies.
        Must be implemented in subclasses.
        """
        pass

    def get_node_by_name(self, name: str):
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
        for dependency in node.dependencies:
            if dependency.name not in self.nodes:
                raise ValueError(f"Dependency '{dependency.name}' for node '{node.name}' does not exist.")
        self.nodes[node.name] = node

    def _validate_dependencies(self):
        """
        Validate the dependencies for all nodes in the workflow.

        Raises:
            ValueError: If a node has an invalid dependency or a circular dependency is detected.
        """
        if not self.nodes:
            raise ValueError("Workflow has no nodes to validate.")

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
            node_names = [n.name for n in self.nodes.values()]

            if not node:
                raise ValueError(f"Node '{node_name}' does not exist in the workflow.")
            for dependency in node.dependencies:
                if dependency.name not in node_names:
                    raise ValueError(
                        f"Dependency '{dependency.name}' for node '{node_name}' does not exist. "
                        f"Available nodes: {node_names}"
                    )
                if not isinstance(dependency, AgentNode):
                    raise ValueError(f"Dependency '{dependency}' is not a valid AgentNode.")

                visit(dependency.name)

            stack.remove(node_name)

        for node_name in self.nodes:
            visit(node_name)

        for node in self.nodes.values():
            for input_key, source in node.inputs.items():
                node_name, output_name = source.split(".")
                if node_name not in self.nodes:
                    raise ValueError(f"Input '{input_key}' references non-existent node '{node_name}'.")
                if output_name not in self.nodes[node_name].outputs:
                    raise ValueError(f"Input '{input_key}' references non-existent output '{output_name}' in node '{node_name}'.")
    
    def _validate_inputs_and_outputs(self):
        """
        Validate that all inputs and outputs in the workflow are consistent.

        Raises:
            ValueError: If inputs reference non-existent outputs or there are missing inputs.
        """
        available_outputs = set(self.initial_inputs.keys())

        for node in self.nodes.values():
            # Check if inputs are resolved
            for input_key, source in node.inputs.items():
                node_name, output_name = source.split(".")
                if node_name not in self.nodes and node_name != "workflow_input":
                    raise ValueError(f"Input '{input_key}' references non-existent node '{node_name}'.")
                if node_name != "workflow_input" and output_name not in self.nodes[node_name].outputs:
                    raise ValueError(f"Input '{input_key}' references non-existent output '{output_name}' in node '{node_name}'.")
            
            # Add this node's outputs to available outputs
            available_outputs.update(f"{node.name}.{output}" for output in node.outputs)



    def determine_execution_order(self) -> List[str]:
        """
        Determine the execution order of nodes based on dependencies.

        Returns:
            List[str]: A list of node names in the order they should be executed.
        """
        if not self.nodes:
            raise ValueError("Workflow has no nodes to determine execution order.")

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

    def execute(self, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow.

        Args:
            inputs (Dict[str, Any], optional): Inputs for the workflow.

        Returns:
            Dict[str, Any]: Results of the workflow execution.
        """
        self._validate_dependencies()
        self._validate_inputs_and_outputs()
        execution_order = self.determine_execution_order()

        results = {}
        for node_name in execution_order:
            node = self.nodes[node_name]
            results[node_name] = node.execute(results=results, inputs=inputs)

        return results


    def visualize(self, output_path: str = "workflow_graph", format: str = "png"):
        """
        Visualizes the workflow as a directed graph.

        Args:
            output_path (str): The output path for the generated graph (without extension).
            format (str): The format of the output file (e.g., 'png', 'pdf').

        Returns:
            str: Path to the generated visualization file.
        """
        dot = Digraph(name=self.name, format=format)
        dot.attr(rankdir='LR')

        # Add nodes to the graph
        for node in self.nodes.values():
            dot.node(node.name, label=node.name)

        # Add edges to represent dependencies
        for node in self.nodes.values():
            for dependency in node.dependencies:
                dot.edge(dependency.name, node.name)

        # Render the graph
        output_file = dot.render(filename=output_path, cleanup=True)
        print(f"Workflow visualization saved to: {output_file}")
        return output_file