# Fluxion

![CI Workflow](https://github.com/ymitiku/fluxion/actions/workflows/ci.yml/badge.svg)


**Fluxion** is a Python library for building flow-based agentic workflows powered by [Flyte](https://flyte.org). It enables seamless orchestration of tasks, integration with language models (LLMs), retrieval-augmented generation (RAG), and program execution, along with speech-to-text (STT) and text-to-speech (TTS) capabilities.



---

## Enhancements

### LLM Capabilities
- **LLMChatAgent**: Supports chat interactions with tools, including methods for executing chat logic and handling tool calls.
- **LLMChatModule**: Includes tools in the input parameters for chat interactions.

### Registry System
- **ToolRegistry**: Methods for registering tools, invoking tool calls, and extracting function metadata.
- **AgentRegistry**: Improved agent registration and retrieval methods.

### Query Execution
- Enhanced query handling to manage empty queries and concatenate system instructions with the query.

## New Modules
- **EmbeddingApiModule**: Handles document embedding.
- **IndexingModule**: Manages the indexing process.
- **RetrievalModule**: Facilitates document retrieval.
- **RagModule**: Implements retrieval-augmented generation using the new retrieval and LLM modules.

## Example Scripts
- Example script demonstrating LLM with tool call integration.
- Example script for querying and generating responses using the RAG module.

## Tests
- Comprehensive unit tests for `LLMChatAgent` and `ToolRegistry`.
- Unit tests for agent registration, unregistration, and query execution.
- Unit tests for `IndexingModule`, `RetrievalModule`, and `RagModule`.

These enhancements collectively improve the functionality and robustness of the `fluxion` project, enabling more sophisticated interactions with LLMs and better management of tools and agents.

## Installation
To install and use Fluxion, please follow the instructions below:

```sh
# Clone the repository
git clone https://github.com/ymitiku/fluxion.git

# Navigate to the project directory
cd fluxion

# Install dependencies
pip install -r requirements.txt

```

## Usage

### Calling locally hosted LLMs

To call locally hosted LLMs, you can use the following code snippet:

```python
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
```

Currently, the `LLMQueryModule` and `LLMChatModule` classes support calling locally hosted LLMs. The `execute` method sends a request to the specified endpoint with the provided prompt or messages and returns the response.

### Using agents for chat interactions and tool calls

Fluxion provides an `LLMChatAgent` class for managing chat interactions and tool calls. You can use the following code snippet to create an agent and execute a chat interaction with tool calls:

```python
    def get_current_whether(city_name):
        return {"temperature": 6.85, "description": "overcast clouds", "humidity": 91}
    # Initialize the LLMChatModule
    llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=60)

    # Initialize the LLMChatAgent
    llm_agent = LLMChatAgent(name="llm_chat_agent", llm_module=llm_module, system_instructions="Provide accurate answers.")
    

    ToolRegistry.register_tool(get_current_whether)
    # Execute

    messages = [
        {
            "role": "user",
            "content": "What is the weather in Paris?"
        }
    ]

    result = llm_agent.execute(messages)
    print(result)
    """
    [
        {'role': 'system', 'content': 'Provide accurate answers.'}, 
        {'role': 'system', 'content': 'Provide accurate answers.'}, 
        {'role': 'user', 'content': 'What is the weather in Paris?'}, 
        {'role': 'assistant', 'content': '', 'tool_calls': [{'function': {'name': 'get_current_whether', 'arguments': {'city_name': 'Paris'}}}]}, 
        {'role': 'tool', 'content': "{'temperature': 6.850000000000023, 'description': 'overcast clouds', 'humidity': 91}"}, 
        {'role': 'assistant', 'content': 'The current weather in Paris is overcast with a temperature of 6.85°C (40.37°F) and high humidity at 91%.'}
    ]

    """

```




## Key Features | TODOS

- **Flow Orchestration:** Build scalable workflows using Flyte.
- **Agent Management:** Manage agents for tasks like LLM interactions, RAG, and program execution.
- **LLM Integration:** Connect to local and cloud-based LLMs (e.g., OpenAI, Hugging Face).
- **RAG Support:** Enable contextual workflows with document retrieval and embeddings.
- **STT/TTS:** Convert speech to text and text to speech for interactive workflows.
- **Error Recovery:** Built-in mechanisms for handling errors and retries.
- **Extensible:** Modular architecture allows customization and scalability.