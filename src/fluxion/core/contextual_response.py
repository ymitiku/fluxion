from typing import List
from fluxion.modules.rag_module import RAGModule
from fluxion.modules.llm_integration import LLMIntegration



class ContextualResponse:
    """
    A class to handle the core contextual response functionality.

    This class encapsulates:
      - Document addition to a RAG index
      - Retrieval of relevant context
      - Querying an LLM for a response
    """

    def __init__(self, rag_endpoint: str, rag_model: str, llm_endpoint: str, llm_model: str, embedding_size: int = 384):
        """
        Initialize the ContextualResponse handler.

        Args:
            rag_endpoint (str): Endpoint for the RAGModule API.
            rag_model (str): Model to use for the RAGModule.
            llm_endpoint (str): Endpoint for the LLMIntegration API.
            llm_model (str): Model to use for the LLMIntegration.
            embedding_size (int): Size of the embeddings (default: 384).
        """
        self.rag_module = RAGModule(endpoint=rag_endpoint, model=rag_model, embedding_size=embedding_size)
        self.llm_module = LLMIntegration(endpoint=llm_endpoint, model=llm_model)

    def add_documents(self, documents: List[str]) -> None:
        """
        Add documents to the RAG index.

        Args:
            documents (List[str]): List of documents to index.
        """
        for doc in documents:
            self.rag_module.add_document(doc)

    def generate_response(self, user_query: str, top_k: int = 1) -> str:
        """
        Generate a contextual response for the user query.

        Args:
            user_query (str): The query from the user.
            top_k (int): Number of top documents to retrieve (default: 1).

        Returns:
            str: The response generated by the LLM.
        """
        # Retrieve context from RAG
        context = self.rag_module.retrieve(query=user_query, top_k=top_k)
        context_text = "\n".join(context)

        # Construct the prompt for the LLM
        prompt = f"Answer the following question based on the context:\n\nContext:\n{context_text}\n\nQuestion: {user_query}"

        # Query the LLM and return the response
        response = self.llm_module.query(prompt=prompt)
        return response.get("response", "Error generating response")
