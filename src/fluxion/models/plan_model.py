from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class PlanStep(BaseModel):
    step_number: int
    description: str
    actions: List[str]
    dependencies: List[int] = []

class Plan(BaseModel):
    task: str
    steps: List[PlanStep]


# Define the structure of a step's execution result
class StepExecutionResult(BaseModel):
    step_number: int
    description: str
    status: str  # e.g., "Pending", "In Progress", "Completed", "Failed"
    actions: List[Dict[str, str]]  # {"action": <str>, "status": <str>, "result": <str>}
    result: str = None