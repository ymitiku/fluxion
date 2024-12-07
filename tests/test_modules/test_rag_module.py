import unittest
from unittest.mock import patch
import numpy as np
from fluxion.modules.rag_module import RAGModule

class TestRAGModule(unittest.TestCase):
    def setUp(self):
        self.endpoint = "http://localhost:5000/api/v1/encode"
        self.model = "local-embedding-model"
        self.rag = RAGModule(endpoint=self.endpoint, model=self.model, embedding_size=768)

    @patch.object(RAGModule, "get_response")
    def test_add_document(self, mock_get_response):
        # Mock embedding response
        mock_embedding = np.random.rand(768).tolist()
        mock_get_response.return_value = {"embedding": mock_embedding}

        # Add a document
        document = "This is a test document."
        self.rag.add_document(document)

        # Assert the document and index status
        self.assertEqual(len(self.rag.documents), 1)
        self.assertEqual(self.rag.documents[0], document)
        self.assertEqual(self.rag.index.ntotal, 1)

    @patch.object(RAGModule, "get_response")
    def test_retrieve(self, mock_get_response):
        # Mock embedding response
        mock_embedding = np.random.rand(768).tolist()
        mock_get_response.return_value = {"embedding": mock_embedding}

        # Add documents
        self.rag.add_document("Document 1")
        self.rag.add_document("Document 2")

        # Mock query embedding
        mock_get_response.return_value = {"embedding": mock_embedding}

        # Retrieve documents
        result = self.rag.retrieve("Query", top_k=1)

        # Assert results
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], self.rag.documents)

    @patch.object(RAGModule, "get_response")
    def test_empty_index_retrieve(self, mock_get_response):
        # Attempt to retrieve without adding documents
        with self.assertRaises(ValueError, msg="No documents in the index. Please add documents first."):
            self.rag.retrieve("Query")

    @patch.object(RAGModule, "get_response")
    def test_api_error(self, mock_get_response):
        # Mock an API error
        mock_get_response.return_value = {"error": "Failed to encode the document."}

        # Add a document
        document = "This is a failing document."
        self.rag.add_document(document)

        # Assert the document is not added to the index
        self.assertEqual(len(self.rag.documents), 0)
        self.assertEqual(self.rag.index.ntotal, 0)

if __name__ == "__main__":
    unittest.main()
