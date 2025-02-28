from abc import abstractmethod, ABC

from typing import Any, Dict, List

class Node(ABC):
    def __init__(self, name: str, inputs: Dict[str, str] = None):
        """
        Initialize the Node.

        Args:
            name (str): The unique name of the node.
            inputs (dict): Mapping of input keys to their source outputs (default: None). Currently, only one-to-one mappings are supported.
        """
        self.name = name
        self.inputs = inputs or {}


    def get_parents(self, nodes_list: Dict[str, "Node"]) -> List["Node"]:
        """
        Get the list of parent nodes for this node based on the input mappings.

        Returns:
            List[str]: List of parent nodes for this node.
        """
        parents = []
        for source in self.inputs.values():
            if source not in nodes_list:
                raise ValueError(f"Parent '{source}' for node '{self.name}' does not exist in the workflow.")
            source_node = nodes_list[source]
            parents.append(source_node)
        return parents
      
    
    def get_dependencies(self, nodes_list: Dict[str, "Node"]) -> Dict[str, "Node"]:
        """
        Get the list of dependencies for this node based on the input mappings.

        Returns:
            List[str]: List of dependencies for this node.
        """
        dependencies = {}
        
        for node in self.get_parents(nodes_list):
            dependencies[node.name] = node
            dependencies.update(node.get_dependencies(nodes_list))
        return dependencies
    

    def _resolve_inputs(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve the inputs for this node based on its input mappings.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.

        Returns:
            Dict[str, Any]: Resolved inputs for the agent.
        """
        resolved = {}
        for key, source in self.inputs.items():
            
            try:
                resolved[key] = results[source]
            except KeyError:
                raise KeyError(f"Input '{key}' from source '{source}' cannot be resolved. Check dependencies and outputs.")
        return resolved
    
    @abstractmethod
    def execute(self, results: Dict[str, Any], inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the node by collecting the required arguments from the workflow's `results` and `inputs`.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.
            inputs (Dict[str, Any]): A dictionary containing the inputs for the workflow.

        Returns:
            Dict[str, Any]: The result of executing the node.
        """
        pass
    

    