from typing import Any, Dict, List
import logging
class AgentRegistry:
    """
    A centralized registry for managing agents with modular names.

    AgentRegistry:
    example-usage::
        from fluxion_ai.core.registry.agent_registry import AgentRegistry
        from fluxion_ai.core.agents.agent import Agent

        class MyAgent(Agent):
            def __init__(self, name: str, description: str):
                super().__init__(name, description=description)

        agent = MyAgent(name="MyAgent", description="My first agent")
        AgentRegistry.register_agent("my_module.MyAgent", agent)

        # Retrieve the agent
        agent = AgentRegistry.get_agent("my_module.MyAgent")
        print(agent)

        # List all registered agents
        agents = AgentRegistry.list_agents()
        print(agents)

        # Clear the agent registry
        AgentRegistry.clear_registry()
    """
    _registry = {}

    @classmethod
    def register_agent(cls, name: str, agent_instance: "Agent"):
        """
        Register an agent with a modular name.

        Args:
            name (str): The modular name of the agent (e.g., "ml_agent.feature_extraction.ImageFeatureExtraction").
            agent_instance (Agent): The agent instance.

        Raises:
            ValueError: If the name is already registered.
        """
        if name in cls._registry:
            raise ValueError(f"Agent name '{name}' is already registered.")
        cls._registry[name] = agent_instance

    @classmethod
    def unregister_agent(cls, name: str):
        """
        Unregister an agent by its modular name.

        Args:
            name (str): The modular name of the agent.
        """
        if name in cls._registry:
            cls._registry.pop(name)

    @classmethod
    def get_agent(cls, name: str) -> "Agent":
        """
        Retrieve an agent by its modular name.

        Args:
            name (str): The modular name of the agent.

        Returns:
            Agent: The agent instance, or None if not found.
        """
        return cls._registry.get(name)

    @classmethod
    def list_agents(cls, group: str = None) -> List[str]:
        """
        List all registered agents, optionally filtered by a group prefix.

        Args:
            group (str, optional): A group prefix to filter agents (e.g., "ml_agent.feature_extraction").

        Returns:
            List[str]: A list of agent names matching the group prefix.
        """
        if group:
            prefix = group + "."
            return [name for name in cls._registry if name.startswith(prefix)]
        return list(cls._registry.keys())

    @classmethod
    def clear_registry(cls):
        """
        Clear the agent registry.
        """
        cls._registry.clear()

    @classmethod
    def group_tree(cls) -> Dict[str, Any]:
        """
        Generate a hierarchical representation of registered agents based on their modular names.

        Returns:
            dict: A nested dictionary representing the hierarchy of agents.
        """
        tree = {}
        for name in cls._registry:
            parts = name.split(".")
            current = tree
            for part in parts:
                current = current.setdefault(part, {})
        return tree
  
    
    @classmethod
    def get_agent_metadata(cls, group: str = None, sort: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve metadata for all registered agents.

        Args:
            group (str, optional): The group prefix to filter agents. If None, retrieves all agents.

        Returns:
            Dict[str, Any]: A dictionary containing metadata for all agents.
        """
        agent_metadata = []
        for agent_name in cls.list_agents(group):
            agent = cls._registry.get(agent_name)
            if agent and hasattr(agent, "metadata"):
                try:
                    agent_metadata.append(agent.metadata())
                except Exception as e:
                    logging.warning(f"Failed to get metadata for agent '{agent_name}': {e}")
        if sort:
            agent_metadata = sorted(agent_metadata, key=lambda x: x.get("name", ""))
        return agent_metadata

