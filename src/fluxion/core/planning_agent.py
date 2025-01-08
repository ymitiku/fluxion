from typing import Dict, Any
from fluxion.core.agent import Agent
from fluxion.modules.planning_module import PlanningModule

class PlanningAgent(Agent):
    """
    An agent capable of planning and executing tasks using a PlanningModule.
    """

    def __init__(self, name: str, planning_module: PlanningModule):
        super().__init__(name)
        self.planning_module = planning_module

    def execute(self, task: str) -> Any:
        """
        Generate and execute a plan for the given task.

        Args:
            task (str): The task description.

        Returns:
            Any: Results of the plan execution.
        """
        plan = self.planning_module.generate_plan(task)
        return self.planning_module.execute_plan(plan)
