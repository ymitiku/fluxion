from flytekit import workflow, task

class FlowOrchestrator:
    """
    Manages the orchestration of workflows using Flyte.
    """

    def __init__(self):
        self.flows = {}

    def register_flow(self, name: str, flow_func: callable):
        """
        Registers a workflow with the orchestrator.

        Args:
            name (str): The name of the workflow.
            flow_func (callable): The Flyte workflow function.
        """
        if name in self.flows:
            raise ValueError(f"Workflow with name '{name}' is already registered.")
        self.flows[name] = flow_func

    def list_flows(self):
        """
        Lists all registered workflows.

        Returns:
            list: Names of registered workflows.
        """
        return list(self.flows.keys())

    def execute_flow(self, name: str, **kwargs):
        """
        Executes a registered workflow.

        Args:
            name (str): The name of the workflow.
            **kwargs: Parameters to pass to the workflow.

        Returns:
            The result of the workflow execution.
        """
        if name not in self.flows:
            raise ValueError(f"No workflow found with name '{name}'.")
        return self.flows[name](**kwargs)

# Example Flyte Tasks and Workflow
@task
def hello_task(name: str) -> str:
    return f"Hello, {name}!"

@workflow
def hello_workflow(name: str) -> str:
    return hello_task(name=name)

# Example usage
if __name__ == "__main__":
    orchestrator = FlowOrchestrator()
    orchestrator.register_flow("hello_world", hello_workflow)

    print(f"Available Flows: {orchestrator.list_flows()}")
    result = orchestrator.execute_flow("hello_world", name="Fluxion")
    print(f"Workflow Result: {result}")
