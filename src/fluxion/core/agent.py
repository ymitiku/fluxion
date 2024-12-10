from abc import ABC, abstractmethod
from fluxion.core.registry.agent_registry import AgentRegistry

class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement.
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
    def execute(self, query: str) -> str:
        """
        Execute the agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The result or response from the agent.
        """
        pass

    def __del__(self):
        """
        Unregister the agent when it is deleted.
        """
        self.cleanup()

    def cleanup(self):
        AgentRegistry.unregister_agent(self.name)



