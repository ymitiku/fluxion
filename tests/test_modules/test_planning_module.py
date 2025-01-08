import json
from pydantic import BaseModel
from typing import Dict, Any
import unittest
from unittest.mock import MagicMock, patch
from fluxion.modules.planning_module import LlmPlanningModule
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry, call_agent
from fluxion.models.plan_model import Plan, PlanStep
from fluxion.core.agent import Agent



class MockStructuredAgent(Agent):
    class InputSchema(BaseModel):
        summary: str

    class OutputSchema(BaseModel):
        result: str
        status: str

    def __init__(self, name: str):
        super().__init__(
            name=name,
            input_schema=MockStructuredAgent.InputSchema,
            output_schema=MockStructuredAgent.OutputSchema,
        )

    def execute(self, summary: str) -> Dict[str, Any]:
        return {"result": summary.upper(), "status": "agent success"}


class TestLlmPlanningModule(unittest.TestCase):
    def setUp(self):
        # Mock LLMChatModule
        self.mock_llm = MagicMock(spec=LLMChatModule)
        self.tool_registry = MagicMock(spec=ToolRegistry)

        # Create the planning module
        self.planning_module = LlmPlanningModule(llm_chat_module=self.mock_llm)
        self.planning_module.tool_registry = self.tool_registry

    def test_generate_plan(self):
        # Mock LLM response
        mock_response_content = {
            "task": "Summarize sales data",
            "context": {"region": "North America"},
            "steps": [
                {
                    "action": "tool_call",
                    "description": "Summarize data",
                    "input": {"data": "sales data"},
                    "on_error": "retry",
                    "max_retries": 3,
                }
            ],
        }
        self.mock_llm.execute.return_value = {"content": json.dumps(mock_response_content)}

        task = "Summarize sales data"
        context = {"region": "North America"}
        plan = self.planning_module.generate_plan(task, context)

        self.assertEqual(plan.task, "Summarize sales data")
        self.assertEqual(plan.context, context)
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].action, "tool_call")
        self.assertEqual(plan.steps[0].input["data"], "sales data")

    def test_invoke_tool(self):
        # Mock tool registry behavior
        self.tool_registry.invoke_tool_call.return_value = {"result": "success"}
        step = PlanStep(
            action="tool_call",
            description="Summarize data",
            input={"tool": "summarize", "data": "sales data"},
            on_error="retry",
        )

        result = self.planning_module.invoke_tool(step)
        self.assertEqual(result["result"], "success")
        self.tool_registry.invoke_tool_call.assert_called_once()

    
    def test_invoke_agent(self):
        # Mock call_agent behavior
        with patch("fluxion.modules.planning_module.call_agent", return_value={"status": "agent success", "result": "SUMMARY INPUT"}) as mock_call_agent:
            step = PlanStep(
                action="agent_call",
                description="Analyze data",
                input={"agent_name": "AnalysisAgent", "summary": "Summary input"},
                on_error="terminate",
                max_retries=2,
            )

            analysis_agent = MockStructuredAgent("AnalysisAgent")

            result = self.planning_module.invoke_agent(step)
            print("result", result)
            self.assertEqual(result["status"], "agent success")
            mock_call_agent.assert_called_once_with(
                agent_name="AnalysisAgent",
                inputs={"summary": "Summary input"},
                max_retries=2,
                retry_backoff=step.retry_backoff,
                fallback=step.fallback,
            )



    def test_execute_plan_with_error_handling(self):
        # Mock methods
        self.planning_module.invoke_tool = MagicMock(side_effect=RuntimeError("Mock failure"))
        self.planning_module.invoke_agent = MagicMock(return_value={"status": "success"})

        plan = Plan(
            task="Process sales data",
            steps=[
                PlanStep(
                    action="tool_call",
                    description="Summarize data",
                    input={"tool": "summarize", "data": "sales data"},
                    on_error="skip",
                ),
                PlanStep(
                    action="agent_call",
                    description="Analyze data",
                    input={"agent": "AnalysisAgent", "data": "summary"},
                    on_error="terminate",
                ),
            ],
        )

        results = self.planning_module.execute_plan(plan)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "skipped")
        self.assertEqual(results[1]["status"], "success")
        self.planning_module.invoke_tool.assert_called_once()
        self.planning_module.invoke_agent.assert_called_once()


if __name__ == "__main__":
    unittest.main()
