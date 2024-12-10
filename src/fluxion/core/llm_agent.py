from typing import Dict, List, Callable
from fluxion.core.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry


class LLMQueryAgent(Agent):
    """
    An agent that queries an LLM for a response.
    """
    def __init__(self, name: str, llm_module: LLMQueryModule, system_instructions: str = ""):
        """
        Initialize the LLMQueryAgent.

        Args:
            name (str): The unique name of the agent.
            llm_module (LLMQueryModule): The LLMQueryModule module.
            system_instructions (str): System instructions for the agent (default: "").
        """
        self.llm_module = llm_module
        super().__init__(name, system_instructions)

    def execute(self, query: str) -> str:
        """
        Execute the LLM query agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The response from the LLM.
        """
        if query.strip() == "":
            raise ValueError("Invalid query: Empty")
        prompt = self.system_instructions + "\n\n" + query if self.system_instructions else query
        return self.llm_module.execute(prompt=prompt)


class LLMChatAgent(Agent):
    """
    An agent that interacts with an LLM for chat and supports tool calls.
    """
    def __init__(self, name: str, llm_module: LLMChatModule, system_instructions: str = "", max_tool_call_depth: int = 2):
        """
        Initialize the LLMChatAgent.

        Args:
            name (str): The unique name of the agent.
            llm_module (LLMChatModule): The LLMChatModule module.
            system_instructions (str): System instructions for the agent (default: "").
        """
        self.llm_module = llm_module
        self.max_tool_call_depth = max_tool_call_depth
        self.tool_registry = ToolRegistry()
        super().__init__(name, system_instructions)


    def register_tool(self, func: Callable):
        """
        Register a tool function with the agent's ToolRegistry.

        Args:
            func (callable): The tool function to register.
        """
        self.tool_registry.register_tool(func)

    def execute(self, messages: List[Dict[str, str]], depth: int = 0) -> List[Dict[str, str]]:
        """
        Execute the LLM chat agent logic.

        Args:
            messages (List[Dict[str, str]]): The chat history, including the user query.

        Returns:
            List[Dict[str, str]]: The updated chat history with the LLM and tool responses.
        """
        if not isinstance(messages, list) or not all(
            isinstance(msg, dict) and "role" in msg and "content" in msg for msg in messages
        ):
            raise ValueError("Invalid messages: Must be a list of dictionaries with 'role' and 'content' keys.")

        if not messages:
            raise ValueError("Invalid messages: Empty list.")

        # Add system instructions as the first message, if provided
        system_message = {"role": "system", "content": self.system_instructions} if self.system_instructions else None
        if system_message:
            messages.insert(0, system_message)

        # Get tools from the agent's ToolRegistry
        tools = [{"type": "function", "function": tool} for _, tool in self.tool_registry.list_tools().items()]


        # Interact with the LLM
        response = self.llm_module.execute(messages=messages, tools=tools)
        messages.append(response)

        # Handle tool calls if present
        if "tool_calls" in response:
            for tool_call in response["tool_calls"]:
                tool_result = self._handle_tool_call(tool_call)
                messages.append({"role": "tool", "content": str(tool_result)})

            if depth < self.max_tool_call_depth:  # Prevent infinite recursion
                return self.execute(messages, depth=depth + 1)
        return messages

    def _handle_tool_call(self, tool_call: Dict[str, Dict]):
        """
        Handle a tool call response from the LLM.

        Args:
            tool_call (Dict[str, Dict]): The tool call details from the LLM response.

        Returns:
            str: The result of the tool invocation.
        """
        try:
            return self.tool_registry.invoke_tool_call(tool_call)
        except ValueError as ve:
            return f"Tool invocation failed: {ve}"
        except TypeError as te:
            return f"Tool invocation failed: {te}"
        except Exception as e:
            return f"Unexpected error during tool invocation: {e}"
        