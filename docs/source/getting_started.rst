Getting Started
===============

Fluxion is a modular Python library for building agentic workflows. This guide will help you get started.

Installation
------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.10+
- [Flyte](https://flyte.org) installed and configured
- Anaconda or virtual environment setup

Steps
~~~~~

1. Clone the repository:

.. code-block:: bash

   git clone
   cd fluxion

2. Set up an Anaconda environment:

.. code-block:: bash

   bash scripts/setup_env.sh

3. Run unit tests:

.. code-block:: bash

   bash scripts/run_tests.sh

Installation

To install Fluxion, run:

.. code-block:: bash

   pip install fluxion

Basic Concepts
--------------

Fluxion revolves around the following core concepts:

1. **Agents**:
   - Autonomous components designed to perform specific tasks.
   - Examples: `LLMQueryAgent`, `PlanningAgent`, `DelegationAgent`.

2. **Tools and Registries**:
   - Tools can be dynamically called by agents during workflow execution.
   - Registries manage agents, tools, and delegations.

3. **Workflows**:
   - Orchestrated sequences of tasks with dependencies.
   - Created using `AgentNode` and `AbstractWorkflow`.

4. **Modules**:
   - Extend Fluxion’s functionality, such as connecting to LLMs (`LLMQueryModule`, `LLMChatModule`).

---

Your First Workflow
--------------------

### Step 1: Create an Agent
Define a custom agent that performs a simple task:

```python
from fluxion.core.agents.agent import Agent

class HelloWorldAgent(Agent):
    def execute(self, name: str) -> dict:
        return {"message": f"Hello, {name}!"}

agent = HelloWorldAgent(name="HelloAgent")
```

### Step 2: Define a Workflow
Create a workflow that uses the agent:

```python
from fluxion.workflows.agent_node import AgentNode
from fluxion.workflows.abstract_workflow import AbstractWorkflow

class HelloWorldWorkflow(AbstractWorkflow):
    def define_workflow(self):
        node = AgentNode(name="HelloNode", agent=HelloWorldAgent("HelloAgent"))
        self.add_node(node)

workflow = HelloWorldWorkflow(name="HelloWorldWorkflow")
```

### Step 3: Execute the Workflow
Run the workflow and view results:

```python
results = workflow.execute(inputs={"HelloNode.name": "Fluxion"})
print(results["HelloNode"]["message"])  # Output: Hello, Fluxion!
```

---

Next Steps
----------

- Explore the [Documentation](https://ymitiku.github.io/fluxion/) for advanced usage.
- Learn about [Agent Coordination](#).
- Join the community discussions on [GitHub](https://github.com/ymitiku/fluxion).

---

Congratulations! You've taken the first step toward mastering Fluxion. Let us know how we can improve or help you achieve your goals.
