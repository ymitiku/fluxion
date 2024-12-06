class Agent:
    """
    Base class for all agents.
    """
    def __init__(self, name: str):
        self.name = name

    def execute(self, input_data):
        """
        Executes the agent logic.

        Args:
            input_data: Input data for the agent.

        Returns:
            The result of the agent execution.
        """
        raise NotImplementedError("Subclasses must implement this method.")

class AgentManager:
    """
    Manages the lifecycle and execution of agents.
    """

    def __init__(self):
        self.agents = {}

    def register_agent(self, name: str, agent: Agent):
        """
        Registers an agent with the manager.

        Args:
            name (str): The name of the agent.
            agent (Agent): The agent instance.
        """
        if name in self.agents:
            raise ValueError(f"Agent with name '{name}' is already registered.")
        self.agents[name] = agent

    def list_agents(self):
        """
        Lists all registered agents.

        Returns:
            list: Names of registered agents.
        """
        return list(self.agents.keys())

    def execute_agent(self, name: str, input_data):
        """
        Executes a registered agent.

        Args:
            name (str): The name of the agent.
            input_data: Input data for the agent.

        Returns:
            The result of the agent execution.
        """
        if name not in self.agents:
            raise ValueError(f"No agent found with name '{name}'.")
        return self.agents[name].execute(input_data)

# Example Agents
class EchoAgent(Agent):
    def execute(self, input_data):
        return f"Echo: {input_data}"

# Example usage
if __name__ == "__main__":
    manager = AgentManager()
    echo_agent = EchoAgent(name="Echo")
    manager.register_agent("echo", echo_agent)

    print(f"Available Agents: {manager.list_agents()}")
    result = manager.execute_agent("echo", "Hello, Fluxion!")
    print(f"Agent Result: {result}")
