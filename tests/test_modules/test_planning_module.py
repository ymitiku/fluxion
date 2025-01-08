import json
import unittest
from unittest.mock import MagicMock
from fluxion.modules.planning_module import LlmPlanningModule
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry
from fluxion.models.plan_model import Plan, PlanStep


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
        # Mock AgentCallingWrapper behavior
        from fluxion.core.agent import AgentCallingWrapper
        AgentCallingWrapper.call_agent = MagicMock(return_value={"status": "agent success"})

        step = PlanStep(
            action="agent_call",
            description="Analyze data",
            input={"agent": "AnalysisAgent", "data": "summary"},
            on_error="terminate",
            max_retries=2,
        )

        result = self.planning_module.invoke_agent(step)
        self.assertEqual(result["status"], "agent success")
        AgentCallingWrapper.call_agent.assert_called_once()

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
