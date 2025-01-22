from fluxon.parser import parse_json_with_recovery
import json
import logging
from typing import Any, Dict, List, Tuple
from fluxion.core.agents.llm_agent import LLMQueryAgent, LLMChatAgent
from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.models.plan_model import Plan, PlanStep, StepExecutionResult
from fluxion.models.message_model import MessageHistory, Message

class PlanGenerationAgent(LLMQueryAgent):
    """ An agent that generates a structured plan for a given task using an LLM. 

    PlanGenerationAgent:
    example-usage::
        from fluxion.core.agents.planning_agent import PlanGenerationAgent
        from fluxion.core.modules.llm_modules import LLMQueryModule

        llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/query", model="llama3.2", timeout=120)
        plan_generation_agent = PlanGenerationAgent(name="PlanGenerationAgent", llm_module=llm_query_module)

        task = "Develop a mobile application for tracking fitness goals."
        goals = ["Create user interface", "Implement data storage"]
        constraints = ["Use a cross-platform framework", "Complete within 2 weeks"]

        plan = plan_generation_agent.execute(task, goals, constraints)
        print("Generated Plan


    """
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or  (
            "You are an expert planner tasked with designing a structured, executable plan for the following task.\n"
            "You will receive a task description, goals, and constraints for the plan.\n"
            "Provide a plan in the specified JSON format with detailed steps to accomplish the task.\n\n"
            "Use the following JSON schema to define the plan:\n"
            "{\n"
            "  \"steps\": [\n"
            "    {\n"
            "      \"step_number\": <int>,\n"
            "      \"description\": \"<description of the step>\",\n"
            "      \"actions\": [\"<action 1>\", \"<action 2>\", ...],\n"
            "      \"dependencies\": [<step_number>, <step_number>, ...]\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n"
            "Only use actions that are relevant to the task.\n"
            "Do not make any assumptions about the task other than the given description and context.\n"
            "Do not include any additional information in your output.\n"
        )

    def execute(self, messages: MessageHistory) -> MessageHistory:
        output = super().execute(messages)
        return output[-1]
    
        

    def generate_plan(self, task: str, goals: List[str], constraints: List[str] = []) -> Plan:
        logging.info(f"{self.name}: Generating a structured plan for the task...")
        prompt = self.generate_structured_planning_prompt(task, goals, constraints)
        messages = MessageHistory(messages = [Message(role="user", content=prompt)])
        response = self.execute(messages)
        try:
            response = parse_json_with_recovery(response.content)
            response["task"] = task
            return Plan.model_validate_json(json.dumps(response))
        except Exception as e:
            logging.error(f"Failed to parse the generated plan: {str(e)}")
            raise ValueError(f"Failed to parse the generated plan: {str(e)}")

    def generate_structured_planning_prompt(self, task: str, goals: List[str], constraints: List[str] = []) -> str:
        prompt = self.system_instructions + "\n\n"
        prompt += f"Task: {task}\n"
        prompt += "Goals:\n" + "\n".join([f"- {goal}" for goal in goals]) + "\n"
        prompt += "Constraints:\n" + "\n".join([f"- {constraint}" for constraint in constraints]) + "\n"
        return prompt


