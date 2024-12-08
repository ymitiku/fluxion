from abc import ABC, abstractmethod
from fluxion.core.agent_registry import AgentRegistry
from fluxion.modules.llm_modules import LLMQueryModule

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



class LLMQueryAgent(Agent):
    """
    An agent that queries an LLM for a response.
    """
    def __init__(self, name: str, llm_module: LLMQueryModule, system_instructions: str = ""):
        """
        Initialize the LLMQueryAgent.

        Args:
            name (str): The unique name of the agent.
            llm_module (LLMQueryModule): The LLMQueryModule module.
            system_instructions (str): System instructions for the agent (default: "").
        """
        self.llm_module = llm_module
        super().__init__(name, system_instructions)

    def execute(self, query: str) -> str:
        """
        Execute the LLM query agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The response from the LLM.
        """
        if query.strip() == "":
            raise ValueError("Invalid query: Empty")
        prompt = self.system_instructions + "\n\n" + query if self.system_instructions else query
        return self.llm_module.execute(prompt=prompt)
    
