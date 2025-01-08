from abc import ABC, abstractmethod
import json
from typing import List, Dict, Any
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry
from fluxion.core.agent import AgentCallingWrapper

""" 
fluxion.modules.planning_module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module provides a reusable module for generating and executing task plans.
"""

class PlanningModule(ABC):
    """
    Abstract base class for planning modules that generate and execute task plans.
    """

    @abstractmethod
    def generate_plan(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate a structured task plan.

        Args:
            task (str): The task description.
            context (Dict[str, Any], optional): Additional context for planning.

        Returns:
            List[Dict[str, Any]]: A list of actions representing the plan.
        """
        pass

    def execute_plan(self, plan: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute a structured task plan.

        Args:
            plan (List[Dict[str, Any]]): A list of actions representing the plan.

        Returns:
            List[Any]: Results of each action in the plan.
        """
        results = []
        for step in plan:
            try:
                result = self.execute_action(step)
                results.append(result)
            except Exception as e:
                on_error = step.get("on_error", "terminate")
                if on_error == "skip":
                    results.append({"status": "skipped", "action": step})
                elif on_error == "terminate":
                    raise RuntimeError(f"Execution terminated due to error in step: {step}") from e
        return results

    def execute_action(self, action: Dict[str, Any]) -> Any:
        """
        Execute a single action (tool_call or agent_call).

        Args:
            action (Dict[str, Any]): The action to execute.

        Returns:
            Any: The result of the action.
        """
        if action["action"] == "tool_call":
            return self.invoke_tool(action)
        elif action["action"] == "agent_call":
            return self.invoke_agent(action)
        raise ValueError(f"Unsupported action type: {action['action']}")

    def invoke_tool(self, action: Dict[str, Any]) -> Any:
        """
        Invoke a tool based on the action.

        Args:
            action (Dict[str, Any]): The action containing tool details.

        Returns:
            Any: The result of the tool call.
        """
        tool_name = action["tool"]
        tool_input = action["input"]
        # Mocked tool invocation
        return {"tool_result": f"Executed tool {tool_name} with input {tool_input}"}

    def invoke_agent(self, action: Dict[str, Any]) -> Any:
        """
        Invoke another agent based on the action.

        Args:
            action (Dict[str, Any]): The action containing agent details.

        Returns:
            Any: The result of the agent call.
        """
        agent_name = action["agent"]
        agent_input = action["input"]
        # Mocked agent invocation
        return {"agent_result": f"Called agent {agent_name} with input {agent_input}"}





class LlmPlanningModule(PlanningModule):
    """
    A planning module that generates plans using an LLM via LLMChatModule.
    """

    def __init__(self, llm_chat_module: LLMChatModule):
        """
        Initialize the LlmPlanningModule.

        Args:
            llm_chat_module (LLMChatModule): The LLMChatModule instance to use for generating plans.
        """
        self.llm_chat_module = llm_chat_module
        self.tool_registry = ToolRegistry()


    def generate_plan(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate a structured task plan using the LLM.

        Args:
            task (str): The task description.
            context (Dict[str, Any], optional): Additional context for planning.

        Returns:
            List[Dict[str, Any]]: A list of actions representing the plan.
        """
        # Prepare the prompt for the LLM
        prompt = (
            f"Task: {task}\n\n"
            "Generate a structured JSON plan for this task. Each step should include:\n"
            "- action (tool_call or agent_call)\n"
            "- description of the action\n"
            "- input data\n"
            "- on_error (retry, skip, or terminate)\n"
            "- max_retries (if applicable)\n\n"
            "Return the plan as a JSON object."
        )

        prompt += f"\nContext: {json.dumps(context, indent=2)}" if context else ""

        # Query the LLM
        response = self.llm_chat_module.execute(messages=[{"role": "user", "content": prompt}])

        # Parse the LLM's response into a plan
        try:
            plan = json.loads(response["content"])
            return plan["plan"]
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse plan from LLM response: {response}")

    def invoke_tool(self, action: Dict[str, Any]) -> Any:
        """
        Invoke a tool from the module's ToolRegistry.

        Args:
            action (Dict[str, Any]): The action containing tool details.

        Returns:
            Any: The result of the tool call.
        """
        tool_name = action["tool"]
        tool_input = action["input"]
        return self.tool_registry.invoke_tool_call({"function": {"name": tool_name, "arguments": tool_input}})
    

    def invoke_agent(self, action: Dict[str, Any]) -> Any:
        """
        Invoke another agent using the agent calling wrapper.

        Args:
            action (Dict[str, Any]): The action containing agent details.

        Returns:
            Any: The result of the agent call.
        """
        agent_name = action["agent"]
        agent_input = action["input"]
        max_retries = action.get("max_retries", 1)
        retry_backoff = action.get("retry_backoff", 0.5)
        fallback = action.get("fallback", None)

        
        return AgentCallingWrapper.call_agent(agent_name, agent_input, max_retries, retry_backoff, fallback)