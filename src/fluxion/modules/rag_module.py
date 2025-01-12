""" 
fluxion.modules.rag_module
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides an interface for interacting with a RAG module for retrieval-augmented generation.

Example:
    ```python
    from fluxion.modules.ir_module import IndexingModule, RetrievalModule
    from fluxion.modules.llm_modules import LLMChatModule
    from fluxion.modules.rag_module import RagModule


    endpoint = "http://localhost:11434/api/embed"
    chat_endpoint = "http://localhost:11434/api/chat"
    model = "all-minilm"
    documents = [
        "Capital of France is Paris",
        "USA got independence in 1776",
        "Python is a programming language",
        "Donald Trump won the 2024 presidential election",
        "It is December 2024. Joe Biden is the current president of the USA",

    ]
    index_module = IndexingModule(endpoint=endpoint, model=model, embedding_size=384)
    index = index_module.execute(documents=documents)
  
    query = "It is now  January 2025. Who is the current president of the USA?"

    retrieval_module = RetrievalModule(index=index, documents=documents, endpoint=endpoint, model=model, embedding_size=384)
    response = retrieval_module.execute(query=query, top_k=2)

    print("Response:", response)

    llm_module = LLMChatModule(endpoint=chat_endpoint, model="llama3.2", timeout=60)

    rag_module = RagModule(retrieval_module=retrieval_module, llm_module=llm_module)
    response = rag_module.execute(query=query, top_k=2)
    print("Rag Response:", response)

    ```

"""


from fluxion.core.modules.ir_module import EmbeddingApiModule, RetrievalModule
from fluxion.core.modules.llm_modules import LLMChatModule   

class RagModule(EmbeddingApiModule):
    """
    Provides an interface for interacting with a RAG module for retrieval-augmented generation.
    """
    def __init__(self, retrieval_module: RetrievalModule, llm_module: LLMChatModule):
        """
        Initialize the RagModule.

        Args:
            retrieval_module (RetrievalModule): The retrieval module instance.
            llm_module (LLMChatModule): The LLMChatModule instance.
        """
        self.retrieval_module = retrieval_module
        self.llm_module = llm_module
    def execute(self, query: str, top_k: int = 1):
        """
        Execute the RAG module logic.
        
        Args:
            query (str): The query or prompt for the agent.
            top_k (int): The number of documents to retrieve.

        Returns:
            str: The response from the LLM.

        Raises:
            ValueError: If the query is empty or invalid.
        """
        context = self.retrieval_module.retrieve(query=query, top_k=top_k)
        context_text = "\n".join(context)
        response = self.llm_module.execute(messages=[
            {
                "role": "system",
                "content": "Answer the user query based on the context."
            },
            {
                "role": "user",
                "content": "Context:\n" + context_text + "\n\nQuestion: " + query
            },
        ])
        return response
        
