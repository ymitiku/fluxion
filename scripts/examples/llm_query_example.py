from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule


if __name__ == "__main__":
    llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
    response = llm_module.execute(prompt="What is the capital of France?")
    print("Query: What is the capital of France?")
    print("Response:", response)
    llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
    response = llm_module.execute(messages=[
        {
            "role": "user",
            "content": "Hello!"
        }

    ])
    print("Chat:")
    print("User: Hello!")
    print("Response:", response["content"])