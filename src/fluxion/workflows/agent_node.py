from typing import Dict, Any, List
from fluxion.core.agent import Agent
import inspect
import logging

logger = logging.getLogger(__name__)

class AgentNode:
    """
    Represents a node in the workflow graph.

    Attributes:
        name (str): The unique name of the agent node.
        agent (Agent): The agent to be executed at this node.
        dependencies (List[AgentNode]): The list of dependencies for this node.
    """

    def __init__(self, name: str, agent: Agent, dependencies: List['AgentNode'] = None):
        """
        Initialize the AgentNode.

        Args:
            name (str): The unique name of the agent node.
            agent (Agent): The agent to be executed at this node.
            dependencies (list): List of dependencies for this node (default: None).
        """
        if not isinstance(agent, Agent):
            raise ValueError(f"The 'agent' attribute must be an instance of Agent. Got {type(agent)} instead.")
        if dependencies and not all(isinstance(dep, AgentNode) for dep in dependencies):
            raise ValueError("All dependencies must be instances of AgentNode.")
        if dependencies and self in dependencies:
            raise ValueError(f"Node '{name}' cannot depend on itself.")

        self.name = name
        self.agent = agent
        self.dependencies = dependencies or []

    def execute(self, results: Dict[str, Any], inputs: Dict[str, Any] = None) -> Any:
        """
        Execute the agent of this node by collecting the required arguments
        from the workflow's `results` and `inputs`.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.
            inputs (Dict[str, Any]): A dictionary containing the inputs for the workflow.

        Returns:
            Any: The result of executing the agent.
        """
        inputs = inputs or {}

        # Collect all arguments from results and inputs

        combined_args = inputs.copy()
        for dep in self.dependencies:
            if dep.name not in results:
                raise KeyError(f"Dependency '{dep.name}' has not been executed yet.")
            combined_args.update(results[dep.name])


        # Inspect the agent's `execute` method to find supported parameters
        agent_execute_signature = inspect.signature(self.agent.execute)
        supported_params = agent_execute_signature.parameters.keys()
        # Filter arguments to include only those supported by the agent
        filtered_args = {key: value for key, value in combined_args.items() if key in supported_params}

        logger.info(f"Executing node '{self.name}' with arguments: {filtered_args}")

        # Call the agent's `execute` method with filtered arguments
        return self.agent.execute(**filtered_args)

    def __repr__(self):
        return f"AgentNode(name={self.name}, agent={self.agent.__class__.__name__}, dependencies={self.dependencies})"
