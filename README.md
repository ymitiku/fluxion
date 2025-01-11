# [Fluxion](https://ymitiku.github.io/fluxion/)

![CI Workflow](https://github.com/ymitiku/fluxion/actions/workflows/ci.yml/badge.svg)

**Fluxion** is a Python library for orchestrating flow-based agentic workflows. Designed for modularity, scalability, and extensibility, it integrates seamlessly with locally or remotly hosted language models (LLMs) powered by [Ollama](https://ollama.com). Fluxion enables developers to build intelligent systems with capabilities like conversational interactions, tool calling, contextual reasoning, and decision-making.

---

## **Table of Contents**

- [Features](#features)
- [Installation](#installation)
- [Setting Up Ollama](#setting-up-ollama)
- [Usage](#usage)
  - [Calling Locally Hosted LLMs](#calling-locally-hosted-llms)
  - [Using Agents for Chat and Tool Calls](#using-agents-for-chat-and-tool-calls)
  - [Building Workflows](#building-workflows)
- [Architecture Overview](#architecture-overview)
- [Examples](#examples)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

---

## **Features**

- **Agent-Oriented Workflow Management:** Design agents that interact through modular workflows.
- **LLM Integration:** Seamlessly connect to locally hosted LLMs using [Ollama](https://ollama.com).
- **Perception and Environment Modeling:** Agents can perceive, process, and act on data from diverse sources.
- **Dynamic Tool Invocation:** Agents dynamically call registered tools with arguments generated at runtime.
- **Modular Architecture:** Create, register, and reuse components like agents, tools, and workflows.
- **Extensibility:** Add custom modules or agents without modifying core logic.
- **Visualization Support:** Visualize workflows for debugging and understanding execution flows.

---

## **Installation**

### **Prerequisites**

- Python 3.11+
- Anaconda or a virtual environment
- [Ollama](https://ollama.com/docs) installed for hosting LLMs
- System Dependencies:
  ```bash
  sudo apt install portaudio19-dev graphviz
  ```

### **Steps**

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ymitiku/fluxion.git
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

4. **Build Documentation (Optional):**
   ```bash
   bash scripts/build_docs.sh
   ```

---

## **Setting Up Ollama**

Fluxion uses [Ollama](https://ollama.com) to connect to locally hosted LLMs. Here's how to set it up:

1. **Install Ollama:**
   Follow the [Ollama Installation Guide](https://ollama.com/docs/installation).

2. **Download a Model:**
   ```bash
   ollama pull llama3.2
   ```

3. **Start the Ollama Server:**
   ```bash
   ollama serve
   ```

4. **Verify the Server:**
   Confirm it's running at `http://localhost:11434`.

---

## **Usage**

### **Calling Locally Hosted LLMs**

Use Fluxion to interact with locally hosted LLMs. For example:

```python
from fluxion.modules.llm_modules import LLMQueryModule, LLMChatModule

# Initialize the LLMQueryModule
llm_query = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
response = llm_query.execute(prompt="What is the capital of France?")
print("Query Response:", response)

# Initialize the LLMChatModule
llm_chat = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
response = llm_chat.execute(messages=[{"role": "user", "content": "Hello!"}])
print("Chat Response:", response)
```

---

### **Using Agents for Chat and Tool Calls**

Agents can perform tool calls dynamically:

```python
from fluxion.core.llm_agent import LLMChatAgent
from fluxion.modules.llm_modules import LLMChatModule

# Define a tool function
def get_weather(city_name: str) -> dict:
    return {"temperature": 20, "description": "sunny"}

# Initialize the LLMChatModule
llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

# Initialize the agent
llm_agent = LLMChatAgent(name="WeatherAgent", llm_module=llm_module)
llm_agent.register_tool(get_weather)

# Execute a conversation
messages = [{"role": "user", "content": "What's the weather in Paris?"}]
response = llm_agent.execute(messages=messages)
print("Chat with Tool Call Response:", response)
```

---


### **Using AgentCallingWrapper with LLMChatAgent**

`AgentCallingWrapper` allows dynamic invocation of agents, enabling seamless communication between agents in a modular workflow. It supports retries, backoff strategies, and fallback logic for robust execution.

Here’s how to integrate it with an `LLMChatAgent`:

```python
from fluxion.core.agent import AgentCallingWrapper
from fluxion.core.llm_agent import LLMChatAgent
from fluxion.modules.llm_modules import LLMChatModule

# Define a tool function
def get_weather(city_name: str) -> dict:
    return {"temperature": 20, "description": "sunny"}

# Initialize the LLMChatModule
llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

# Initialize the agent
llm_agent = LLMChatAgent(name="WeatherAgent", llm_module=llm_module)
llm_agent.register_tool(get_weather)

# Register AgentCallingWrapper for dynamic agent invocation
llm_agent.register_tool(AgentCallingWrapper.call_agent)
```

---

####  **Advanced Features**

1. **Retries**:
   - Specify the maximum number of retries for an agent call.
   - Use `retry_backoff` to introduce a delay between retries.

2. **Fallback Logic**:
   - Define a fallback function to handle cases where retries are exhausted.

3. **Example: Using Retries and Fallback**

```python
def fallback_logic(inputs):
    return {"message": "Unable to complete request. Please try again later."}

inputs = {"agent_name": "mock_agent", "inputs": {"value": 5}}

try:
    result = AgentCallingWrapper.call_agent(
        agent_name="mock_agent",
        inputs=inputs,
        max_retries=3,
        retry_backoff=0.5,
        fallback=fallback_logic,
    )
    print("Agent Result:", result)
except RuntimeError as e:
    print("Error calling agent:", e)
```

#### **What This Does:**
- Retries the agent call up to three times.
- Uses a backoff delay of 0.5 seconds between retries.
- Executes the fallback logic if all retries fail.

---

### **When to Use AgentCallingWrapper**
- **Inter-Agent Communication**:
  - When agents need to invoke other agents dynamically in workflows.
- **Error Recovery**:
  - To handle transient failures with retries or provide fallback results for irrecoverable errors.
- **Modular Workflow Design**:
  - Enables complex workflows with minimal coupling between agents.

---

### **Building Workflows**

Fluxion supports creating workflows using agent nodes:

```python
from fluxion.workflows.agent_node import AgentNode
from fluxion.workflows.abstract_workflow import AbstractWorkflow

class CustomWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node1 = AgentNode(name="Node1", agent=YourCustomAgent1())
        node2 = AgentNode(name="Node2", agent=YourCustomAgent2(), dependencies=[node1])
        self.add_node(node1)
        self.add_node(node2)

workflow = CustomWorkflow(name="ExampleWorkflow")
inputs = {"key": "value"}
results = workflow.execute(inputs=inputs)
print("Workflow Results:", results)
```

---

## **Architecture Overview**

Fluxion organizes its functionalities into the following key components:

1. **Agents:** Perform tasks such as querying LLMs or calling tools.
2. **Modules:** Include APIs, indexing, and retrieval modules.
3. **Workflows:** Define execution flows for agents.
4. **Registry:** Manage agents and tools for reuse.
5. **Visualization:** Visualize workflow graphs for clarity.

---

## **Examples**

For complete examples and tutorials, visit the [Fluxion Documentation](https://ymitiku.github.io/fluxion/).

---

## **Contributing**

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## **Roadmap**

- **Version 1.0.0:**
  - Complete core modules: Error recovery, program execution, and STT/TTS.
  - Enhance visualization support.
- **Future Versions:**
  - Reinforcement learning integrations.
  - Support for distributed workflows.
  - Plugin system for third-party integrations.

---

## **License**

This project is licensed under the [Apache License 2.0](LICENSE).
