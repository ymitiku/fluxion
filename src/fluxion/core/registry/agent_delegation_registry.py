from typing import Any, Dict, List
from .agent_registry import AgentRegistry

class AgentDelegationRegistry:
    """
    A registry for managing delegated tasks and their metadata.
    """
    def __init__(self):
        self._registry = {}

    def add_delegation(self, agent_name: str, task_description: str):
        """
        Adds a delegation entry for a specific agent.

        Args:
            agent_name (str): The name of the agent.
            task_description (str): Description of the task.

        Raises:
            ValueError: If the agent is already registered.
        """
        if agent_name in self._registry:
            raise ValueError(f"Agent '{agent_name}' already has a delegated task.")
        agent = AgentRegistry.get_agent(agent_name)
        if agent is None:
            raise ValueError(f"Agent '{agent_name}' is not registered.")
        agent_metadata = agent.metadata()
        self._registry[agent_name] = {
            "task_description": task_description,
            "agent_metadata": agent_metadata
        }

    def get_delegation(self, agent_name: str) -> Dict[str, Any]:
        """
        Retrieves the delegation entry for a specific agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            Dict[str, Any]: The delegation entry.

        Raises:
            KeyError: If the agent is not registered.
        """
        if agent_name not in self._registry:
            raise KeyError(f"No delegation found for agent '{agent_name}'.")
        return self._registry[agent_name]

    def list_delegations(self) -> List[Dict[str, Any]]:
        """
        Lists all delegations in the registry.

        Returns:
            List[Dict[str, Any]]: A list of all delegation entries.
        """
        return list(self._registry.items())
    


    def remove_delegation(self, agent_name: str):
        """
        Removes a delegation entry for a specific agent.

        Args:
            agent_name (str): The name of the agent.

        Raises:
            KeyError: If the agent is not registered.
        """
        if agent_name not in self._registry:
            raise KeyError(f"No delegation found for agent '{agent_name}'.")
        del self._registry[agent_name]

    def clear_registry(self):
        """
        Clears all delegations from the registry.
        """
        self._registry.clear()
