# [<img src="readme-assets/images/fluxion-logo-rounded.png" width="27"/>](readme-assets/images/fluxion-logo-rounded.png)[Fluxion](https://ymitiku.github.io/fluxion/)

![CI Workflow](https://github.com/ymitiku/fluxion/actions/workflows/ci.yml/badge.svg)


**Fluxion** is a Python library for building and managing agentic workflows. Designed with modularity, scalability, and extensibility in mind, Fluxion simplifies the integration of locally or remotely hosted language models (LLMs) powered by [Ollama](https://ollama.com). By leveraging its robust architecture, developers can create intelligent systems capable of natural conversation, contextual reasoning, tool invocation, and autonomous decision-making, enabling seamless orchestration of complex, dynamic workflows.

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



## **Features**

Fluxion provides a powerful suite of tools and functionalities to enable the development of intelligent, flow-based workflows with ease and flexibility:

### 🧩 **Modular and Extensible Design**
- Build dynamic workflows by combining modular components that can easily be extended or customized for specific use cases.
- Integrate with various language models (LLMs), such as those powered by Ollama, while maintaining flexibility for custom implementations.

### 🤖 **Agent-Based Framework**
- Create and manage intelligent agents with capabilities for:
  - **Conversational Interactions**: Enable rich dialogue-based workflows.
  - **Decision-Making**: Empower agents to reason and make autonomous decisions.
  - **Delegation**: Assign tasks to specialized agents or fallback to a generic agent when required.

### ⚙️ **Tool Calling**
- Seamlessly invoke tools or external functions directly from LLM responses, including:
  - **Dynamic tool selection** based on task requirements.
  - Robust input validation and schema enforcement for safe and reliable tool usage.

### 📚 **Plan-Based Execution**
- Generate structured task plans with support for:
  - **High-Level Task Planning**: Automatically create step-by-step plans for complex workflows.
  - **Step Interpretation and Execution**: Execute tasks step-by-step, handling dependencies and failures gracefully.

### 🧠 **Contextual Reasoning**
- Leverage contextual information to improve decision-making and task execution:
  - Pass relevant task context to agents and tools.
  - Enhance LLM interactions with additional metadata, agent schemas, and task history.

### 🚦 **Agent Coordination and Delegation**
- Orchestrate multi-agent workflows:
  - Use the **CoordinationAgent** to dynamically assign tasks to appropriate agents.
  - Employ the **DelegationAgent** to delegate tasks intelligently based on task descriptions, available agents, and fallback strategies.

### 🌐 **LLM Integration**
- Connect seamlessly with locally or remotely hosted LLMs using:
  - High-performance APIs powered by Ollama.
  - Support for advanced LLM capabilities, including tool calls, chat, and query modules.

### 🛠️ **Built for Developers**
- Comprehensive and well-documented API with support for:
  - Easy-to-understand abstractions for workflows and agents.
  - Fine-grained control over execution flows and error handling.
  - A growing suite of examples and pre-built agents to accelerate development.
---

## **Installation**

### **Prerequisites**

- Python 3.11+
- Anaconda or a virtual environment
- [Ollama](https://ollama.com/docs) installed for hosting LLMs
- System Dependencies:
   * Ubuntu/Debian:
  ```bash
  sudo apt install portaudio19-dev graphviz
  ```
   * MacOS:
  ```bash
  brew install portaudio graphviz
  ```

### **Steps**

#### **GitHub Installation**

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/ymitiku/fluxion.git
   cd fluxion
   pip install -e .
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

#### **PyPI Installation**
```bash
pip install fluxion-ai-python
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

#### **Using generation endpoint:**
```python
from fluxion_ai.core.modules.llm_modules import LLMQueryModule

# Initialize the LLMQueryModule
llm_query = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
response = llm_query.execute(prompt="What is the capital of France?")
print("Query Response:", response)
# Query Response: The capital of France is Paris.
```

#### **Using chat endpoint:**

```python
from fluxion_ai.core.modules.llm_modules import LLMChatModule

# Initialize the LLMChatModule
llm_chat = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
messages = [
  {"role": "user", "content": "Hello!"},
]
response = llm_chat.execute(messages=messages)
print("Chat Response:", response)
# Chat Response: {'role': 'assistant', 'content': 'How can I assist you today?'}
```

---

### **Using Agents for Chat and Tool Calls**

Agents can perform tool calls dynamically:

```python
from fluxion_ai.core.agents.llm_agent import LLMChatAgent
from fluxion_ai.core.modules.llm_modules import LLMChatModule
from fluxion_ai.models.message_model import Message, MessageHistory
from fluxion_ai.core.registry.tool_registry import tool

# Define a tool function
@tool
def get_weather(city_name: str) -> dict:
    return {"temperature": 20, "description": "sunny"}

# Initialize the LLMChatModule
llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

# Initialize the agent
llm_agent = LLMChatAgent(name="WeatherAgent", llm_module=llm_module)
llm_agent.register_tool(get_weather)

# Execute a conversation
messages = MessageHistory(messages = [Message(role="user", content="What's the weather in Paris?")])
response = llm_agent.execute(messages=messages)
print("Chat with Tool Call Response:", response)
```

---


### **Using call_agent with LLMChatAgent**

`call_agent` allows dynamic invocation of agents, enabling seamless communication between agents in a modular workflow. It supports retries, backoff strategies, and fallback logic for robust execution.

Here’s how to integrate it with an `LLMChatAgent`:

```python
from fluxion_ai.core.registry.tool_registry import call_agent
from fluxion_ai.core.agents.llm_agent import LLMChatAgent
from fluxion_ai.core.modules.llm_modules import LLMChatModule
from fluxion_ai.core.registry.tool_registry import tool


# Define a tool function
@tool
def get_weather(city_name: str) -> dict:
    return {"temperature": 20, "description": "sunny"}

# Initialize the LLMChatModule
llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")

# Initialize the agent
llm_agent = LLMChatAgent(name="WeatherAgent", llm_module=llm_module)
llm_agent.register_tool(get_weather)

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

messages = MessageHistory(messages = [Message(role="user", content="What's capital of Ireland?")])
try:
    result = call_agent(
        agent_name="mock_agent",
        messages=messages,
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

### **When to Use call_agent**
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
from fluxion_ai.core.agents.llm_agent import LLMChatAgent
from fluxion_ai.core.modules.llm_modules import LLMChatModule
from fluxion_ai.workflows.agent_node import AgentNode
from fluxion_ai.workflows.abstract_workflow import AbstractWorkflow
from fluxion_ai.models.message_model import Message, MessageHistory

class CustomWorkflow(AbstractWorkflow):
    def define_workflow(self):
        module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
        agent1 = LLMChatAgent("Agent1", llm_module=module)
        agent2 = LLMChatAgent("Agent2", llm_module=module)
        node1 = AgentNode(name="Node1", agent=agent1)
        node2 = AgentNode(name="Node2", agent=agent2, inputs={"messages": "Node1"})
        
        self.add_node(node1)
        self.add_node(node2)

workflow = CustomWorkflow(name="ExampleWorkflow")
workflow.define_workflow()
inputs = {"messages": MessageHistory(messages=[Message(role="user", content="Hello!")])}
results = workflow.execute(inputs=inputs)
print("Workflow Results:", results)
```

---

## **Architecture Overview**

Fluxion is designed with a modular and extensible architecture that emphasizes scalability, interoperability, and flexibility. The following key components form the foundation of Fluxion's ecosystem:

### **1. Core Components**
- **Agents**
  - The primary building blocks for creating intelligent workflows. Each agent is specialized for a particular task or functionality.
  - Types of agents include:
    - **LLMQueryAgent**: Executes single-turn tasks and queries using a language model.
    - **LLMChatAgent**: Handles multi-turn conversations with memory and context support.
    - **PlanningAgent**: Generates structured plans and executes workflows step-by-step.
    - **CoordinationAgent**: Dynamically orchestrates tasks by selecting and calling appropriate agents or tools.
    - **DelegationAgent**: Delegates tasks intelligently to other agents or handles them directly using fallback mechanisms.
  
- **Tool Registry**
  - A centralized registry for managing tools that can be called by agents or workflows.
  - Ensures input validation, metadata management, and consistent integration with LLMs.

- **Agent Registry**
  - Tracks all available agents in the system, allowing agents to dynamically discover and collaborate with each other.
  - Provides metadata for agents, including input/output schemas and descriptions, to facilitate coordination.

### **2. Modules**
- **LLM Modules**
  - Abstractions for connecting to locally or remotely hosted language models, such as those powered by Ollama.
  - Modules include:
    - **LLMQueryModule**: Executes single-turn queries.
    - **LLMChatModule**: Manages multi-turn conversational interactions, tool calls, and delegation logic.

- **IR modules**
   - **EmbeddingApiModule**: EmbeddingApiModule is a module that provides an interface to the embedding API. It can be used to get embeddings for a given text.
   - **IndexingModule**: IndexingModule is a module that provides functionalities to build semantic search indexes which can be used to search for similar documents.
   - **RetrievalModule**: RetrievalModule is a module that provides functionalities to retrieve documents from a given index.



### **3. Workflow Execution**

Fluxion enables the construction, execution, and monitoring of agent-based workflows. It integrates key components like **AgentNodes**, **AbstractWorkflows**, and orchestration adapters for external platforms like Flyte.

- **AgentNode**: Represents a workflow step with an agent, its dependencies, inputs, and outputs. Ensures proper data flow and validates outputs.
- **AbstractWorkflow**: A base class for managing workflows. It handles node addition, dependency validation, execution order, and workflow execution, with visualization support for better clarity.
- **FlyteWorkflowAdapter**: Adapts Fluxion workflows for Flyte, converting `AbstractWorkflow` into Flyte-compatible workflows and enabling external orchestration.
- **WorkflowProgressTracker**: Tracks node status and execution times, offering progress updates for workflow monitoring.

Fluxion workflows are validated for dependencies and executed in the correct order. Nodes exchange data seamlessly, enabling smooth execution for both local and orchestrated environments.


### **4. Extensibility**
Fluxion is designed to be easily extendable:
- Add new agents with custom logic and integrate them seamlessly into workflows.
- Register custom tools with the Tool Registry to expand functionality.
- Extend the architecture by creating new modules, agents, or registries for specific domains or applications.

### **5. Key Design Principles**
- **Modularity**: All components are self-contained and can be used independently or as part of a larger workflow.
- **Interoperability**: Agents and tools communicate through well-defined interfaces and schemas.
- **Flexibility**: Supports a wide range of workflows, from simple task execution to complex multi-agent orchestration.
- **Scalability**: Built to handle diverse tasks and workloads without bottlenecks.

---


## **Examples**

For complete examples and tutorials, visit the [Fluxion Documentation](https://ymitiku.github.io/fluxion/).

---

## **Contributing**

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---


## **Vision and Goals**
Fluxion aims to become the comprehensive framework for building agentic workflows, empowering developers to:
- Design modular, extensible, and scalable intelligent systems.
- Seamlessly integrate advanced LLM capabilities for decision-making and automation.
- Simplify complex workflows through intuitive APIs, dynamic task orchestration, and robust execution monitoring.

Future updates will continue to focus on innovation, developer experience, and real-world applicability.

---

## **License**

This project is licensed under the [Apache License 2.0](LICENSE).


Copyright © 2025 [<img src="readme-assets/images/fluxion-logo-rounded.png" width="16"/>](readme-assets/images/fluxion-logo-rounded.png)Fluxion