
from fluxion.modules.ir_module import EmbeddingApiModule, RetrievalModule
from fluxion.modules.llm_modules import LLMChatModule   

class RagModule(EmbeddingApiModule):
    def __init__(self, retrieval_module: RetrievalModule, llm_module: LLMChatModule):
        self.retrieval_module = retrieval_module
        self.llm_module = llm_module
    def execute(self, query: str, top_k: int = 1):
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
        
