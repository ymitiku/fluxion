import json
import unittest
from unittest.mock import MagicMock
from fluxion.modules.planning_module import LlmPlanningModule
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry


class TestLlmPlanningModule(unittest.TestCase):
    def setUp(self):
        # Mock LLMChatModule
        self.mock_llm = MagicMock(spec=LLMChatModule)
        self.planning_module = LlmPlanningModule(llm_chat_module=self.mock_llm)
        self.planning_module.tool_registry = MagicMock(spec=ToolRegistry)

    def test_generate_plan(self):
        # Mock LLM response
        self.mock_llm.execute.return_value = {
            "content": json.dumps({
                "plan": [
                    {"action": "tool_call", "tool": "summarize", "input": {"text": "data"}, "on_error": "retry"}
                ]
            })
        }

        task = "Summarize sales data"
        plan = self.planning_module.generate_plan(task)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["action"], "tool_call")
        self.assertEqual(plan[0]["tool"], "summarize")

    def test_invoke_tool(self):
        # Mock tool registry behavior
        self.planning_module.tool_registry.invoke_tool_call.return_value = {"result": "success"}
        action = {"tool": "summarize", "input": {"text": "data"}}

        result = self.planning_module.invoke_tool(action)
        self.assertEqual(result["result"], "success")

    def test_invoke_agent(self):
        # Mock AgentCallingWrapper behavior
        from fluxion.core.agent import AgentCallingWrapper
        AgentCallingWrapper.call_agent = MagicMock(return_value={"status": "agent success"})
        action = {
            "action": "agent_call",
            "agent": "AnalysisAgent",
            "input": {"data": "summary"},
            "max_retries": 2
        }

        result = self.planning_module.invoke_agent(action)
        self.assertEqual(result["status"], "agent success")

    def test_execute_plan_with_error_handling(self):
        # Mock methods
        self.planning_module.invoke_tool = MagicMock(side_effect=RuntimeError("Mock failure"))
        self.planning_module.invoke_agent = MagicMock(return_value={"status": "success"})

        plan = [
            {"action": "tool_call", "tool": "summarize", "input": {"text": "data"}, "on_error": "skip"},
            {"action": "agent_call", "agent": "AnalysisAgent", "input": {"data": "summary"}}
        ]

        results = self.planning_module.execute_plan(plan)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["status"], "skipped")
        self.assertEqual(results[1]["status"], "success")


if __name__ == "__main__":
    unittest.main()
