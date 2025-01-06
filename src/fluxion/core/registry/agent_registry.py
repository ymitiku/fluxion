class AgentRegistry:
    """
    A centralized registry for managing agents with modular names.
    """
    _registry = {}

    @classmethod
    def register_agent(cls, name: str, agent_instance):
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
    def get_agent(cls, name: str):
        """
        Retrieve an agent by its modular name.

        Args:
            name (str): The modular name of the agent.

        Returns:
            Agent: The agent instance, or None if not found.
        """
        return cls._registry.get(name)

    @classmethod
    def list_agents(cls, group: str = None):
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
    def group_tree(cls):
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
