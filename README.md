# [Fluxion](https://ymitiku.github.io/fluxion/)

![CI Workflow](https://github.com/ymitiku/fluxion/actions/workflows/ci.yml/badge.svg)

**Fluxion** is a Python library for building flow-based agentic workflows. Designed with extensibility and modularity in mind, it integrates seamlessly with locally hosted language models (LLMs) powered by [Ollama](https://ollama.com). Fluxion enables the creation of intelligent agents that perform tasks such as conversational interactions, tool calling, and contextual reasoning.

---

## **Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Setting Up Ollama](#setting-up-ollama)
- [Usage](#usage)
  - [Calling Locally Hosted LLMs](#calling-locally-hosted-llms)
  - [Using Agents for Chat and Tool Calls](#using-agents-for-chat-and-tool-calls)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**

- **Agent Management:** Design and execute agents for tasks like LLM interactions, tool calling, and contextual reasoning.
- **LLM Integration:** Connect to local LLMs hosted using [Ollama](https://ollama.com).
- **Tool Calling Support:** Agents can dynamically call functions with generated arguments.
- **Extensible Architecture:** Modular design allows for seamless customization and scalability.

---

## **Installation**

### **Prerequisites**

- Python 3.8+
- Anaconda or virtual environment setup
- [Ollama](https://ollama.com/docs) installed for hosting LLMs

### **Steps**

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/fluxion.git
   cd fluxion
   ```

2. **Set Up the Environment:**
   ```bash
   bash scripts/setup_env.sh
   ```

3. **Run Unit Tests:**
   ```bash
   bash scripts/run_tests.sh
   ```

---

## **Setting Up Ollama**

Fluxion is optimized for locally hosted LLMs using [Ollama](https://ollama.com). Follow these steps to set up your Ollama environment:

1. **Install Ollama:**
   - Visit the [Ollama Installation Guide](https://ollama.com/docs/installation) for detailed instructions.

2. **Download a Model:**
   - After installing Ollama, download a model (e.g., `llama3.2`):
     ```bash
     ollama pull llama3.2
     ```

3. **Start the Ollama Server:**
   - Run the Ollama server locally to host your model:
     ```bash
     ollama serve
     ```

4. **Verify the Server:**
   - Ensure the server is running and accessible at `http://localhost:11434`.

---

## **Usage**

### **Calling Locally Hosted LLMs**

You can use Fluxion to interact with locally hosted LLMs. Here's a basic example:

```python
from fluxion.modules.llm_modules import LLMQueryModule, LLMChatModule

# Initialize the LLMQueryModule
llm_query = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
response = llm_query.execute(prompt="What is the capital of France?")
print("Query Response:", response)

# Initialize the LLMChatModule
llm_chat = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
response = llm_chat.execute(messages=[
    {"role": "user", "content": "Hello!"}
])
print("Chat Response:", response)
```

### **Using Agents for Chat and Tool Calls**

Fluxion provides the `LLMChatAgent` class to manage conversations and tool calls:

```python
from fluxion.core.agent import LLMChatAgent
from fluxion.core.registry.tool_registry import ToolRegistry
from fluxion.modules.llm_modules import LLMChatModule

# Define a tool function
def get_weather(city_name: str) -> dict:
    """Returns dummy weather data."""
    return {"temperature": 20, "description": "sunny"}

# Register the tool
ToolRegistry.register_tool(get_weather)

# Initialize the LLMChatModule
llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

# Initialize the agent
llm_agent = LLMChatAgent(name="WeatherAgent", llm_module=llm_module)

# Execute a conversation
messages = [{"role": "user", "content": "What's the weather in Paris?"}]
response = llm_agent.execute(messages=messages)
print("Chat with Tool Call Response:", response)
```


---

## **Contributing**

We welcome contributions to Fluxion! See the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

---

## **License**

This project is licensed under the [Apache License 2.0](LICENSE). You may use, modify, and distribute this software in accordance with the terms specified in the license.

