
"""
fluxion_ai.modules.ir_module
~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides modules for indexing and retrieving information using embeddings.

This module defines classes for embedding generation, indexing, and retrieval
of documents using a locally hosted embedding model and FAISS for efficient similarity search.


ir_module:
example-usage::
    from fluxion_ai.modules.ir_module import IndexingModule, RetrievalModule

    # Initialize the IndexingModule
    indexing_module = IndexingModule(endpoint="http://localhost:11434/api/index", model="sentence-transformers/paraphrase-MiniLM-L6-v2")

    # Index documents
    documents = ["Capital of France is Paris", "USA got independence in 1776"]
    index = indexing_module.execute(documents=documents)

    # Initialize the RetrievalModule
    retrieval_module = RetrievalModule(index=index, documents=documents, endpoint="http://localhost:11434/api/retrieve", model="sentence-transformers/paraphrase-MiniLM-L6-v2")

    # Retrieve relevant context
    response = retrieval_module.execute(query="What is the capital of France?", top_k=1)
    print(response)
"""



import faiss
from typing import List, Generator, Dict, Any
import numpy as np
from fluxion_ai.core.modules.api_module import ApiModule
import logging


class EmbeddingApiModule(ApiModule):
    """
    A module for generating embeddings using a locally hosted embedding model via REST API.

    This module provides methods for encoding documents into embeddings and processing the API responses.

    EmbeddingApiModule:
    example-usage::
        from fluxion_ai.modules.ir_module import EmbeddingApiModule

        # Initialize the EmbeddingApiModule
        embedding_module = EmbeddingApiModule(endpoint="http://localhost:11434/api/encode", model="sentence-transformers/paraphrase-MiniLM-L6-v2")

        # Encode a single document
        embedding = embedding_module.execute(documents="Hello, World!")
        print(embedding)

        # Encode multiple documents
        documents = ["Capital of France is Paris", "USA got independence in 1776"]
        embeddings = embedding_module.execute(documents=documents)
        print(embeddings)

    """
    def __init__(self, endpoint: str, model: str = None, headers: dict = None, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4, documents_key: str = "documents"):
        """
        Initialize the EmbeddingApiModule.

        Args:
            endpoint (str): The API endpoint URL.
            model (str, optional): The embedding model name.
            headers (dict, optional): Headers to include in API requests. Defaults to None.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10.
            embedding_size (int, optional): Size of the embeddings. Defaults to 768.
            batch_size (int, optional): Batch size for encoding documents. Defaults to 4.
            documents_key (str, optional): Key for document data in API requests. Defaults to "documents".
        """
        super().__init__(endpoint, headers, timeout)
        self.model = model
        self.embedding_size = embedding_size
        self.batch_size = batch_size
        self.documents_key = documents_key

    def encode_documents(self, documents: List[str]) -> np.ndarray:
        """
        Encode a list of documents into embeddings.

        Args:
            documents (List[str]): List of documents to encode.

        Returns:
            np.ndarray: A NumPy array containing the embeddings.

        Raises:
            ValueError: If a document is empty or invalid.
        """
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
    
    def post_process(self, response, full_response = False) -> np.ndarray:
        """
        Post-process the API response to extract embeddings.

        Args:
            response (dict): The API response.
            full_response (bool, optional): Whether to return the full response. Defaults to False.

        Returns:
            np.ndarray: The extracted embeddings.

        Raises:
            ValueError: If embeddings are not found in the response.
        """
        if "embeddings" in response:
            return np.array(response["embeddings"], dtype=np.float32)
        else:
            raise ValueError("No embedding found in response")
        
    def encode_document(self, document: str) -> np.ndarray:
        """
        Encode a single document into an embedding.

        Args:
            document (str): The document to encode.

        Returns:
            np.ndarray: A NumPy array containing the embedding.

        Raises:
            ValueError: If the document is empty or invalid.
        """
        if document is None or document == "":
            raise ValueError("Empty document found")
        data = {
            "model": self.model,
            "input": document,
        }
        response = self.get_response(data)
        return self.post_process(response)
    
    def batchify(self, data, batch_size) -> Generator[List[str], None, None]:
        """
        Split data into batches for processing.

        Args:
            data (List[str]): The data to batchify.
            batch_size (int): The batch size.

        Yields:
            List[str]: A batch of data.
        """
        for i in range(0, len(data), batch_size):
            yield data[i:i + batch_size]

    def get_input_params(self, *args, **kwargs):
        """ Get input parameters for the API call. 
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            dict: The input parameters for the API call.
        """
        if self.documents_key in kwargs:

            documents = kwargs.get(self.documents_key, None)
            assert documents is not None, "Documents are required for indexing"
            return {self.documents_key: documents}
        else:
            raise ValueError("Documents are required for indexing")

    def execute(self, *args, **kwargs) -> np.ndarray:
        """
        Execute the embedding generation process.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            np.ndarray: The generated embeddings or a dictionary with documents and embeddings.
        """
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
    """
    A module for indexing documents using FAISS. Inherits from EmbeddingApiModule.

    This module provides methods for encoding documents into embeddings, adding them to a FAISS index, and processing the API responses.

    IndexingModule:
    example-usage::
        from fluxion_ai.modules.ir_module import IndexingModule

        # Initialize the IndexingModule
        indexing_module = IndexingModule(endpoint="http://localhost:11434/api/index", model="sentence-transformers/paraphrase-MiniLM-L6-v2")

        # Index documents
        documents = ["Capital of France is Paris", "USA got independence in 1776"]
        index = indexing_module.execute(documents=documents)
    """
    def __init__(self, endpoint: str, model: str = None, headers: dict = {}, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4):
        """
        Initialize the IndexingModule.

        Args:
            endpoint (str): The API endpoint URL.
            model (str, optional): The embedding model name.
            headers (dict, optional): Headers to include in API requests. Defaults to an empty dictionary.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10.
            embedding_size (int, optional): Size of the embeddings. Defaults to 768.
            batch_size (int, optional): Batch size for encoding documents. Defaults to 4.
        """
        super().__init__(endpoint, model, headers, timeout, embedding_size, batch_size, documents_key="documents")
        self.index = faiss.IndexFlatIP(embedding_size)
        self.documents = []
        self.logger = logging.getLogger(__name__)

    def execute(self, *args, **kwargs) -> faiss.IndexFlatIP:
        """
        Index documents and add embeddings to the FAISS index.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            faiss.IndexFlatIP: The FAISS index with the added embeddings.
        """
        data = self.get_input_params(*args, **kwargs)
        self.documents = data[self.documents_key]
        embeddings = super().execute(documents=self.documents)
        self.logger.info(f"Adding {len(embeddings)} embeddings to the index")
        self.index.add(embeddings)
        return self.index

