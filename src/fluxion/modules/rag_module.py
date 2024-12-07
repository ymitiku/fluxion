import faiss
import numpy as np
from fluxion.modules.api_module import ApiModule

class RAGModule(ApiModule):
    """
    Implements Retrieval-Augmented Generation for contextual workflows.
    """
    def __init__(self, endpoint: str, model: str = None, headers: dict = None, timeout: int = 10, embedding_size: int = 768):
        """
        Initialize the RAG module.

        Args:
            endpoint (str): The endpoint to send the request to.
            model (str): The model to use for encoding text.
            headers (dict): The headers to include in the request.
            timeout (int): The request timeout in seconds.
            embedding_size (int): The size of the text embeddings.
        """
        super().__init__(endpoint, headers, timeout)
        self.model = model
        self.index = faiss.IndexFlatIP(embedding_size)
        self.embedding_size = embedding_size
        self.documents = []

    def add_document(self, document: str):
        """
        Add a document to the RAG index.

        Args:
            document (str): Document text to be indexed.
        """
        embedding = self.encode_document(document)

        if embedding is not None and embedding.shape[0] == 1 and embedding.shape[1] == self.embedding_size:
            self.index.add(embedding)
            self.documents.append(document)
        elif embedding is None:
            print(f"Failed to add document: {document}")
        elif len(embedding) != 1:
            print(f"Failed to add document: {document}. Expected 1 embedding, got {len(embedding)}")
        elif len(embedding[0]) != self.embedding_size:
            print(f"Failed to add document: {document}. Expected embedding size {self.embedding_size}, got {len(embedding[0])}")
    

    def encode_document(self, document: str):
        """
        Encode a document using the RAG model.

        Args:
            document (str): Document text to be encoded.

        Returns:
            np.array: Encoded document or None in case of an error.
        """
        data = {
            "model": self.model,
            "prompt": document,
        }
        response = self.get_response(data)
        if "embedding" in response:
            return np.array([response["embedding"]], dtype=np.float32)
        else:
            print(f"Error encoding document: {response.get('error', 'Unknown error')}")
            return None

    def retrieve(self, query: str, top_k: int = 1):
        """
        Retrieve the most relevant documents for a query.

        Args:
            query (str): Query text.
            top_k (int): Number of top results to retrieve.

        Returns:
            list: Retrieved documents.
        """
        if self.index.ntotal == 0:
            raise ValueError("No documents in the index. Please add documents first.")
        query_embedding = self.encode_document(query)
        if query_embedding is None:
            return []
        distances, indices = self.index.search(query_embedding, top_k)
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
