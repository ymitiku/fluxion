import requests
import unittest
from unittest.mock import patch
from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule

class TestLLMModules(unittest.TestCase):
    @patch("fluxion.core.modules.api_module.requests.post")
    def test_llm_query_success(self, mock_post):
        # Mock a successful API response
        mock_post.return_value.json.return_value = {"response": "Paris"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize the LLMQueryModule
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

        # Execute the query
        result = llm_module.execute(prompt="What is the capital of France?")
        
        # Assert the response
        self.assertEqual(result, "Paris")
        mock_post.assert_called_once()

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_llm_query_failure(self, mock_post):
        # Mock a failed API request
        mock_post.side_effect = requests.exceptions.RequestException("API request failed.")

        # Initialize the LLMQueryModule
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

        # Execute the query
        result = llm_module.execute(prompt="What is the capital of France?")
        
        # Assert the error message
        self.assertIn("error", result)
        self.assertIn("API request failed", result["error"])

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_llm_chat_success(self, mock_post):
        # Mock a successful API response for chat
        mock_post.return_value.json.return_value = {"message": "Hello, how can I help you?"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize the LLMChatModule
        llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

        # Execute the chat
        result = llm_module.execute(messages=[{"role": "user", "content": "Hello!"}])
        
        # Assert the response
        self.assertEqual(result, "Hello, how can I help you?")
        mock_post.assert_called_once()

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_llm_chat_failure(self, mock_post):
        # Mock a failed API request
        mock_post.side_effect = requests.exceptions.RequestException("API request failed.")

        # Initialize the LLMChatModule
        llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

        # Execute the chat
        result = llm_module.execute(messages=[{"role": "user", "content": "Hello!"}])
        
        # Assert the error message
        self.assertIn("error", result)
        self.assertIn("API request failed", result["error"])

    @patch("fluxion.core.modules.api_module.requests.post")
    def test_llm_query_full_response(self, mock_post):
        # Mock a successful API response with full response mode
        mock_post.return_value.json.return_value = {"response": "Paris", "other_info": "details"}
        mock_post.return_value.raise_for_status = lambda: None

        # Initialize the LLMQueryModule
        llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

        # Execute the query with full_response=True
        result = llm_module.execute(prompt="What is the capital of France?", full_response=True)
        
        # Assert the full response
        self.assertEqual(result, {"response": "Paris", "other_info": "details"})
        mock_post.assert_called_once()

if __name__ == "__main__":
    unittest.main()
