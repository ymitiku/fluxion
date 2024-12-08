from fluxion.workflows.builtin_workflows import contextual_response_workflow
from fluxion.core.workflow_orchestrator import NamedFlowOrchestrator

if __name__ == "__main__":
    # Inputs for the workflow
    llm_endpoint = "http://localhost:11434/api/generate"
    rag_endpoint = "http://localhost:11434/api/embeddings"
    llm_model = "llama3.2"
    rag_model = "all-minilm"
    user_query = "What is the capital of France?"
    documents = [
        "The capital of France is Paris.",
        "The speed of light is 299,792,458 meters per second.",
        "The Earth is the third planet from the Sun.",
    ]
    

    manager = NamedFlowOrchestrator()
    manager.register_flow("contextual_response_workflow", contextual_response_workflow)
    response = manager.execute_workflow("contextual_response_workflow", llm_endpoint=llm_endpoint, rag_endpoint=rag_endpoint, llm_model=llm_model, rag_model=rag_model, user_query=user_query, documents=documents)

    
    print("Response:", response)