# Plan Execution Agent with Enhanced Context
class PlanExecutionAgent(LLMChatAgent):
    """ An agent that executes a structured plan step by step using an LLM.

    PlanExecutionAgent:
    example-usage::
        from fluxion.core.agents.planning_agent import PlanExecutionAgent
        from fluxion.core.modules.llm_modules import LLMQueryModule

        llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/query", model="llama3.2", timeout=120)
        plan_execution_agent = PlanExecutionAgent(name="PlanExecutionAgent", llm_module=llm_query_module)
        
        # Define a structured plan
        plan = {
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

        execution_log = plan_execution_agent.execute_plan(plan)
        print("Execution Log:", execution_log)

    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the PlanExecutionAgent with an LLM module and broader task context.

        Args:
            name (str): Name of the agent.
            llm_module (LLMQueryModule): LLMQueryModule for executing actions.
            task (str): The broader task the plan is solving.
        """
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or (
            f"You are an intelligent assistant helping execute a task.\n"
            "You will receive the following information from the user\n"
            "- Broader task context\n"
            "- Results of previously completed actions\n"
            "- Current step description\n"
            "- Action to execute\n"
            "Your goal is to assist in executing the task by providing the necessary information and guidance.\n"
        )

        self.execution_log: List[StepExecutionResult] = []
        logging.basicConfig(level=logging.INFO)

    def execute_plan(self, plan: Plan) -> List[StepExecutionResult]:
        """
        Execute a structured plan step by step using the LLM.

        Args:
            plan (Plan): The structured plan to execute.

        Returns:
            List[StepExecutionResult]: A log of execution results for each step.
        """
        logging.info(f"{self.name}: Starting execution of the plan...")
        completed_steps = set()

        for step in sorted(plan.steps, key=lambda x: x.step_number):
            if not self._can_execute(step, completed_steps):
                logging.warning(
                    f"Step {step.step_number} cannot be executed yet. Dependencies: {step.dependencies}"
                )
                continue

            step_result = StepExecutionResult(
                step_number=step.step_number,
                description=step.description,
                status="In Progress",
                actions=[]
            )
            logging.info(f"Executing Step {step.step_number}: {step.description}")
            there_is_action_success = False
            for action in step.actions:
                action_execution_result = self.execute_action(plan.task, action, step.description)
                step_result.actions.append({
                    "action": action,
                    "status": action_execution_result.get("status", "failed"),
                    "result": action_execution_result.get("result", None)
                })
                if action_execution_result.get("status", "failed") == "done":
                    there_is_action_success = True
            
            if there_is_action_success:
                step_result.status = "Completed"
                completed_steps.add(step.step_number)
            else:
                step_result.status = "Failed"
                

            logging.info(f"Step {step.step_number} completed with status: {step_result.status}")

            self.execution_log.append(step_result)

        return self.execution_log
    
    def construct_planning_prompt(self, task: str, step_description: str, action: str) -> MessageHistory:
        previous_results = self._gather_previous_results()
        prompt =  (
            f"The broader task is: {task}\n\n"
            f"The current step of the task is:\n"
            f"Step Description: {step_description}\n\n"
            f"The results of previously completed actions are as follows:\n"
            f"{previous_results}\n\n"
            f"Your goal is to execute the following action:\n"
            f"Action: {action}\n\n"
            f"Please note: You do not need to execute the entire task, only the specific action within this step."
            "Generate tool call only if there is a need to use a tool for the action.\n"
            "Respond with the following structured format:\n"
            "{\n"
            "  \"result\": \"<result of the action>\",\n"
            "  \"status\": \"<done|failed>\"\n"
            "}"
            "Strictly adhere to the format to ensure proper processing."
        )

        return MessageHistory(messages=[Message(role="user", content=prompt)])


    def execute_action(self, task: str, action: str, step_description: str) -> Tuple[str, str]:
        """
        Execute a single action using the LLM with broader task context.

        Args:
            task (str): The broader task context.
            action (str): The action to execute.
            step_description (str): Description of the current step.

        Returns:
            tuple: (status of execution, result of the action).
        """
        try:
            # Gather results of previous actions
            logging.info(f"Querying LLM to execute action: {action}")
            response = super().execute(messages = self.construct_planning_prompt(task, step_description, action))
            try:
                output = parse_json_with_recovery(response[-1].content)
                if output == {}:
                    return {"status": "failed", "result": "Failed to parse the response"}
                return output
            except Exception as e:
                return {"status": "failed", "result": f"Failed to parse the response: {str(e)}"}

            # Assuming a successful response indicates completion
        except Exception as e:
            logging.error(f"Action execution failed: {action}. Error: {e}")
            return "Failed", str(e)

    def _can_execute(self, step: PlanStep, completed_steps: set) -> bool:
        """ Check if a step can be executed based on completed steps.

        Args:
            step (PlanStep): The step to check for execution.
            completed_steps (set): A set of completed step numbers.

        Returns:
            bool: True if the step can be executed, False otherwise.
        """
        unmet_dependencies = [dep for dep in step.dependencies if dep not in completed_steps]
        if unmet_dependencies:
            logging.warning(f"Step {step.step_number} has unmet dependencies: {unmet_dependencies}")
            return False
        return True


    def _gather_previous_results(self) -> str:
        """
        Gather results from previously executed actions.

        Returns:
            str: A summary of previous results as a formatted string.
        """
        results = []
        for result in self.execution_log:
            results.append(f"Step {result.step_number}: {result.status}")
            for action in result.actions:
                results.append(f"- Action: {action['action']} | Result: {action.get('result', 'No result')}")
        return "\n".join(results) if results else "No actions have been completed yet."

    def report_execution(self):
        """
        Report the execution log.
        """
        logging.info("Execution Report:")
        for result in self.execution_log:
            logging.info(f"Step {result.step_number}: {result.status}")
            for action in result.actions:
                logging.info(f"  - Action: {action['action']} | Status: {action['status']} | Result: {action.get('result', 'No result')}")


