import unittest
from unittest.mock import Mock
from fluxion.modules.rag_module import RagModule

class TestRagModule(unittest.TestCase):
    def test_rag_execution(self):
        mock_retrieval = Mock()
        mock_retrieval.retrieve.return_value = ["Context document"]
        mock_llm = Mock()
        mock_llm.execute.return_value = "Generated response"

        module = RagModule(retrieval_module=mock_retrieval, llm_module=mock_llm)
        response = module.execute(query="Test query", top_k=1)
        self.assertEqual(response, "Generated response")
        mock_retrieval.retrieve.assert_called_once_with(query="Test query", top_k=1)
        mock_llm.execute.assert_called_once()
