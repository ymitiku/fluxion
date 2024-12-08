Getting Started
===============

Fluxion is a modular Python library for building agentic workflows. This guide will help you get started.

Installation
------------

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
