from abc import ABC, abstractmethod
import json
import logging
from typing import Any, Dict, List
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.registry.tool_registry import ToolRegistry, call_agent
from fluxion.models.plan_model import Plan, PlanStep

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
    def generate_plan(self, task: str, context: Dict[str, Any] = None) -> Plan:
        """
        Generate a structured task plan.

        Args:
            task (str): The task description.
            context (Dict[str, Any], optional): Additional context for planning.

        Returns:
            Plan: A structured task plan.
        """
        pass

    def execute_plan(self, plan: Plan) -> List[Any]:
        """
        Execute a structured task plan.

        Args:
            plan (Plan): The structured task plan.

        Returns:
            List[Any]: Results of each action in the plan.
        """
        results = []
        for step in plan.steps:
            try:
                result = self.execute_action(step)
                results.append(result)
            except Exception as e:
                if step.on_error == "skip":
                    results.append({"status": "skipped", "step": step.dict()})
                elif step.on_error == "terminate":
                    raise RuntimeError(f"Execution terminated due to error in step: {step}") from e
        return results

    def execute_action(self, step: PlanStep) -> Any:
        """
        Execute a single step in the plan.

        Args:
            step (PlanStep): The step to execute.

        Returns:
            Any: The result of the action.
        """
        if step.action == "tool_call":
            return self.invoke_tool(step)
        elif step.action == "agent_call":
            return self.invoke_agent(step)
        raise ValueError(f"Unsupported action type: {step.action}")

    @abstractmethod
    def invoke_tool(self, step: PlanStep) -> Any:
        """
        Invoke a tool based on the step.

        Args:
            step (PlanStep): The step containing tool details.

        Returns:
            Any: The result of the tool call.
        """
        
    @abstractmethod
    def invoke_agent(self, step: PlanStep) -> Any:
        """
        Invoke another agent using the agent calling wrapper.

        Args:
            step (PlanStep): The step containing agent details.

        Returns:
            Any: The result of the agent call.
        """
        pass


class LlmPlanningModule(PlanningModule):
    """
    A planning module that generates plans using an LLM via LLMChatModule.
    """

    def __init__(self, llm_chat_module: LLMChatModule, agent_group: str= None):
        """
        Initialize the LlmPlanningModule.

        Args:
            llm_chat_module (LLMChatModule): The LLMChatModule instance to use for generating plans.
        """
        self.llm_chat_module = llm_chat_module
        self.tool_registry = ToolRegistry()
        self.agent_group = agent_group
        self.tool_registry.register_tool(call_agent)

    def generate_plan(self, task: str, context: Dict[str, Any] = None) -> Plan:
        """
        Generate a structured task plan using the LLM.

        Args:
            task (str): The task description.
            context (Dict[str, Any], optional): Additional context for planning.

        Returns:
            Plan: A structured task plan.
        """
        # Prepare the prompt for the LLM
        agent_metadata = AgentRegistry.get_agent_metadata(self.agent_group)

        if not agent_metadata:
            logging.warning("No agents available for task planning.")

        prompt = self._construct_prompt(task, agent_metadata, self.tool_registry.list_tools(), context)

        system_instruction = self._construct_system_instruction()

        messages = [{"role": "system", "content": system_instruction}] if system_instruction else []
        messages.append({"role": "user", "content": prompt})

        # Get tools from the agent's ToolRegistry
        tools = [{"type": "function", "function": tool} for _, tool in self.tool_registry.list_tools().items()]


        # Query the LLM
        response = self.llm_chat_module.execute(messages=messages, tools=tools)

        # Parse the LLM's response into a plan
        try:
            parsed_plan = json.loads(response["content"])
            return Plan(**parsed_plan)
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse plan for task '{task}' with response: {response}")
            raise ValueError(f"Failed to parse plan from LLM response: {response}") from e
        
    
    def _construct_prompt(self, task: str, agent_metadata: List[Dict[str, Any]], tools_metadata: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """
        Construct the user prompt for the LLM.

        Args:
            task (str): The task description.
            agent_metadata (List[Dict[str, Any]]): Metadata for available agents.
            tools_metadata (List[Dict[str, Any]]): Metadata for available tools.
            context (Dict[str, Any]): Additional task context.

        Returns:
            str: The constructed prompt.
        """
        return (
            f"Task: {task}\n\n"
            f"Context: {json.dumps(context, indent=2) if context else 'None'}\n\n"
            f"List of available agents for calling:\n{json.dumps(agent_metadata, indent=2)}\n\n"
            f"Schema for the plan:\n{Plan.schema_as_json()}\n\n"
            f"Generate a structured plan based on the schema."
        )

    def _construct_system_instruction(self) -> str:
        """
        Construct the system instruction for the LLM.

        Returns:
            str: The system instruction.
        """
        return (
            "You are an intelligent agent that generates robust plans for given tasks.\n"
            "You have access to tools and agents to accomplish these tasks.\n"
            "You will receive a task description, context, and a schema for the plan.\n"
            "Generate a structured plan based on the schema provided."
        )


    def invoke_tool(self, step: PlanStep) -> Any:
        """
        Invoke a tool based on the step.

        Args:
            step (PlanStep): The step containing tool details.

        Returns:
            Any: The result of the tool call.
        """
        return self.tool_registry.invoke_tool_call({"function": {"name": step.input["tool"], "arguments": step.input}})

    def invoke_agent(self, step: PlanStep) -> Any:
        """
        Invoke another agent using the agent calling wrapper.

        Args:
            step (PlanStep): The step containing agent details.

        Returns:
            Any: The result of the agent call.
        """
        inputs = step.input
        agent_name = inputs.pop("agent_name")
        
        return call_agent(
            agent_name=agent_name,
            inputs=inputs,
            max_retries=step.max_retries,
            retry_backoff=step.retry_backoff,
            fallback=step.fallback,
        )