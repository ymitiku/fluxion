export PYTHONPATH=$PYTHONPATH:./src
source activate fluxion-env


# python scripts/examples/llm_query_example.py
# python scripts/examples/rag_example.py
python scripts/examples/llm_with_tool_call_example.py