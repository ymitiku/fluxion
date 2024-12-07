# Fluxion

![CI Workflow](https://github.com/ymitiku/fluxion/actions/workflows/ci.yml/badge.svg)


**Fluxion** is a Python library for building flow-based agentic workflows powered by [Flyte](https://flyte.org). It enables seamless orchestration of tasks, integration with language models (LLMs), retrieval-augmented generation (RAG), and program execution, along with speech-to-text (STT) and text-to-speech (TTS) capabilities.

## Key Features

- **Flow Orchestration:** Build scalable workflows using Flyte.
- **Agent Management:** Manage agents for tasks like LLM interactions, RAG, and program execution.
- **LLM Integration:** Connect to local and cloud-based LLMs (e.g., OpenAI, Hugging Face).
- **RAG Support:** Enable contextual workflows with document retrieval and embeddings.
- **STT/TTS:** Convert speech to text and text to speech for interactive workflows.
- **Error Recovery:** Built-in mechanisms for handling errors and retries.
- **Extensible:** Modular architecture allows customization and scalability.

---

## Installation

### Prerequisites

- Python 3.8+
- [Flyte](https://flyte.org) installed and configured
- Anaconda or virtual environment setup

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fluxion.git
   cd fluxion
   ```

2. Set up an Anaconda environment:

```bash
bash scripts/setup_env.sh
```

3. Run unit tests:

```bash

bash scripts/run_tests.sh
```


### Quick Start

1. Register and execute workflows

```python
from fluxion.core.flow_orchestrator import FlowOrchestrator

# Create an orchestrator instance
orchestrator = FlowOrchestrator()

# Register the workflow
orchestrator.register_flow("add_workflow", add_workflow)

# Execute the workflow
result = orchestrator.execute_flow("add_workflow", a=5, b=3)
print(f"Workflow Result: {result}")  # Output: 8

```


3. Register and use agents

```python
from fluxion.core.agent_manager import Agent

# Define a custom agent
class MultiplyAgent(Agent):
    def execute(self, input_data):
        return input_data * 2

# Register the agent
from fluxion.core.agent_manager import AgentManager
manager = AgentManager()
multiply_agent = MultiplyAgent(name="MultiplyAgent")
manager.register_agent("multiply_agent", multiply_agent)

# Execute the agent
result = manager.execute_agent("multiply_agent", 10)
print(f"Agent Result: {result}")  # Output: 20

```


### Contributing
Contributions are welcome! To get started:

- Fork the repository.
- Create a new branch (git checkout -b feature/my-feature).
- Commit your changes (git commit -m 'Add some feature').
- Push to the branch (git push origin feature/my-feature).
- Open a pull request.



### Roadmap
* Expand agent capabilities to support chaining and stateful workflows.
* Enhance error recovery with advanced fallback mechanisms.
* Add IoT and cloud service integration.
* Support for multi-language workflows.
* Interactive debugging and visualization tools.



### Acknowledgements
- Flyte for workflow orchestration.
- OpenAI and Hugging Face for LLM APIs.
- SpeechRecognition and pyttsx3 for STT and TTS.


Contact
For questions or support, feel free to open an issue or contact the maintainers.