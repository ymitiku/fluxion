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
from fluxion.core.modules.llm_modules import LLMQueryModule, LLMChatModule
from fluxion.core.registry.tool_registry import ToolRegistry
from fluxion.models.message_model import Message, MessageHistory, ToolCall


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

    def execute(self, messages: MessageHistory) -> MessageHistory:
        """
        Execute the LLM query agent logic.

        Args:
            query (str): The query or prompt for the agent.

        Returns:
            str: The response from the LLM.

        Raises:
            ValueError: If the query is empty or invalid.
        """
        if not isinstance(messages, MessageHistory):
            raise ValueError("Invalid messages: Must be an instance of MessageHistory.")
        if len(messages) == 0:
            raise ValueError("Invalid messages: Empty message history.")

        for msg in messages.messages:
            if not isinstance(msg, Message):
                raise ValueError("Invalid message: Must be instance of {}!".format(msg))
            if not msg.content:
                raise ValueError("Invalid message content: Cannot be empty.")
            if msg.role not in ["user", "assistant", "system", "tool"]:
                raise ValueError("Invalid message role: Must be 'user', 'assistant', 'system', or 'tool'.")
        query = "\n".join(["{}: {}".format(msg.role, msg.content) for msg in messages])
    
        prompt = self.system_instructions + "\n\n" + query if self.system_instructions else query
        response =  self.llm_module.execute(prompt=prompt)
        messages.append(Message(role="assistant", content=response, tool_calls=None))
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

    def __init__(self, *args, llm_module: LLMChatModule, max_tool_call_depth: int = 10, **kwargs):
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


    def construct_llm_inputs(self, messages: MessageHistory) -> Dict[str, Any]:
        if not messages:
            raise ValueError("Invalid messages: Cannot be empty.")
        if not isinstance(messages, MessageHistory):
            raise ValueError("Invalid messages: Must be an instance of MessageHistory.")
        if not messages.messages:
            raise ValueError("Invalid messages: Empty list.")

        # Add system instructions as the first message, if provided
        if self.system_instructions:
            output_messages = [{"role": "system", "content": self.system_instructions}]
        else:
            output_messages = []
    
        output_messages.extend(
            [
                {
                    "role": msg.role, "content": msg.content, 
                    "tool_calls": [tool_call.to_llm_format() for tool_call in msg.tool_calls] if msg.tool_calls else None
                } 
                for msg in messages
            ]
        )
        

        # Get tools from the agent's ToolRegistry
        tools = self.get_llm_tools()


        return dict(messages=output_messages, tools=tools)
    
    def get_llm_tools(self):
        return [{"type": "function", "function": tool} for _, tool in self.tool_registry.list_tools().items()]


    def execute(self, messages: MessageHistory, depth: int = 0) -> MessageHistory:
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
        llm_inputs = self.construct_llm_inputs(messages)

        response = self.llm_module.execute(**llm_inputs)
        response_message = Message.from_llm_format(response)
        
        messages.append(response_message)
        
        # Handle tool calls if present
        messages = self._execute_tool_calls(response_message, messages, depth)

        return messages
    
    def _execute_tool_calls(self, response: Message, messages: MessageHistory, depth: int = 0) -> List[Dict[str, str]]:
        """
        Execute tool calls in the chat history.

        Args:
            messages (List[Dict[str, str]]): The chat history, including the user query.

        Returns:
            List[Dict[str, str]]: The updated chat history with the LLM and tool responses.
        """
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_result = self._handle_tool_call(tool_call)
                if tool_result["errors"]:
                    messages.append(Message(role="tool", content=json.dumps(tool_result["errors"], indent=2)))
                else:
                    messages.append(Message(role="tool", content=json.dumps(tool_result["result"], indent=2)))
            if depth < self.max_tool_call_depth:  # Prevent infinite recursion
                if messages[0].content == self.system_instructions:
                    messages.messages = messages.messages[1:]
                return self.execute(messages, depth=depth + 1)
        return messages

    def _handle_tool_call(self, tool_call: ToolCall) -> Any:
        """
        Handle a tool call response from the LLM.

        Args:
            tool_call (Dict[str, Dict]): The tool call details from the LLM response.

        Returns:
            str: The result of the tool invocation.
        """
        try:
            return {
                "result":  self.tool_registry.invoke_tool_call(tool_call),
                "errors": None
            }
        except ValueError as ve:
            return {
                "result": None,
                "errors": ["ValueError occurred during tool {} invocation!".format(tool_call.name), str(ve)]
            }
        except TypeError as te:
            return {
                "result": None,
                "errors": ["TypeError occurred during tool {} invocation!".format(tool_call.name), str(te)]
            }
        except Exception as e:
            return {
                "result": None,
                "errors": ["An error occurred during tool {} invocation!".format(tool_call.name), str(e)]
            }


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
        self.state = MessageHistory(messages=[])
        self.max_state_size = max_state_size

       
    def execute(self, messages: MessageHistory, depth: int = 0) -> MessageHistory:
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
        response = self.llm_module.execute(**self.construct_llm_inputs(self.state))
        response_message = Message.from_llm_format(response)
        messages.append(response_message)

        self.update_state(MessageHistory(messages=[response_message]))

        
        
        # Handle tool calls if present
        messages = self._execute_tool_calls(response_message, messages, depth)

        return messages
    
    def update_state(self, messages: MessageHistory):
        """
        Update the agent's state.

        Args:
            messages (MessageHistory): The messages to add to the state.
        """
        self.state.extend(messages)
        if self.max_state_size:
            self.state.messages = self.state.messages[-self.max_state_size:]


