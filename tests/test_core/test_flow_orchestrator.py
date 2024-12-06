import pytest
from flytekit import workflow, task
from fluxion.core.flow_orchestrator import FlowOrchestrator

# Define test Flyte tasks and workflows
@task
def get_task(task_name: str) -> str:
    return f"Test Task: {task_name}"

@workflow
def get_workflow(flow_name: str) -> str:
    return get_task(task_name=flow_name)

def test_register_and_list_flows():
    orchestrator = FlowOrchestrator()
    orchestrator.register_flow("test_flow", get_workflow)

    # Check if the flow is registered
    assert "test_flow" in orchestrator.list_flows()

def test_execute_flow():
    orchestrator = FlowOrchestrator()
    orchestrator.register_flow("test_flow", get_workflow)

    # Execute the flow and verify output
    result = orchestrator.execute_flow("test_flow", flow_name="Fluxion")
    assert result == "Test Task: Fluxion"

def test_register_duplicate_flow():
    orchestrator = FlowOrchestrator()
    orchestrator.register_flow("test_flow", get_workflow)

    # Attempt to register the same flow again
    with pytest.raises(ValueError, match="Workflow with name 'test_flow' is already registered."):
        orchestrator.register_flow("test_flow", get_workflow)

def test_execute_unregistered_flow():
    orchestrator = FlowOrchestrator()

    # Attempt to execute a non-existent flow
    with pytest.raises(ValueError, match="No workflow found with name 'non_existent_flow'."):
        orchestrator.execute_flow("non_existent_flow", flow_name="Fluxion")
