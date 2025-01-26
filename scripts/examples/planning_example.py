from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.agents.planning_agent import PlanningAgent

# Initialize LLM modules (mock or real)
llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2", timeout=120)
llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)

# Initialize the Planning Agent
planning_agent = PlanningAgent(
    name="ExamplePlanningAgent",
    llm_module=llm_chat_module,
    llm_query_module=llm_query_module
)

# Define task, goals, and constraints
task = "Analyze customer feedback and generate a report."
goals = ["Summarize customer feedback from CSV data", "Identify common issues", "Generate a detailed report"]
constraints = ["Use only CSV data", "Complete within 24 hours"]

# Execute the planning process
try:
    # Step 1: Generate the plan
    final_response = planning_agent.plan_and_execute(task=task, goals=goals, constraints=constraints)
    # Step 2: Display the plan
    print("Generated Plan:")
    print(final_response["plan"].model_dump_json(indent=2))

    # Step 3: Display the execution log
    print("\nExecution Log:")
    for step_result in final_response["execution_log"]:
        print(f"Step {step_result.step_number}: {step_result.status}")
        for action in step_result.actions:
            print(f"  - Action: {action['action']} | Status: {action['status']} | Result: {action.get('result', 'No result')}")

    print("Final summary:", final_response["summary"])

except Exception as e:
    print(f"Error during planning or execution: {e}")