class RetrievalModule(EmbeddingApiModule):
    """
    A module for retrieving documents using a FAISS index and query embeddings.

    This module provides methods for encoding queries into embeddings, searching the FAISS index for the most similar documents, and processing the API responses.

    RetrievalModule:
    example-usage::
        from fluxion_ai.modules.ir_module import RetrievalModule

        # Initialize the RetrievalModule
        retrieval_module = RetrievalModule(index=index, documents=documents, endpoint="http://localhost:11434/api/retrieve", model="sentence-transformers/paraphrase-MiniLM-L6-v2")

        # Retrieve relevant context
        response = retrieval_module.execute(query="What is the capital of France?", top_k=1)
        print(response)
    """
    def __init__(self, indexing_module: IndexingModule, endpoint: str, model: str = None, headers: dict = {}, timeout: int = 10, embedding_size: int = 768, batch_size: int = 4):
        """
        Initialize the RetrievalModule.

        Args:
            indexing_module (IndexingModule): The indexing module containing the FAISS index.
            endpoint (str): The API endpoint URL.
            model (str, optional): The embedding model name.
            headers (dict, optional): Headers to include in API requests. Defaults to an empty dictionary.
            timeout (int, optional): Timeout for API requests in seconds. Defaults to 10.
            embedding_size (int, optional): Size of the embeddings. Defaults to 768.
            batch_size (int, optional): Batch size for encoding queries. Defaults to 4.
        """
        super().__init__(endpoint, model, headers, timeout, embedding_size=embedding_size, batch_size=batch_size, documents_key="query")
        self.indexing_module = indexing_module
        self.logger = logging.getLogger(__name__)


    def get_input_params(self, *args, **kwargs) -> Dict[str, Any]:
        """ Get input parameters for the retrieval API call.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Dict[str, Any]: The input parameters for the retrieval API call.
        
        """
        if "query" in kwargs:
            query = kwargs["query"]
            assert type(query) == str, "Invalid input type for query"
            return {"query": query, "top_k": kwargs.get("top_k", 1)}
        else:
            raise ValueError("Query is required for retrieval")

    def retrieve(self, query: str, top_k: int = 1) -> List[str]:
        """
        Retrieve the most relevant documents for a query.

        Args:
            query (str): The query text.
            top_k (int, optional): Number of top results to retrieve. Defaults to 1.

        Returns:
            List[str]: The retrieved documents.
        """
        query_embedding = super().execute(query=query)
        distances, indices = self.indexing_module.index.search(query_embedding, top_k)
                
        return [self.indexing_module.documents[i] for i in indices[0] if i < len(self.indexing_module.documents)]
    def execute(self, *args, **kwargs) -> List[str]:
        """
        Execute the retrieval process.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            List[str]: The retrieved documents.
        """
        data = self.get_input_params(*args, **kwargs)
        query = data["query"]
        top_k = data.get("top_k", 1)
        return self.retrieve(query, top_k)