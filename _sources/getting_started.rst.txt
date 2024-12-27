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

Quickstart
----------

Here’s a simple example to set up an agent:

.. code-block:: python

   from fluxion.modules.llm_modules import LLMQueryModule
   from fluxion.core.agent import LLMQueryAgent

   llm_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")
   agent = LLMQueryAgent(name="TestAgent", llm_module=llm_module)
   response = agent.execute(query="What is the capital of France?")
   print(response)
