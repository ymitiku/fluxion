import faiss
from typing import List
import numpy as np
from fluxion.modules.api_module import ApiModule
import logging


class EmbeddingApiModule(ApiModule):
    def __init__(self, endpoint: str, model: str = None, headers: dict = None, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4, documents_key: str = "documents"):
        super().__init__(endpoint, headers, timeout)
        self.model = model
        self.embedding_size = embedding_size
        self.batch_size = batch_size
        self.documents_key = documents_key

    def encode_documents(self, documents: List[str]):
        for doc in documents:
            if doc is None or doc == "":
                raise ValueError("Empty document found")
        embeddings = []
        for batch in self.batchify(documents, self.batch_size):
            data = {
                "model": self.model,
                "input": batch,
            }
            response = self.get_response(data)
            embeddings.append(self.post_process(response))
     
        return np.concatenate(embeddings, axis=0)
    
    def post_process(self, response, full_response = False):
        if "embeddings" in response:
            return np.array(response["embeddings"], dtype=np.float32)
        else:
            raise ValueError("No embedding found in response")
        
    def encode_document(self, document: str):
        if document is None or document == "":
            raise ValueError("Empty document found")
        data = {
            "model": self.model,
            "input": document,
        }
        response = self.get_response(data)
        return self.post_process(response)
    
    def batchify(self, data, batch_size):
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def get_input_params(self, *args, **kwargs):
        if self.documents_key in kwargs:

            documents = kwargs.get(self.documents_key, None)
            assert documents is not None, "Documents are required for indexing"
            return {self.documents_key: documents}
        else:
            raise ValueError("Documents are required for indexing")

    def execute(self, *args, **kwargs):
        data = self.get_input_params(*args, **kwargs)
        assert self.documents_key in data, "Documents are required for indexing"
        if type(data[self.documents_key]) == str:
            embeddings = self.encode_document(data[self.documents_key])
        elif type(data[self.documents_key]) == list:
            embeddings = self.encode_documents(data[self.documents_key])
        else:
            raise ValueError("Invalid input type for documents")
        return_documents = kwargs.get("return_documents", False)

        if return_documents:
            return {
                self.documents_key: data[self.documents_key],
                "embeddings": embeddings
            }
        else:
            return embeddings
    

class IndexingModule(EmbeddingApiModule):
    def __init__(self, endpoint: str, model: str = None, headers: dict = None, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4):
        super().__init__(endpoint, model, headers, timeout, embedding_size, batch_size, documents_key="documents")
        self.index = faiss.IndexFlatIP(embedding_size)
        self.documents = []
        self.logger = logging.getLogger(__name__)

    def execute(self, *args, **kwargs):
        data = self.get_input_params(*args, **kwargs)
        self.documents = data[self.documents_key]
        embeddings = super().execute(documents=self.documents)
        self.logger.info(f"Adding {len(embeddings)} embeddings to the index")
        self.index.add(embeddings)
        return self.index

class RetrievalModule(EmbeddingApiModule):
    def __init__(self, index: faiss.IndexFlatIP, documents: List[str], endpoint: str, model: str = None, headers: dict = None, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4):
        super().__init__(endpoint, model, headers, timeout, embedding_size=embedding_size, batch_size=batch_size, documents_key="query")
        self.index = index
        self.documents = documents
        self.logger = logging.getLogger(__name__)


    def get_input_params(self, *args, **kwargs):
        if "query" in kwargs:
            query = kwargs["query"]
            assert type(query) == str, "Invalid input type for query"
            return {"query": query, "top_k": kwargs.get("top_k", 1)}
        else:
            raise ValueError("Query is required for retrieval")

    def retrieve(self, query: str, top_k: int = 1):
        query_embedding = super().execute(query=query)
        distances, indices = self.index.search(query_embedding, top_k)
                
        return [self.documents[i] for i in indices[0] if i < len(self.documents)]
    def execute(self, *args, **kwargs):
        data = self.get_input_params(*args, **kwargs)
        query = data["query"]
        top_k = data.get("top_k", 1)
        return self.retrieve(query, top_k)