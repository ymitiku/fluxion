import pytest
from fluxion.core.agent_manager import AgentManager, Agent

# Define a test agent
class TestAgent(Agent):
    def execute(self, input_data):
        return f"Processed: {input_data}"

def test_register_and_list_agents():
    manager = AgentManager()
    test_agent = TestAgent(name="TestAgent")
    manager.register_agent("test_agent", test_agent)

    # Check if the agent is registered
    assert "test_agent" in manager.list_agents()

def test_execute_agent():
    manager = AgentManager()
    test_agent = TestAgent(name="TestAgent")
    manager.register_agent("test_agent", test_agent)

    # Execute the agent and verify output
    result = manager.execute_agent("test_agent", "InputData")
    assert result == "Processed: InputData"

def test_register_duplicate_agent():
    manager = AgentManager()
    test_agent = TestAgent(name="TestAgent")
    manager.register_agent("test_agent", test_agent)

    # Attempt to register the same agent again
    with pytest.raises(ValueError, match="Agent with name 'test_agent' is already registered."):
        manager.register_agent("test_agent", test_agent)

def test_execute_unregistered_agent():
    manager = AgentManager()

    # Attempt to execute a non-existent agent
    with pytest.raises(ValueError, match="No agent found with name 'non_existent_agent'."):
        manager.execute_agent("non_existent_agent", "InputData")
