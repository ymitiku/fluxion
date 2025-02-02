import unittest
import numpy as np
from unittest.mock import Mock
import faiss
from fluxion.core.modules.ir_module import IndexingModule, RetrievalModule

class TestIndexingModule(unittest.TestCase):
    def test_indexing(self):
        mock_llm = Mock()
        mock_llm.execute.return_value = [[0.1, 0.2, 0.3, 0.4]]
        documents = ["Test document"]
        
        module = IndexingModule(endpoint="http://mock-endpoint", model="mock-model", embedding_size=4)
        module.encode_documents = Mock(return_value=np.array([[0.1, 0.2, 0.3, 0.4]]))  # Mock embedding generation
        
        index = module.execute(documents=documents)
        self.assertIsInstance(index, faiss.IndexFlatIP)
        self.assertEqual(len(module.documents), 1)

class TestRetrievalModule(unittest.TestCase):
    def test_retrieval(self):
        mock_index = faiss.IndexFlatIP(4)
        mock_index.add(np.array([[0.1, 0.2, 0.3, 0.4]]))
        documents = ["Test document"]
        indexing_module = IndexingModule(endpoint="http://mock-endpoint", model="mock-model", embedding_size=4)
        indexing_module.index = mock_index
        indexing_module.documents = documents
        
        module = RetrievalModule(indexing_module=indexing_module, documents=documents, endpoint="http://mock-endpoint", model="mock-model", embedding_size=4)
        module.encode_document = Mock(return_value=np.array([[0.1, 0.2, 0.3, 0.4]]))  # Mock embedding generation
        
        results = module.execute(query="Test query", top_k=1)
        self.assertEqual(results, ["Test document"])


if __name__ == "__main__":
    unittest.main()