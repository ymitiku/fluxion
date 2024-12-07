import unittest
import responses
from fluxion.modules.llm_integration import LLMIntegration
import requests

class TestLLMIntegration(unittest.TestCase):
    @responses.activate
    def test_query_success(self):
        # Mock endpoint and response
        endpoint = "http://localhost:5000/api/v1/query"
        prompt = "What is the capital of France?"
        model = "local-gpt-model"
        mock_response = {"response": "The capital of France is Paris."}

        # Mock the POST request
        responses.add(
            responses.POST,
            endpoint,
            json=mock_response,
            status=200,
        )

        # Initialize LLMIntegration with the mock endpoint
        llm = LLMIntegration(endpoint=endpoint, model=model)

        # Call the query method
        response = llm.query(prompt=prompt)

        # Assert the response matches the mock response
        self.assertEqual(response, mock_response)

    @responses.activate
    def test_query_error(self):
        # Mock endpoint and response
        endpoint = "http://localhost:5000/api/v1/query"
        prompt = "What is the speed of light?"
        model = "local-gpt-model"
        mock_error = "HTTP error occurred: 500 Server Error: Internal Server Error for url: http://localhost:5000/api/v1/query"

        # Mock the POST request with an error
        responses.add(
            responses.POST,
            endpoint,
            # json=mock_error,
            status=500,
        )

        # Initialize LLMIntegration with the mock endpoint
        llm = LLMIntegration(endpoint=endpoint, model=model)
    
        with self.assertRaises(requests.exceptions.HTTPError):
            response = llm.query(prompt=prompt)



    @responses.activate
    def test_query_timeout(self):
        # Mock endpoint
        endpoint = "http://localhost:5000/api/v1/query"
        prompt = "Describe quantum mechanics."
        model = "local-gpt-model"

        # Simulate a timeout by not returning a response
        responses.add(
            responses.POST,
            endpoint,
            body=requests.exceptions.Timeout("Request timed out."),
        )

        # Initialize LLMIntegration with the mock endpoint
        llm = LLMIntegration(endpoint=endpoint, model=model)

        with self.assertRaises(requests.exceptions.Timeout):
            response = llm.query(prompt=prompt)


if __name__ == "__main__":
    unittest.main()
