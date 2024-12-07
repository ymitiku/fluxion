from fluxion.modules.ir_module import IndexingModule, RetrievalModule
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.modules.rag_module import RagModule


if __name__ == "__main__":

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

