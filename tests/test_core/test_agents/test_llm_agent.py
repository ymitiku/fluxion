

import unittest
from unittest.mock import Mock, patch, MagicMock

from fluxion.core.agents.llm_agent import LLMQueryAgent, LLMChatAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry



def example_tool(param1: str):
    return f"Processed {param1}"

class TestLLMQueryAgent(unittest.TestCase):
    def setUp(self):
        AgentRegistry.clear_registry()

    def tearDown(self):
        AgentRegistry.clear_registry()

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_execute_success(self, mock_post):
        # Mock LLMQueryModule response
        mock_post.return_value.json.return_value = {"response": "Paris"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize LLMQueryAgent
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)

        # Execute query
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        response = agent.execute(messages=messages)[-1]["content"]
        self.assertEqual(response, "Paris")

        # Verify API interaction
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": "user: What is the capital of France?", "stream": False},
            headers={},
            timeout=10
        )

    @patch("fluxion.core.modules.api_module.requests.post")
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
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        response = agent.execute(messages=messages)[-1]["content"]
        self.assertEqual(response, "Paris")

        # Verify the combined prompt
        combined_prompt = "These are system instructions.\n\nuser: What is the capital of France?"
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": combined_prompt, "stream": False},
            headers={},
            timeout=10
        )

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_execute_with_seeds_and_temperature(self, mock_post):
        # Mock LLMQueryModule response
        mock_post.return_value.json.return_value = {"response": "Paris"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize LLMQueryAgent with seeds and temperature
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2", seed=123, temperature=0.5)
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)

        # Execute query
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        response = agent.execute(messages=messages)[-1]["content"]
        self.assertEqual(response, "Paris")

        # Verify API interaction
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": "user: What is the capital of France?", "stream": False, "seed": 123, "temperature": 0.5},
            headers={},
            timeout=10
        )

    def test_invalid_query(self):
        # Mock LLMQueryModule
        llm_module = Mock(spec=LLMQueryModule)
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)

        # Test with invalid query
        with self.assertRaises(ValueError):
            agent.execute(messages=[])  # Empty query

        with self.assertRaises(ValueError):
            agent.execute(messages=[{"role": "user"}])
        
        with self.assertRaises(ValueError):
            agent.execute(messages=[{"role": "user", "content": ""}])
        with self.assertRaises(ValueError):
            agent.execute(messages=[{"role": "non_existent", "content": "Invalid role"}])

    def test_agent_registration(self):
        # Mock LLMQueryModule
        llm_module = Mock(spec=LLMQueryModule)

        # Initialize LLMQueryAgent
        agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_module)
        self.assertIn("LLMQueryAgent", AgentRegistry.list_agents())
        self.assertIs(AgentRegistry.get_agent("LLMQueryAgent"), agent)

class TestLLMChatAgent(unittest.TestCase):

    def setUp(self):
        self.mock_llm_module = MagicMock(spec=LLMChatModule)
        self.agent = LLMChatAgent(name="TestAgent", llm_module=self.mock_llm_module, max_tool_call_depth=2)
        AgentRegistry.clear_registry()

    def test_register_and_invoke_tool(self):

        self.agent.tool_registry.register_tool(example_tool)
        tool_call = {
            "function": {
                "name": "test_llm_agent.example_tool",
                "arguments": {"param1": "data"}
            }
        }

        result = self.agent.tool_registry.invoke_tool_call(tool_call)
        self.assertEqual(result, "Processed data")

    def test_tool_registry_with_duplicate_tool_name(self):


        self.agent.tool_registry.register_tool(example_tool)

        with self.assertRaises(ValueError):
            self.agent.tool_registry.register_tool(example_tool)  # Registering the same tool should raise an error

    def test_execute_with_single_tool_call(self):
        self.mock_llm_module.execute.return_value = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "test_llm_agent.example_tool", "arguments": {"param1": "data"}}}
            ]
        }

        self.agent.tool_registry.register_tool(example_tool)

        messages = [{"role": "user", "content": "What is the result?"}]
        result = self.agent.execute(messages)

        self.assertIn("Processed data", result[-1]["content"])

    def test_execute_with_multiple_tool_calls(self):
        self.mock_llm_module.execute.side_effect = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "test_llm_agent.example_tool", "arguments": {"param1": "data"}}}
                ]
            },
            {"role": "assistant", "content": "Final response."}
        ]

        self.agent.tool_registry.register_tool(example_tool)

        messages = [{"role": "user", "content": "What is the result?"}]
        result = self.agent.execute(messages)

        self.assertIn("Processed data", result[-2]["content"])
        self.assertEqual(result[-1]["content"], "Final response.")

    def test_execute_with_tool_call_recursion_depth(self):
        self.mock_llm_module.execute.side_effect = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "test_llm_agent.example_tool", "arguments": {"param1": "data"}}}
                ]
            },
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"function": {"name": "test_llm_agent.example_tool", "arguments": {"param1": "data2"}}}
                ]
            },
            {"role": "assistant", "content": "Final response."}
        ]

        

        self.agent.tool_registry.register_tool(example_tool)

        messages = [{"role": "user", "content": "What is the result?"}]
        result = self.agent.execute(messages)

        self.assertEqual(len(result), 6)  # System message + user query + 2 tool calls + 2 assistant responses
        self.assertIn("Processed data", result[2]["content"])
        self.assertIn("Processed data2", result[4]["content"])

    def test_execute_with_invalid_tool_call(self):
        self.mock_llm_module.execute.return_value = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {"function": {"name": "non_existent_tool", "arguments": {}}}
            ]
        }

        messages = [{"role": "user", "content": "What is the result?"}]
        result = self.agent.execute(messages)

        self.assertIn("Tool invocation failed", result[-1]["content"])

    def test_execute_without_tool_calls(self):
        self.mock_llm_module.execute.return_value = {
            "role": "assistant",
            "content": "Here is your answer."
        }

        messages = [{"role": "user", "content": "What is the result?"}]
        result = self.agent.execute(messages)

        self.assertEqual(result[-1]["content"], "Here is your answer.")




if __name__ == "__main__":
    unittest.main()