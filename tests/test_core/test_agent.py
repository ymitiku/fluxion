import unittest
from unittest.mock import Mock, patch
from fluxion.core.agent import Agent, LLMQueryAgent, LLMChatAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry



class TestAgentBase(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()

    def tearDown(self):
        AgentRegistry.clear_registry()

    def test_agent_registration(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        self.assertIn("TestAgent", AgentRegistry._registry)
        self.assertIs(AgentRegistry.get_agent("TestAgent"), agent)

    def test_agent_unregistration(self):
        class MockAgent(Agent):
            def execute(self, query: str) -> str:
                return "Mock response"

        agent = MockAgent(name="TestAgent")
        agent.cleanup()  # Explicitly call cleanup() instead of relying on __del__
        self.assertNotIn("TestAgent", AgentRegistry._registry)

    def test_abstract_class_instantiation(self):
        with self.assertRaises(TypeError):
            Agent(name="AbstractAgent")  # Abstract class cannot be instantiated


class TestLLMQueryAgent(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()

    def tearDown(self):
        AgentRegistry.clear_registry()

    @patch("fluxion.modules.api_module.requests.post")
    def test_execute_success(self, mock_post):
        # Mock LLMQueryModule response
        mock_post.return_value.json.return_value = {"response": "Paris"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize LLMQueryAgent
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)

        # Execute query
        response = agent.execute(query="What is the capital of France?")
        self.assertEqual(response, "Paris")

        # Verify API interaction
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": "What is the capital of France?", "stream": False},
            headers={},
            timeout=10
        )

    @patch("fluxion.modules.api_module.requests.post")
    def test_execute_with_system_instructions(self, mock_post):
        # Mock LLMQueryModule response
        mock_post.return_value.json.return_value = {"response": "Paris"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize LLMQueryAgent with system instructions
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
        agent = LLMQueryAgent(
            name="LLMQueryAgentWithInstructions",
            llm_module=llm_module,
            system_instructions="These are system instructions."
        )

        # Execute query
        response = agent.execute(query="What is the capital of France?")
        self.assertEqual(response, "Paris")

        # Verify the combined prompt
        combined_prompt = "These are system instructions.\n\nWhat is the capital of France?"
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": combined_prompt, "stream": False},
            headers={},
            timeout=10
        )

    def test_invalid_query(self):
        # Mock LLMQueryModule
        llm_module = Mock(spec=LLMQueryModule)
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)

        # Test with invalid query
        with self.assertRaises(ValueError):
            agent.execute(query="")  # Empty query

    def test_agent_registration(self):
        # Mock LLMQueryModule
        llm_module = Mock(spec=LLMQueryModule)

        # Initialize LLMQueryAgent
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)
        self.assertIn("LLMQueryAgent", AgentRegistry._registry)
        self.assertIs(AgentRegistry.get_agent("LLMQueryAgent"), agent)




class TestLLMChatAgent(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()
        self.mock_llm_module = Mock(spec=LLMChatModule)
        ToolRegistry._registry = {}  # Reset ToolRegistry before each test

        def sample_tool(location: str, format: str = "celsius"):
            """Sample tool function."""
            return f"The current weather in {location} is 20 degrees {format}."

        ToolRegistry.register_tool(sample_tool)
        self.agent = LLMChatAgent(
            name="TestChatAgent",
            llm_module=self.mock_llm_module,
            system_instructions="Provide accurate answers."
        )

    def tearDown(self):
        ToolRegistry._registry = {}  # Reset ToolRegistry after each test

    @patch("fluxion.core.registry.tool_registry.ToolRegistry.invoke_tool_call")
    def test_execute_with_tool_call(self, mock_invoke_tool_call):
        # Mock LLM response with a tool call
        self.mock_llm_module.execute.return_value = {
            "role": "assistant",
            "content": "",
            "tool_call": {
                "function": {
                    "name": "sample_tool",
                    "arguments": {"location": "Paris", "format": "celsius"},
                }
            },
        }

        mock_invoke_tool_call.return_value = "The current weather in Paris is 20 degrees celsius."

        # Execute the agent
        messages = [{"role": "user", "content": "What is the weather in Paris?"}]
        result = self.agent.execute(messages)

        # Verify the result contains the tool response
        self.assertIn(
            {"role": "tool", "content": "The current weather in Paris is 20 degrees celsius."},
            result
        )

        # Verify tool call invocation
        mock_invoke_tool_call.assert_called_once_with(
            {
                "function": {
                    "name": "sample_tool",
                    "arguments": {"location": "Paris", "format": "celsius"},
                }
            }
        )

    def test_execute_with_system_instructions(self):
        # Mock LLM response without a tool call
        self.mock_llm_module.execute.return_value = {
            "role": "assistant",
            "content": "Paris is sunny today."
        }

        messages = [{"role": "user", "content": "What is the weather in Paris?"}]
        result = self.agent.execute(messages)

        # Verify system instructions are added
        self.assertEqual(result[0], {"role": "system", "content": "Provide accurate answers."})

        # Verify LLM response is appended
        self.assertIn({"role": "assistant", "content": "Paris is sunny today."}, result)

    def test_execute_invalid_messages(self):
        # Test with invalid message format
        with self.assertRaises(ValueError):
            self.agent.execute(messages=[{"role": "user"}])  # Missing 'content' key

        with self.assertRaises(ValueError):
            self.agent.execute(messages="Invalid type")  # Not a list


if __name__ == "__main__":
    unittest.main()
