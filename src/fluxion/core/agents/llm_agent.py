"""
fluxion.core.llm_agent
~~~~~~~~~~~~~~~~~~~~~~

Defines agents for interacting with Large Language Models (LLMs).

The module includes:
- `LLMQueryAgent` for simple query-based interactions with an LLM.
- `LLMChatAgent` for chat-based interactions that support tool calls.
"""

import json
from typing import Any, Callable, Dict, List, Optional
from fluxion.core.agents.agent import Agent
from fluxion.core.registry.agent_registry import AgentRegistry
from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry


class LLMQueryAgent(Agent):
    """
    An agent that queries an LLM for a response. It uses an LLMQueryModule for execution. 

    LLMQueryAgent:
    example-usage::
        from fluxion.core.agents.llm_agent import LLMQueryAgent
        from fluxion.core.modules.llm_modules import LLMQueryModule

        llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/query", model="llama3.2", timeout=120)
        llm_query_agent = LLMQueryAgent(name="LLMQueryAgent", llm_module=llm_query_module)

        query = "Summarize the key points from the article."
        response = llm_query_agent.execute(query)
        print("LLM Response:", response)

    """

    def __init__(self, *args, llm_module: LLMQueryModule, **kwargs):
        """
        Initialize the LLMQueryAgent.

        Args:
            args: Additional positional arguments for the agent.
            llm_module (LLMQueryModule): The LLMQueryModule instance.
            kwargs: Additional keyword arguments for the agent.
        """
        self.llm_module = llm_module
        super().__init__(*args, **kwargs)

    def execute(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Execute the LLM query agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The response from the LLM.

        Raises:
            ValueError: If the query is empty or invalid.
        """
        if not isinstance(messages, list):
            raise ValueError("Invalid messages: Must be a list of dictionaries.")
        if len(messages) == 0:
            raise ValueError("Invalid messages: Empty list.")

        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise ValueError("Invalid message: Must be a dictionary with 'role' and 'content' keys.")
            if not msg["content"]:
                raise ValueError("Invalid message content: Cannot be empty.")
            if msg["role"] not in ["user", "assistant", "system"]:
                raise ValueError("Invalid message role: Must be 'user', 'assistant', or 'system'.")
        query = "\n".join(["{}: {}".format(msg["role"], msg["content"]) for msg in messages])
    
        prompt = self.system_instructions + "\n\n" + query if self.system_instructions else query
        response =  self.llm_module.execute(prompt=prompt)
        messages.append({
            "role": "assistant",
            "content": response
        })
        return messages

class LLMChatAgent(Agent):
    """
    An agent that interacts with an LLM for chat and supports tool calls.

    LLMChatAgent:
    example-usage::

        from fluxion.core.agents.llm_agent import LLMChatAgent
        from fluxion.core.modules.llm_modules import LLMChatModule
        from fluxion.core.registry.tool_registry import ToolRegistry

        llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)
        llm_chat_agent = LLMChatAgent(name="LLMChatAgent", llm_module=llm_chat_module)

        def tool_summarize(data: Dict[str, Any]) -> Dict[str, Any]:
            return {"summary": f"Summarized data: {data}"}

        llm_chat_agent.register_tool(tool_summarize)

        messages = [
            {"role": "user", "content": "Summarize the data."},
        ]
        response = llm_chat_agent.execute(messages)
        print("LLM Chat Response:", response)

    """

    def __init__(self, *args, llm_module: LLMChatModule, max_tool_call_depth: int = 2, **kwargs):
        """
        Initialize the LLMChatAgent.

        Args:
            args: Additional positional arguments for the agent.
            max_tool_call_depth (int): The maximum depth for tool calls (default: 2).
            kwargs: Additional keyword arguments for the agent.
        """
        self.max_tool_call_depth = max_tool_call_depth
        self.tool_registry = ToolRegistry()
        self.llm_module = llm_module
        super().__init__(*args, **kwargs)
 
    def register_tool(self, func: Callable):
        """
        Register a tool function with the agent's ToolRegistry.

        Args:
            func (Callable): The tool function to register.
        """
        self.tool_registry.register_tool(func)

    def register_tools(self, tools: List[Callable]):
        """
        Register multiple tool functions with the agent's ToolRegistry.

        Args:
            tools (List[Callable]): The list of tool functions to register.
        """
        for tool in tools:
            self.register_tool(tool)


    def construct_llm_inputs(self, messages: List[Dict[str, str]]):
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
        tools = self.get_llm_tools()


        return dict(messages=messages, tools=tools)
    
    def get_llm_tools(self):
        return [{"type": "function", "function": tool} for _, tool in self.tool_registry.list_tools().items()]


    def execute(self, messages: List[Dict[str, str]], depth: int = 0) -> List[Dict[str, str]]:
        """
        Execute the LLM chat agent logic.

        Args:
            messages (List[Dict[str, str]]): The chat history, including the user query.
            depth (int): Current depth of recursion for tool calls (default: 0).

        Returns:
            List[Dict[str, str]]: The updated chat history with the LLM and tool responses.

        Raises:
            ValueError: If the input messages are not valid.
        """

        # Interact with the LLM
        response = self.llm_module.execute(**self.construct_llm_inputs(messages))
        messages.append(response)

        # Handle tool calls if present
        messages = self._execute_tool_calls(response, messages, depth)
        return messages
    
    def _execute_tool_calls(self, response: Dict[str, Any], messages: List[Dict[str, str]], depth: int = 0) -> List[Dict[str, str]]:
        """
        Execute tool calls in the chat history.

        Args:
            messages (List[Dict[str, str]]): The chat history, including the user query.

        Returns:
            List[Dict[str, str]]: The updated chat history with the LLM and tool responses.
        """
        if "tool_calls" in response:
            for tool_call in response["tool_calls"]:
                tool_result = self._handle_tool_call(tool_call)
                messages.append({"role": "tool", "content": json.dumps(tool_result, indent=2)})

            if depth < self.max_tool_call_depth:  # Prevent infinite recursion
                if messages[0]["role"] == "system":
                    messages = messages[1:] # Skip the system message
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



class PersistentLLMChatAgent(LLMChatAgent):
    """
    An agent that interacts with an LLM for chat and supports tool calls, with persistent state.

    PersistentLLMChatAgent:
    example-usage::

        from fluxion.core.agents.llm_agent import PersistentLLMChatAgent
        from fluxion.core.modules.llm_modules import LLMChatModule
        from fluxion.core.registry.tool_registry import ToolRegistry

        llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)
        llm_chat_agent = PersistentLLMChatAgent(name="LLMChatAgent", llm_module=llm_chat_module)

        def tool_summarize(data: Dict[str, Any]) -> Dict[str, Any]:
            return {"summary": f"Summarized data: {data}"}

        llm_chat_agent.register_tool(tool_summarize)

        messages = [
            {"role": "user", "content": "Summarize the data."},
        ]
        response = llm_chat_agent.execute(messages)
        print("LLM Chat Response:", response)

    """

    def __init__(self, *args, max_state_size: Optional[int] = None, **kwargs):
        """
        Initialize the PersistentLLMChatAgent.

        Args:
            args: Additional positional arguments for the agent.
            kwargs: Additional keyword arguments for the agent.
        """
        super().__init__(*args, **kwargs)
        self.state = {"messages": []}
        self.max_state_size = max_state_size

       
    def execute(self, messages: List[Dict[str, str]], depth: int = 0) -> List[Dict[str, str]]:
        """
        Execute the PersistentLLMChatAgent logic with persistent state.

        Args:
            messages (List[Dict[str, str]]): The chat history, including the user query.
            depth (int): Current depth of recursion for tool calls (default: 0).

        Returns:
            List[Dict[str, str]]: The updated chat history with the LLM and tool responses.

        Raises:
            ValueError: If the input messages are not valid.
        """

        # Update the agent's state
        self.update_state(messages)

        # Interact with the LLM
        response = self.llm_module.execute(**self.construct_llm_inputs(self.state["messages"]))
        messages.append(response)

        self.update_state([response])
        
        # Handle tool calls if present
        messages = self._execute_tool_calls(response, messages, depth)

        

        return messages
    
    def update_state(self, messages: List[Dict[str, str]]):
        """
        Update the agent's state.

        Args:
            state (Dict[str, Any]): The new state to set.
        """
        self.state["messages"].extend(messages)
        if self.max_state_size:
            self.state["messages"] = self.state["messages"][-self.max_state_size:]

