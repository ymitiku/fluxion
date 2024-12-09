from flytekit import task, workflow
from typing import List
from fluxion.modules.llm_modules import LLMQueryModule
from fluxion.modules.rag_module import RagModule


@task
def contextual_response_task(
    rag_endpoint: str, rag_model: str, llm_endpoint: str, llm_model: str, user_query: str, documents: List[str], top_k: int,
    embedding_size: int = 384
) -> str:
    """
    Task to generate a response using the RagModule and LLMIntegration.
    """

    llm_module = LLMQueryModule(endpoint=llm_endpoint, model=llm_model, timeout=60)
    print("Adding documents to the RAG index...")
    rag_module = RagModule(endpoint=rag_endpoint, model=rag_model, embedding_size=embedding_size)
    for doc in documents:
        rag_module.add_document(doc)

    print("Retrieving context...")
    context = rag_module.retrieve(query=user_query, top_k=top_k)
    context_text = "\n".join(context)
    prompt = f"If context is available please use it. Answer the following question based on the context:\n\nContext:\n{context_text}\n\nQuestion: {user_query}"
    print("Generating response...")
    response = llm_module.query(prompt=prompt)
    return response.get("response", "Error generating response")


@workflow
def contextual_response_workflow(
    llm_endpoint: str,
    rag_endpoint: str,
    rag_model: str,
    llm_model: str,
    user_query: str,
    documents: List[str],
    top_k: int = 1,
    embedding_size: int = 384,
) -> str:
    """
    Flyte workflow to generate a contextual response.
    """

    return contextual_response_task(
        rag_endpoint=rag_endpoint,
        rag_model=rag_model,
        llm_endpoint=llm_endpoint,
        llm_model=llm_model,
        user_query=user_query,
        documents=documents,
        top_k=top_k,
        embedding_size=embedding_size,
    )