from fluxion.core.modules.ir_module import IndexingModule, RetrievalModule
from fluxion.core.modules.llm_modules import LLMChatModule
from fluxion.modules.rag_module import RagModule


if __name__ == "__main__":

    endpoint = "http://localhost:11434/api/embed"
    chat_endpoint = "http://localhost:11434/api/chat"
    model = "all-minilm"
    documents = [
        "Capital of France is Paris",
        "USA got independence in 1776",
        "Python is a programming language",
        """
        Robert B. Darnell’s lab unveiled a tool edging neuroscience much closer to understanding a phenomenon known as dendritic translation—a “holy grail for understanding memory formation,” he says. 
        Dendritic translation is a coordinated burst of neuronal activity, which involves an uptick in localized protein production within the spiny branches that project off the neuron cell body and 
        receive signals from other neurons at synapses. It’s a process key to memory—and its dysfunction is linked to intellectual disorders.

        Using a new platform they developed, Darnell’s team identified several previously unknown regulatory mechanisms that drive dendritic translation. The work “defines a whole new biochemical 
        pathway which fits with, complements, and vastly expands what we already knew about memory and learning,” Darnell says. 
        """, # Copied from https://www.rockefeller.edu/news/36948-intriguing-science-discoveries-of-2024/
        "biochemistry, study of the chemical substances and processes that occur in plants, animals, and microorganisms and of the changes they undergo during development and life."

    ]
    index_module = IndexingModule(endpoint=endpoint, model=model, embedding_size=384)
    index = index_module.execute(documents=documents)
  
    query = "Who is Robert B. Darnell? What is his lab's recent discovery?"

    retrieval_module = RetrievalModule(indexing_module=index_module, endpoint=endpoint, model=model, embedding_size=384)
    response = retrieval_module.execute(query=query, top_k=2)
    print("Query:", query)
    print("Retrieval Response:")
    print("Response 0:", response[0])
    print("Response 1:", response[1])
    print("=====================================")

    llm_module = LLMChatModule(endpoint=chat_endpoint, model="llama3.2", timeout=60)
    print("Running rag example")
    print("Query:", query)
    print("Querying without RAG")
    response = llm_module.execute(messages=[
        {
            "role": "user",
            "content": query
        }

    ])
    print("Response:", response["content"])

    print("=====================================")
    print("Querying with RAG")

    rag_module = RagModule(retrieval_module=retrieval_module, llm_module=llm_module)
    response = rag_module.execute(query=query, top_k=2)
    print("Rag Response:", response["content"])

