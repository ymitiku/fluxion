import json
from fluxon.parser import parse_json_with_recovery
from fluxion.core.agents.llm_agent import LLMChatAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from typing import List, Dict, Any
from fluxion.core.registry.tool_registry import call_agent
from fluxion.models.message_model import Message, MessageHistory, ToolCall

class CoordinationAgent(LLMChatAgent):
    """
    An agent that generates tool calls by calling other agents based on the given task and available agents. 
    It uses an LLM to generate the tool call. 

    CoordinationAgent:
    example-usage::
        from fluxion.core.agents.coordination_agent import CoordinationAgent
        from fluxion.core.modules.llm_modules import LLMChatModule
        from fluxion.core.agents.agent import Agent
        from pydantic import Field, BaseModel
        
        llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)
        
        class DataLoaderAgent(Agent):
            class InputSchema(BaseModel):
                source: str = Field(..., description="The source of the data, e.g., 'sales.csv'.")
        
            class OutputSchema(BaseModel):
                data: str = Field(..., description="The loaded data as a string.")
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
            def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
                return {"data": f"Sales data loaded successfully. {inputs['source']}"}
        
        class DataSummarizerAgent(Agent):
            class InputSchema(BaseModel):
                data: str = Field(..., description="The data to summarize.")
        
            class OutputSchema(BaseModel):
                summary: str = Field(..., description="The summary of the data.")
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
        
            def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
                return {"summary": "{} records summarized.".format(len(data["data"]))}
        
        loader_agent = DataLoaderAgent(name="sales.DataLoader", description="Loads data from a specified source.")
        summarizer_agent = DataSummarizerAgent(name="sales.DataSummarizer")
        
        coordination_agent = CoordinationAgent(name="CoordinationAgent", llm_module=llm_chat_module, agents_groups=["sales"])
        
        messages = [
            {"role": "user", "content": "Summarize sales data and generate a report."},
        ]
        tool_call = coordination_agent.execute(messages)
        print("Generated Tool Call:", json.dumps(tool_call, indent=2))
    """
    

    def __init__(self, *args, agents_groups = [],  **kwargs):
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or (
            "You are an intelligent coordination agent responsible for orchestrating tasks by calling other agents. "
            "You must select an appropriate agent and generate a tool call that adheres to the provided format."
        )
        self.agents_groups = agents_groups

    def execute(self, messages: MessageHistory) -> MessageHistory:
        """
        Generates a tool call using an LLM based on the given task and available agents.

        Args:
            messages (MessageHistory): The messages exchanged.

        Returns:
            MessageHistory: The messages exchanged.
        """

        llm_inputs = self.construct_llm_inputs(messages)

        response = self.llm_module.execute(**llm_inputs)
        return Message.from_llm_format(response)
        

    def coordinate_agents(self, messages: MessageHistory) -> Message:
        """
        Generates a tool call using an LLM based on the given task and available agents.

        Args:
            messages (MessageHistory): The messages exchanged.
            depth (int): The depth of the recursive call (default: 0).

        Returns:
            Message: Result from agent call or error message.
        """
        available_agents = [agent_metadata for group in self.agents_groups for agent_metadata in AgentRegistry.get_agent_metadata(group)]
        # User prompt
        system_prompt = (
            "Available Agents:\n" + json.dumps(available_agents, indent=2) + "\n\n"
            "# Context\n"
            "- Agents are classes with execute method that accepts messages in the following format:\n"
            "```json\n"
            "{\n"
            "    \"role\": \"<should be one of user|system|assistant|tool>\",\n"
            "    \"content\": \"message content\"\n"
            "}\n"
            "```\n"
            "A call to an agent looks like this:\n"
            "```python\n"
            "result = call_agent(agent_name=agent_name, messages=messages)\n"
            "```\n"
            "Instructions:\n"
            "1. Review the task description and the list of available agents.\n"
            "2. Select the best agent to perform the task or subtask.\n"
            "4. Ensure the `agent_name` is one of the available agents.\n"
            "5. If no suitable agent is available, respond with:\n"
            "{\n"
            "    \"error\": \"No suitable agent found or inputs could not be generated.\"\n"
            "}\n\n"
            "Generate the output with the following format:\n"
            "```json\n"
            "{\n"
            "    \"agent_name\": \"agent_name\",\n"
            "}\n"
            "```\n"
            "# Constraints\n"
            "- Strictly adhere to the provided format.\n"
            "- Ensure the agent name is one of the available agents.\n"
            "- Provide a valid response or error message.\n"
            "- Do not include your thought process or additional information.\n"


        )
        # Save original messages
        original_messages = messages.copy()
        # Combine system message and user prompt
        user_prompt_message = Message(role="system", content=system_prompt)
        messages.messages = [user_prompt_message] + messages.messages

        
        response = self.execute(messages=messages)
        response.errors = response.errors or []

        if response.errors and len(response.errors) > 0:
            return response
        try:
            response_content = parse_json_with_recovery(response.content)
            if response_content == {} and (response.content.strip() != "{}" or response.content.strip() != ""):
                raise ValueError("Invalid JSON response.")
            elif response.content.strip() == "{}" or response.content.strip() == "":
                raise ValueError("Empty JSON response.")
       
            if "error" in response_content:
                response.errors.append(response_content["error"])
                response.content = ""
            if not "agent_name" in response_content:
                response.errors.append("No agent name found in the response from the LLM.")
                response.content = ""
          
            if response.errors and len(response.errors) > 0:
                return response
                        
            return call_agent(response_content["agent_name"],  messages=original_messages)

        except ValueError as ve:
            response.errors.append("ValueError occurred while parsing the response from the LLM.")
            response.errors.append(str(ve))
            return response
        except TypeError as te:
            response.errors.append("TypeError occurred while parsing the response from the LLM.")
            response.errors.append(str(te))
            return response
        except Exception as e:
            response.errors.append("Unknown error occurred while parsing the response from the LLM.")
            response.errors.append(str(e))

        
        
        return response
       
        
        
    def get_agent_call_result(self, response: Message) -> Message:
        """
        Get the result of the agent call.

        Args:
            response (Message): The response from the agent call.

        Returns:
            Message: The result of the agent call.
        """
        try:
            response_content = parse_json_with_recovery(response.content)
            if not "agent_name" in response_content:
                if not response.errors:
                    response.errors = []
                response.errors.append("No agent name found in the response from the LLM.")
                return response
            if "arguments" not in response_content:
                if not response.errors:
                    response.errors = []
                response.errors.append("No arguments found in the response from the LLM.")
                return response
            
            if not "messages" in response_content["arguments"]:
                if not response.errors:
                    response.errors = []
                response.errors.append("No messages found in the response from the LLM.")
                return response
            

            return call_agent(response_content["arguments"]["agent_name"], response_content["arguments"]["messages"])
        except ValueError as ve:
            if not response.errors:
                response.errors = []
            response.errors.append("ValueError occurred while parsing the response from the LLM.")
            response.errors.append(str(ve))
            return response
        

