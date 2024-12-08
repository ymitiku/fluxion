from typing import Dict, List
from abc import ABC, abstractmethod
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry

class Agent(ABC):
    """
    Abstract base class for all agents with unique name enforcement.
    """
    def __init__(self, name: str, system_instructions: str = ""):
        """
        Initialize the agent and register it.

        Args:
            name (str): The unique name of the agent.
            system_instructions (str): System instructions for the agent (default: "").

        Raises:
            ValueError: If the name is not unique.
        """
        self.name = name
        self.system_instructions = system_instructions
        AgentRegistry.register_agent(name, self)

    @abstractmethod
    def execute(self, query: str) -> str:
        """
        Execute the agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The result or response from the agent.
        """
        pass

    def __del__(self):
        """
        Unregister the agent when it is deleted.
        """
        self.cleanup()

    def cleanup(self):
        AgentRegistry.unregister_agent(self.name)



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
        super().__init__(name, system_instructions)

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

        # Get registered tools

        tool_names = ToolRegistry.get_tool_names()
        tools = [ToolRegistry.get_tool(tool_name) for tool_name in tool_names]

        # Interact with the LLM
        response = self.llm_module.execute(messages=messages, tools=tools)
        messages.append(response)
    
        
        # Handle tool calls if present
        if "tool_calls" in response:
            for tool in response["tool_calls"]:
                tool_result = self._handle_tool_call(tool)
               
                messages.append({"role": "tool", "content": str(tool_result)})
            if depth < self.max_tool_call_depth: # To avoid infinite recursion
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
            return ToolRegistry.invoke_tool_call(tool_call)
        except ValueError as ve:
            return f"Tool invocation failed: {ve}"
        except Exception as e:
            return f"Unexpected error during tool invocation: {e}"
        


