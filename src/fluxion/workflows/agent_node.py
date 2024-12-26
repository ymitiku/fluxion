from typing import Dict, Any
from fluxion.core.agent import Agent
import inspect


class AgentNode:
    """
    Represents a node in the workflow graph.

    Attributes:
        name (str): The unique name of the agent node.
        agent (Agent): The agent to be executed at this node.
        dependencies (List[AgentNode]): The list of dependencies for this node.
    """

    def __init__(self, name: str, agent: Agent, dependencies: list = None):
        """
        Initialize the AgentNode.

        Args:
            name (str): The unique name of the agent node.
            agent (Agent): The agent to be executed at this node.
            dependencies (list): List of dependencies for this node (default: None).
        """
        if not isinstance(agent, Agent):
            raise ValueError(f"The 'agent' attribute must be an instance of Agent. Got {type(agent)} instead.")

        self.name = name
        self.agent = agent
        self.dependencies = dependencies or []

    def execute(self, results: Dict[str, Any], inputs: Dict[str, Any]) -> Any:
        """
        Execute the agent of this node by collecting the required arguments
        from the workflow's `results` and `inputs`.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.
            inputs (Dict[str, Any]): A dictionary containing the inputs for the workflow.

        Returns:
            Any: The result of executing the agent.
        """
        # Collect all arguments from results and inputs

        combined_args = inputs.copy()
        for dep in self.dependencies:
            combined_args.update(results[dep.name])


        # Inspect the agent's `execute` method to find supported parameters
        agent_execute_signature = inspect.signature(self.agent.execute)
        supported_params = agent_execute_signature.parameters.keys()
        # Filter arguments to include only those supported by the agent
        filtered_args = {key: value for key, value in combined_args.items() if key in supported_params}
        # Call the agent's `execute` method with filtered arguments
        agent_result = self.agent.execute(**filtered_args)
        return agent_result

    def __repr__(self):
        return f"AgentNode(name={self.name}, agent={self.agent.__class__.__name__}, dependencies={self.dependencies})"
