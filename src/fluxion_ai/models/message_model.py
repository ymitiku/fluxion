from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
import json

class ToolCall(BaseModel):
    name: str = Field(..., description="The name of the tool called.", title="Name")
    arguments: Dict[str, Any] = Field(..., description="The arguments passed to the tool.", title="Arguments")

    @classmethod
    def from_llm_format(cls, tool_call: Dict[str, Any]) -> "ToolCall":
        """ Parse a tool call from a dictionary.

        Args:
            tool_call (Dict[str, Any]): The tool call dictionary.

        Returns:
            ToolCall: The ToolCall object.
        """
        assert "function" in tool_call, "Tool call must contain a 'function' key."
        assert len(tool_call) == 1, "Tool call must contain only one key - 'function'."
        name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]
        return ToolCall(name=name, arguments=arguments)
    
    def to_llm_format(self) -> Dict[str, Any]:
        """ Convert the ToolCall object to a dictionary.

        Returns:
            Dict[str, Any]: The tool call dictionary.
        """
        return {"function": {"name": self.name, "arguments": self.arguments}}
    
    @classmethod
    def parse_raw(cls, raw: str) -> "ToolCall":
        """ Parse a ToolCall from a raw string.

        Args:
            raw (str): The raw string.

        Returns:
            ToolCall: The ToolCall object.
        """
        return ToolCall.parse_llm_tool_call(json.loads(raw))
    
    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> "ToolCall":
        """ Parse a ToolCall from a dictionary.

        Args:
            obj (Dict[str, Any]): The dictionary.

        Returns:
            ToolCall: The ToolCall object.
        """
        return ToolCall(name=obj["name"], arguments=obj["arguments"])

class Message(BaseModel):
    role: str = Field(..., description="The role of the message sender.", titile="Role")
    content: str = Field(..., description="The content of the message.", title="Content")
    tool_calls: Optional[List[ToolCall]]  = Field(None, description="The list of tool calls made in the message.", title="Tool Calls")
    errors: Optional[List[str]] = Field(None, description="List of error messages if any.", title="Errors")

    def to_llm_format(self) -> List[Dict[str, Any]]:
        """ Get the LLM tool calls from the message.

        Returns:
            List[Dict[str, Any]]: The LLM tool calls.
        """
        return [tool_call.to_llm_format() for tool_call in self.tool_calls] if self.tool_calls else None
    
    @classmethod
    def from_llm_format(cls, message: Dict[str, Any]) -> "Message":
        """ Parse a message from a dictionary.

        Args:
            message (Dict[str, Any]): The message dictionary.

        Returns:
            Message: The Message object.
        """
        role = message["role"]
        content = message["content"]
        error = message["error"] if "error" in message else None
        tool_calls = [ToolCall.from_llm_format(tool_call) for tool_call in message["tool_calls"]] if "tool_calls" in message else None
        return Message(role=role, content=content, tool_calls=tool_calls, error=error)
    
    @classmethod
    def parse_raw(cls, raw: str) -> "Message":
        """ Parse a Message from a raw string.

        Args:
            raw (str): The raw string.

        Returns:
            Message: The Message object.
        """
        parsed_json = json.loads(raw)
        tool_calls = parsed_json.get("tool_calls", None)
        tool_calls = [ToolCall.from_dict(tool_call["function"]) for tool_call in tool_calls] if tool_calls else None
        return Message(role=parsed_json["role"], content=parsed_json["content"], tool_calls=tool_calls)
    
    @classmethod
    def from_dict(cls, obj: Dict[str, Any]) -> "Message":
        """ Parse a Message from a dictionary.

        Args:
            obj (Dict[str, Any]): The dictionary.

        Returns:
            Message: The Message object.
        """
        tool_calls = [ToolCall.from_dict(tool_call["function"]) for tool_call in obj["tool_calls"]] if "tool_calls" in obj and obj["tool_calls"] else None
        return Message(role=obj["role"], content=obj["content"], tool_calls=tool_calls)
    


class MessageHistory(BaseModel):
    messages: List[Message] = Field(..., description="The list of messages exchanged.", title="Messages")

    def to_llm_format(self) -> Dict[str, Any]:
        """ Convert the MessageHistory to LLM format.

        Returns:
            Dict[str, Any]: The LLM format.
        """
        return {"messages": [{"role": message.role, "content": message.content, "tool_calls": message.to_llm_format()} for message in self.messages]}
    
    @classmethod
    def from_llm_format(cls, obj: Dict[str, Any]) -> "MessageHistory":
        """ Parse a MessageHistory from a dictionary.

        Args:
            obj (Dict[str, Any]): The dictionary.

        Returns:
            MessageHistory: The MessageHistory object.
        """
        messages = [Message.from_llm_format(message) for message in obj["messages"]]
        return MessageHistory(messages=messages)
    
    @classmethod
    def parse_raw(cls, raw: str) -> "MessageHistory":
        """ Parse a MessageHistory from a raw string.

        Args:
            raw (str): The raw string.

        Returns:
            MessageHistory: The MessageHistory object.
        """
        parsed_json = json.loads(raw)
        messages = [Message.from_dict(message) for message in parsed_json["messages"]]
        return MessageHistory(messages=messages)

    def __len__(self):
        return len(self.messages)
    
    def __getitem__(self, index):
        return self.messages[index]
    
    def __iter__(self):
        return iter(self.messages)
    
    def append(self, message: Message):
        assert isinstance(message, Message), "Message must be an instance of Message."
        self.messages.append(message)


    def extend(self, messages: "MessageHistory"):
        assert isinstance(messages, MessageHistory), "messages must be an instance of MessageHistory."
        self.messages.extend(messages)