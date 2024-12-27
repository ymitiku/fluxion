from flytekit import task, workflow, dynamic
from fluxion.workflows.abstract_workflow import AbstractWorkflow
from fluxion.workflows.agent_node import AgentNode
from typing import Any, Dict

class FlyteWorkflowAdapter:
    """
    Adapter to convert an AbstractWorkflow into a Flyte workflow.
    """

    def __init__(self, workflow: AbstractWorkflow):
        self.workflow = workflow

    def generate_flyte_workflow(self):
        """
        Converts the AbstractWorkflow into a Flyte workflow.

        Returns:
            Callable: A Flyte-compatible workflow function.
        """

        # Define a dynamic workflow at the module level
        return flyte_dynamic_workflow(self.workflow)

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the Flyte workflow with the given inputs.

        Args:
            inputs (Dict[str, Any]): Inputs to pass to the workflow.

        Returns:
            Dict[str, Any]: The results from executing the workflow.
        """
        flyte_workflow = self.generate_flyte_workflow()
        output =  flyte_workflow(inputs)
        print("output", output)
        return output


# Task to execute a single AgentNode
@task
def flyte_task(upstream_results: Dict[str, Any], node_inputs: Dict[str, Any], node_name: str, workflow: AbstractWorkflow) -> Dict[str, Any]:
    """
    Executes a single AgentNode as a Flyte task.

    Args:
        upstream_results (Dict[str, Any]): Results from previous nodes in the workflow.
        node_inputs (Dict[str, Any]): Inputs for the AgentNode.
        node_name (str): The name of the AgentNode.
        workflow (AbstractWorkflow): The parent workflow containing the nodes.

    Returns:
        Dict[str, Any]: The output from the node execution.
    """
    node = workflow.get_node_by_name(node_name)
    return node.execute(upstream_results, node_inputs)


# Dynamic workflow to orchestrate execution
@dynamic
def flyte_dynamic_workflow(workflow: AbstractWorkflow) -> Dict[str, Any]:
    """
    A Flyte dynamic workflow to execute nodes of the AbstractWorkflow.

    Args:
        workflow (AbstractWorkflow): The workflow to execute.

    Returns:
        Dict[str, Any]: The results from executing the workflow.
    """
    results = {}
    inputs = workflow.initial_inputs

    # Determine execution order and run nodes
    execution_order = workflow.determine_execution_order()
    for node_name in execution_order:
        node = workflow.get_node_by_name(node_name)
        all_inputs = {**inputs, **results}  # Combine inputs and previous results

        # Execute the node as a Flyte task
        node_result = flyte_task(results, inputs, node_name=node_name, workflow=workflow)
        results[node.name] = node_result

    return results
