"""
fluxion.core.agent
~~~~~~~~~~~~~~~~~~

Defines the `Agent` class, which serves as the base class for agents in the Fluxion framework.

Agents represent intelligent components that can execute tasks, process inputs, and interact with the environment.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from fluxion.core.registry.agent_registry import AgentRegistry


class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement.

    Attributes:
        name (str): The unique name of the agent.
        system_instructions (str): System instructions for the agent.
    """

    def __init__(self, name: str, system_instructions: str = ""):
        """
        Initialize the agent and register it.

        Args:
            name (str): The unique name of the agent.
            system_instructions (str): System instructions for the agent (default: "").

        Raises:
            ValueError: If the name is not unique.
        """
        self.name = name
        self.system_instructions = system_instructions
        AgentRegistry.register_agent(name, self)

    @abstractmethod
    def execute(self, **kwargs: Dict[str, Any]) -> str:
        """
        Execute the agent logic.

        This method must be implemented by subclasses.

        Args:
            **kwargs (Dict[str, Any]): Arbitrary keyword arguments for task execution.

        Returns:
            str: The result or response from the agent.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        pass

    def __del__(self):
        """
        Unregister the agent when it is deleted.
        """
        self.cleanup()

    def cleanup(self):
        """
        Unregister the agent from the registry.
        """
        AgentRegistry.unregister_agent(self.name)
