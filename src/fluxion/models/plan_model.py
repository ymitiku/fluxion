from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class ActionType(str, Enum):
    TOOL_CALL = "tool_call"
    AGENT_CALL = "agent_call"

class ErrorRecoveryStrategy(str, Enum):
    RETRY = "retry"
    SKIP = "skip"
    TERMINATE = "terminate"

class PlanStep(BaseModel):
    """
    Represents a single step in a task plan.
    """
    action: ActionType = Field(..., description="The type of action, e.g., 'tool_call' or 'agent_call'.")
    description: str = Field(..., description="A brief description of the action.")
    input: Dict[str, Any] = Field(..., description="The input data required for the action.")
    on_error: ErrorRecoveryStrategy = Field(ErrorRecoveryStrategy.TERMINATE, description="Error recovery strategy: retry, skip, or terminate.")
    max_retries: Optional[int] = Field(1, description="Maximum number of retries for the action.")
    retry_backoff: Optional[float] = Field(0.5, description="Backoff time in seconds between retries.")
    fallback: Optional[Dict[str, Any]] = Field(None, description="Fallback logic or data in case of failure.")

    @validator("action", pre=True)
    def validate_action(cls, value):
        """
        Normalize string inputs for action to match the ActionType enum.
        """
        if isinstance(value, str):
            try:
                return ActionType(value.lower())
            except ValueError:
                raise ValueError(f"Invalid action type: {value}")
        return value

    @validator("on_error", pre=True)
    def validate_on_error(cls, value):
        """
        Normalize string inputs for on_error to match the ErrorRecoveryStrategy enum.
        """
        if isinstance(value, str):
            try:
                return ErrorRecoveryStrategy(value.lower())
            except ValueError:
                raise ValueError(f"Invalid error recovery strategy: {value}")
        return value

class Plan(BaseModel):
    """
    Represents a structured task plan containing multiple steps.
    """
    task: str = Field(..., description="The high-level task description.")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the plan.")
    steps: List[PlanStep] = Field(..., description="The list of actions to execute as part of the plan.")

    def to_prompt(self) -> str:
        """
        Convert the plan to a JSON string formatted for an LLM prompt.

        Returns:
            str: The JSON representation of the plan formatted for the LLM.
        """
        return self.model_dump_json(indent=2)

    @staticmethod
    def schema_as_json() -> str:
        """
        Returns the JSON Schema of the Plan object for use in LLM prompts.

        Returns:
            str: JSON Schema representation of the Plan.
        """
        return Plan.model_json_schema()

# Example usage:
if __name__ == "__main__":
    example_plan = Plan(
        task="Analyze sales data and generate a report.",
        context={"region": "North America", "time_period": "Q4 2023"},
        steps=[
            PlanStep(
                action="tool_call",  # Strings will be converted to ActionType enums
                description="Summarize sales data",
                input={"data": "raw sales data"},
                on_error="retry",  # Strings will be converted to ErrorRecoveryStrategy enums
                max_retries=3
            ),
            PlanStep(
                action="agent_call",
                description="Analyze summarized data",
                input={"summary": "result from summarize"},
                on_error="terminate"
            ),
            PlanStep(
                action="tool_call",
                description="Generate a sales report",
                input={"analysis": "result from analyze"},
                on_error="skip"
            )
        ]
    )

    print("Plan as JSON for LLM Prompt:")
    print(example_plan.to_prompt())

    print("\nPlan Schema as JSON:")
    print(Plan.schema_as_json())