class PlanningAgent(LLMChatAgent):
    """ An agent that coordinates the planning and execution of a structured plan using an LLM.

    PlanningAgent:
    example-usage::
        from fluxion.core.agents.planning_agent import PlanningAgent
        from fluxion.core.modules.llm_modules import LLMQueryModule

        llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/query", model="llama3.2", timeout=120)
        llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)
        planning_agent = PlanningAgent(name="PlanningAgent", llm_module=llm_chat_module, llm_query_module=llm_query_module)

        task = "Develop a mobile application for tracking fitness goals."
        goals = ["Create user interface", "Implement data storage"]
        constraints = ["Use a cross-platform framework", "Complete within 2 weeks"]

        final_response = planning_agent.execute(task, goals, constraints)
        print("Final Response:", final_response)

    """
        

    def __init__(self, *args, llm_query_module: LLMQueryModule = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or (
            "You are an intelligent assist in summarizing action results.\n"
            "Another agent performed a series of actions and generated results.\n"
            "Your goal is to summarize the results and provide a high-level overview.\n"
            "You will receive the results of the actions and the broader task context.\n"
            "Provide a summary of the results and any additional insights.\n"
        )
        self.llm_query_module = llm_query_module
        self.plan_generation_agent = PlanGenerationAgent(name="{}.PlanGenerationAgent".format(self.name), llm_module=self.llm_query_module)
        self.execution_agent = PlanExecutionAgent(name="{}.PlanExecutionAgent".format(self.name), llm_module=self.llm_module)
    def plan_and_execute(self, task: str, goals: List[str], constraints: List[str] = []) -> Dict[str, Any]:
        
        plan = self.plan_generation_agent.generate_plan(task, goals, constraints)
        execution_log = self.execution_agent.execute_plan(plan)
        prompt = "Task: {}\n\nGoals:\n{}\n\nConstraints:\n{}".format(task, "\n".join([f"- {goal}" for goal in goals]), "\n".join([f"- {constraint}" for constraint in constraints]))
        prompt += "\n\nGenerated Plan:\n" +  json.dumps(plan.model_dump(), indent=2)
        prompt += "\n\nExecution Log:\n" + json.dumps([result.model_dump() for result in execution_log], indent=2)
        messages = MessageHistory(messages=[Message(role="user", content=prompt)])
        summary =  super().execute(messages=messages)
        return {
            "plan": plan,
            "execution_log": execution_log,
            "summary": summary
        }
        
    
        
if __name__ == "__main__":
    from googlesearch import search as google_search
    
    # Define the broader task
    task_description = "Develop a mobile application for tracking fitness goals."


    def initialize_repo(name: str) -> str:
        """ Create a GitHub repository with the given name. 
        
        Args:
            name (str): The name of the repository.

        Returns:
            str: A message indicating the repository creation status.
        """
        return f"Created GitHub repository: {name}"

    def implement_api(api_name: str, api_route: str) -> str:
        """ Implement an API endpoint in the project. 
        
        Args:
            api_name (str): The name of the API.
            api_route (str): The route of the API.

        Returns:
            str: A message indicating the API implementation status.
        """
        return f"Implemented API: {api_name} at route: {api_route}"
    
    def build_ui(ui_framework: str) -> str:
        """ Build the user interface using the specified framework. 
        
        Args:
            ui_framework (str): The UI framework to use.

        Returns:
            str: A message indicating the UI build status.
        """
        return f"Built UI using {ui_framework}"
    
    def add_payment_gateway(gateway_name: str) -> str:
        """ Integrate a payment gateway into the application. 
        
        Args:
            gateway_name (str): The name of the payment gateway.

        Returns:
            str: A message indicating the payment gateway integration status.
        """
        return f"Integrated {gateway_name} payment gateway"
    
    def search_on_internet(query: str) -> str:
        """ Search Online for the given query. It uses Google search API.
        
        Args:
            query (str): The search query.

        Returns:
            str: The search results in JSON format.
        """
        logging.info(f"Searching Google for: {query}")
        import re
        num_items = 5
        output = []
        for item in google_search(query, num_results=num_items, region="ie", advanced=True):
            # Remove brackets, quotes, and special characters from the title and description
            title = re.sub(r"[\"'[\]]", "", item.title)
            description = re.sub(r"[\"'[\]]", "", item.description)

            output.append(
                {
                    "title": title,
                    "description": description,
                }
            )
        return json.dumps(output)


    # Initialize the LLMQueryModule
    llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2", timeout=300)
    llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=300)

    # Intialize the PlanGenerationAgent
    planning_agent = PlanningAgent(name="PlanningAgent", llm_module=llm_chat_module, llm_query_module=llm_query_module)
    planning_agent.register_tools([initialize_repo, implement_api, build_ui, add_payment_gateway, search_on_internet])

    final_response = planning_agent.plan_and_execute(
        task = "Create a hello world program",
        goals = ["Print 'Hello, World!' to the console"],
        constraints = ["Use a programming language of your choice"]
    )

    print("Final Response:")
    print("Plan:", json.dumps(final_response["plan"].model_dump(), indent=2))
    print("Execution Log:", json.dumps([result.model_dump() for result in final_response["execution_log"]], indent=2))
    print("Summary:", "\n".join([message.content for message in final_response["summary"].messages]))
