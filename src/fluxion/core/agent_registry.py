class AgentRegistry:
    """
    A centralized registry to ensure unique agent names.
    """
    _registry = {}

    @classmethod
    def register_agent(cls, name: str, agent_instance):
        """
        Register an agent in the registry.

        Args:
            name (str): The name of the agent.
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
        Unregister an agent from the registry.

        Args:
            name (str): The name of the agent.
        """
        if name in cls._registry:
            del cls._registry[name]

    @classmethod
    def get_agent(cls, name: str):
        """
        Retrieve an agent by its name.

        Args:
            name (str): The name of the agent.

        Returns:
            Agent: The agent instance, or None if not found.
        """
        return cls._registry.get(name)

    @classmethod
    def list_agents(cls):
        """
        List all registered agents.

        Returns:
            List[str]: A list of all agent names.
        """
        return list(cls._registry.keys())
