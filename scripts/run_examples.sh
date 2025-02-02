export PYTHONPATH=$PYTHONPATH:./src
source activate fluxion-env

# echo "Running LLM Query example"
# python scripts/examples/llm_query_example.py

# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running RAG example"
# python scripts/examples/rag_example.py

# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running LLM with tool call example"
# python scripts/examples/llm_with_tool_call_example.py

# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running planning example"
# python scripts/examples/planning_example.py


# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running Workflow creation example"
# python scripts/examples/workflow_creation_example.py

echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "Running chatbot example"
python scripts/examples/chatbot_example.py

# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running agent coordination example"
# python scripts/examples/agent_coordination_example.py

# echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
# echo "Running delegation agent example"
# python scripts/examples/delegation_agent_example.py