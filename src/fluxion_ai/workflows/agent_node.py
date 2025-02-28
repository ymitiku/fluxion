""" 
fluxion_ai.workflows.agent_node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module defines the AgentNode class, which represents a node in the workflow graph with explicit input and output definitions. The AgentNode class is used to define the structure of the workflow graph and execute agents
at each node based on the dependencies and inputs provided. The AgentNode class is part of the Fluxion framework and is used to build and execute workflows with multiple agents and dependencies.

The AgentNode class includes the following attributes:
- name: The unique name of the agent node.
- agent: The agent to be executed at
this node.
- dependencies: The list of dependencies for this node.
- inputs: Mapping of input keys to their source outputs (e.g., {"key1": "NodeA"}).
- outputs: List of output keys provided by this node.

The AgentNode class provides methods to resolve inputs, execute the agent, and validate the outputs of the agent execution. The AgentNode class is used in conjunction with the AbstractWorkflow class to build and execute
complex workflows with multiple agents and dependencies.

The AgentNode class is a fundamental component of the Fluxion framework and enables the creation and execution of intelligent workflows with multiple agents and dependencies.

"""

from typing import Dict, Any
from copy import deepcopy
import inspect
from fluxion_ai.core.agents.agent import Agent
from fluxion_ai.workflows.node import Node



class AgentNode(Node):
    """
    Represents a node in the workflow graph with explicit input and output definitions.

    Attributes:
        name (str): The unique name of the agent node.
        agent (Agent): The agent to be executed at this node.
        inputs (Dict[str, str]): Mapping of input keys to their source outputs (e.g., {"key1": "NodeA"}).
        outputs (List[str]): List of output keys provided by this node.
    """

    def __init__(self, name: str, agent: Agent,  inputs: Dict[str, str] = None):
        """
        Initialize the AgentNode.

        Args:
            name (str): The unique name of the agent node.
            agent (Agent): The agent to be executed at this node.
            inputs (dict): Mapping of input keys to their source outputs (default: None). Currently, only one-to-one mappings are supported.
        """
        if not isinstance(agent, Agent):
            raise ValueError(f"The 'agent' attribute must be an instance of Agent. Got {type(agent)} instead.")

        self.name = name
        self.agent = agent
        self.inputs = inputs or {}

    def execute(self, results: Dict[str, Any], inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the agent of this node by collecting the required arguments
        from the workflow's `results` and `inputs`.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.
            inputs (Dict[str, Any]): A dictionary containing the inputs for the workflow.

        Returns:
            Dict[str, Any]: The result of executing the agent.
        """
        execute_inputs = self.get_agent_execute_inputs(results, inputs)
        # Call the agent's `execute` method with filtered arguments
        agent_result = self.agent.execute(**execute_inputs)

        return agent_result
    
    def get_agent_execute_inputs(self, results: Dict[str, Any], inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get the inputs to pass to the agent's `execute` method based on the results and inputs of the workflow.

        Args:
            results (Dict[str, Any]): A dictionary containing the outputs of executed nodes.
            inputs (Dict[str, Any]): A dictionary containing the inputs for the workflow.

        Returns:
            Dict[str, Any]: The filtered inputs to pass to the agent's `execute` method.
        """
        inputs = inputs or {}
        resolved_inputs = self._resolve_inputs(results)


        # Inspect the agent's `execute` method to find supported parameters
        agent_execute_signature = inspect.signature(self.agent.execute)
        supported_params = agent_execute_signature.parameters.keys()
        required_params = [param for param, param_info in agent_execute_signature.parameters.items() if param_info.default == inspect.Parameter.empty]
        # Filter inputs to include only those supported by the agent
        # combined_inputs = {**inputs, **resolved_inputs}
        combined_inputs = deepcopy(resolved_inputs)
        for key, value in inputs.items():
            if key not in combined_inputs:
                combined_inputs[key] = deepcopy(value)
        filtered_inputs = {key: value for key, value in combined_inputs.items() if key in supported_params}

        for required_param in required_params:
            if required_param not in filtered_inputs:
                raise KeyError(f"Required parameter '{required_param}' is missing from the agent inputs.")
            
        return filtered_inputs

    def __repr__(self):
        dependencies = [source for source in self.inputs.values()]
        return f"AgentNode(name={self.name}, agent={self.agent.__class__.__name__}, dependencies={dependencies})"