# Example Usage
if __name__ == "__main__":
    # Mock LLMChatModule for demonstration purposes
    from fluxion.core.modules.llm_modules import LLMChatModule
    from fluxion.core.agents.agent import Agent
    from pydantic import Field, BaseModel

    llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)

    

    # Define a task and available agents
  

    class DataLoaderAgent(Agent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def execute(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
            return Message(role="assistant", content="Data loaded successfully.")
        
    class DataSummarizerAgent(Agent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        def execute(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
            return Message(role="assistant", content="Data summarized successfully.")
        
    loader_agent = DataLoaderAgent(name="sales.DataLoader", description="Loads data from a specified source.")
    summarizer_agent = DataSummarizerAgent(name="sales.DataSummarizer")

    # Initialize the CoordinationAgent
    coordination_agent = CoordinationAgent(name="CoordinationAgent", llm_module=llm_chat_module, agents_groups=["sales"])

    task_1 = "Load sales data from 'sales.csv'."
    task_2 = "Summarize sales data."

    # Executing tas
    messages =  MessageHistory.from_llm_format({
        "messages": [
            {"role": "user", "content": task_1},
        ]
    })
    result = coordination_agent.coordinate_agents(messages)
   
    print("Task", task_1, "Result:", result.content)
    # Generate a 


    messages =  MessageHistory.from_llm_format({
        "messages": [
            {"role": "user", "content": task_2},
        ]
    })

    result = coordination_agent.coordinate_agents(messages)
    print("Task", task_2, "Result:", result.content)