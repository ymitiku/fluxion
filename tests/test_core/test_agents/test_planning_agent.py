import json
import unittest
from unittest.mock import MagicMock, patch
from fluxion.core.modules.llm_modules import LLMQueryModule
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.agents.planning_agent import PlanGenerationAgent, PlanExecutionAgent
from fluxion.models.plan_model import Plan, PlanStep, StepExecutionResult
from fluxon.parser import parse_json_with_recovery

class TestPlanGenerationAgent(unittest.TestCase):

    def setUp(self):
        # Mock LLMQueryModule
        AgentRegistry.clear_registry()
        self.mock_llm = MagicMock(spec=LLMQueryModule)
        self.agent = PlanGenerationAgent(name="PlanGenAgent", llm_module=self.mock_llm)

    def test_generate_structured_planning_prompt(self):
        task = "Analyze customer feedback"
        goals = ["Summarize feedback", "Identify common issues"]
        constraints = ["Use only CSV data", "Complete within 1 hour"]

        expected_prompt = (
            self.agent.system_instructions + "\n\n"
            "Task: Analyze customer feedback\n"
            "Goals:\n- Summarize feedback\n- Identify common issues\n"
            "Constraints:\n- Use only CSV data\n- Complete within 1 hour\n"
        )

        generated_prompt = self.agent.generate_structured_planning_prompt(task, goals, constraints)
        self.assertEqual(generated_prompt, expected_prompt)

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_execute_success(self, mock_parse_json_with_recovery):
        # Mock LLM response
        mock_response = {
            "steps": [
                {
                    "step_number": 1,
                    "description": "Load data from CSV",
                    "actions": ["LoadCSV"],
                    "dependencies": []
                },
                {
                    "step_number": 2,
                    "description": "Summarize data",
                    "actions": ["Summarize"],
                    "dependencies": [1]
                }
            ]
        }
        mock_parse_json_with_recovery.return_value = mock_response
        self.mock_llm.execute.return_value = json.dumps(mock_response)

        task = "Analyze customer feedback"
        goals = ["Summarize feedback", "Identify common issues"]
        constraints = []

        plan = self.agent.generate_plan(task, goals, constraints)
        
        self.assertIsInstance(plan, Plan)
        self.assertEqual(plan.task, task)
        self.assertEqual(len(plan.steps), 2)
        self.assertEqual(plan.steps[0].description, "Load data from CSV")

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_execute_invalid_response(self, mock_parse_json_with_recovery):
        # Mock invalid LLM response
        mock_parse_json_with_recovery.side_effect = ValueError("Invalid JSON format")
        self.mock_llm.execute.return_value = "Invalid response"

        task = "Analyze customer feedback"
        goals = ["Summarize feedback", "Identify common issues"]
        constraints = []

        with self.assertRaises(ValueError) as context:
            self.agent.generate_plan(task, goals, constraints)

        self.assertIn("Failed to parse the generated plan", str(context.exception))

    def test_generate_structured_planning_prompt_no_constraints(self):
        task = "Analyze customer feedback"
        goals = ["Summarize feedback", "Identify common issues"]
        
        expected_prompt = (
            self.agent.system_instructions + "\n\n"
            "Task: Analyze customer feedback\n"
            "Goals:\n- Summarize feedback\n- Identify common issues\n"
            "Constraints:\n\n"
        )

        generated_prompt = self.agent.generate_structured_planning_prompt(task, goals)
        self.assertEqual(generated_prompt, expected_prompt)




class TestPlanExecutionAgent(unittest.TestCase):

    def setUp(self):
        # Mock LLMChatModule
        AgentRegistry.clear_registry()
        self.mock_llm = MagicMock()
        self.agent = PlanExecutionAgent(name="PlanExecAgent", llm_module=self.mock_llm)

    def test_can_execute(self):
        step = PlanStep(step_number=2, description="Summarize data", actions=["Summarize"], dependencies=[1])
        completed_steps = {1}
        self.assertTrue(self.agent._can_execute(step, completed_steps))

        completed_steps = set()
        self.assertFalse(self.agent._can_execute(step, completed_steps))

    def test_gather_previous_results(self):
        self.agent.execution_log = [
            StepExecutionResult.parse_raw(json.dumps({
                "step_number": 1,
                "description": "Load data",
                "status": "Completed",
                "actions": [
                    {"action": "LoadCSV", "status": "done", "result": "Data loaded successfully"}
                ],
            })),
            StepExecutionResult.parse_raw(json.dumps({
                "step_number": 2,
                "description": "Summarize data",
                "status": "Failed",
                "actions": [
                    {"action": "Summarize", "status": "failed", "result": "Error in summarizing"}
                ],
            })),
        ]
        expected_result = (
            "Step 1: Completed\n"
            "- Action: LoadCSV | Result: Data loaded successfully\n"
            "Step 2: Failed\n"
            "- Action: Summarize | Result: Error in summarizing"
        )
        self.assertEqual(self.agent._gather_previous_results(), expected_result)

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_execute_action_success(self, mock_parse_json_with_recovery):
        mock_parse_json_with_recovery.return_value = {"status": "done", "result": "Action completed successfully"}
        self.mock_llm.execute.return_value = {"role": "assistant", "content": "{\"status\": \"done\", \"result\": \"Action completed successfully\"}"}

        result = self.agent.execute_action("Analyze feedback", "Summarize", "Summarize customer feedback")
        self.assertEqual(result, {"status": "done", "result": "Action completed successfully"})

    @patch("fluxon.parser.parse_json_with_recovery")
    def test_execute_action_failure(self, mock_parse_json_with_recovery):
        mock_parse_json_with_recovery.side_effect = ValueError("Invalid JSON")
        self.mock_llm.execute.return_value = {"role": "assistant", "content": "Invalid response"}
        

        result = self.agent.execute_action("Analyze feedback", "Summarize", "Summarize customer feedback")
        self.assertEqual(result["status"], "failed")
        self.assertIn("Failed to parse the response", result["result"])

    @patch("fluxion.core.agents.planning_agent.PlanExecutionAgent.execute_action")
    def test_execute_plan(self, mock_execute_action):
        mock_execute_action.side_effect = lambda task, action, desc: {
            "status": "done" if action == "LoadCSV" else "failed",
            "result": "Mock result",
        }

        plan = Plan(
            task="Analyze customer feedback",
            steps=[
                PlanStep(step_number=1, description="Load data", actions=["LoadCSV"], dependencies=[]),
                PlanStep(step_number=2, description="Summarize data", actions=["Summarize"], dependencies=[1]),
            ]
        )

        execution_log = self.agent.execute_plan(plan)

        self.assertEqual(len(execution_log), 2)
        self.assertEqual(execution_log[0].status, "Completed")
        self.assertEqual(execution_log[1].status, "Failed")

    def test_report_execution(self):
        self.agent.execution_log = [
            StepExecutionResult.parse_raw(json.dumps({
                "step_number": 1,
                "description": "Load data",
                "status": "Completed",
                "actions": [
                    {"action": "LoadCSV", "status": "done", "result": "Data loaded successfully"}
                ],
            }))
        ]
        with patch("logging.info") as mock_logging:
            self.agent.report_execution()
            mock_logging.assert_any_call("Step 1: Completed")
            mock_logging.assert_any_call("  - Action: LoadCSV | Status: done | Result: Data loaded successfully")



if __name__ == "__main__":
    unittest.main()
