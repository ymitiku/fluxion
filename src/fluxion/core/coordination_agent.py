import json
from fluxon.parser import parse_json_with_recovery
from fluxion.core.llm_agent import LLMChatAgent
from fluxion.core.registry.agent_registry import AgentRegistry
from typing import List, Dict, Any
from fluxion.core.registry.tool_registry import call_agent

class CoordinationAgent(LLMChatAgent):
    def __init__(self, *args, agents_groups = [],  **kwargs):
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or (
            "You are an intelligent coordination agent responsible for orchestrating tasks by calling other agents. "
            "You must select an appropriate agent and generate a tool call that adheres to the provided schema."
        )
        self.agents_groups = agents_groups
        self.register_tool(call_agent)

    def execute(self, messages: List[Dict[str, str]], depth: int = 0) -> List[Dict[str, str]]:
        """
        Generates a tool call using an LLM based on the given task and available agents.

        Args:
            task (str): The task description.

        Returns:
            Dict: The LLM-generated tool call or an error message.
        """
        available_agents = [agent_metadata for group in self.agents_groups for agent_metadata in AgentRegistry.get_agent_metadata(group)]
        # User prompt
        user_prompt = (
            "Available Agents:\n" + json.dumps(available_agents, indent=2) + "\n\n"
            "Instructions:\n"
            "1. Review the task description and the list of available agents.\n"
            "2. Select the best agent to perform the task or subtask.\n"
            "3. Generate a tool call in the following format:\n"
            "{\n"
            "    \"function\": {\n"
            "        \"name\": \"call_agent\",\n"
            "        \"arguments\": {\n"
            "            \"agent_name\": \"<name_of_the_agent>\",\n"
            "            \"inputs\": {\n"
            "                \"<input_name>\": \"<input_value>\"\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "4. Ensure the `agent_name` and `inputs` are valid based on the agent's schema.\n"
            "5. If no suitable agent is available, respond with:\n"
            "{\n"
            "    \"error\": \"No suitable agent found or inputs could not be generated.\"\n"
            "}\n\n"
        )
        # Combine system message and user prompt
        messages = [{"role": "user", "content": user_prompt}] + messages

        # Query the LLM
        response = super().execute(messages=messages)

        try:
            # Parse the LLM response
            if "error" in response[-1]:
                return response[-1]
            content =  response[-1]["content"]
            output =  parse_json_with_recovery(content)

            if content and not output:
                return {"error": "Failed to parse the response from the LLM."}
            return output
        except ValueError:
            return {"error": "Failed to parse the response from the LLM."}

# Example Usage
if __name__ == "__main__":
    # Mock LLMChatModule for demonstration purposes
    from fluxion.modules.llm_modules import LLMChatModule
    from fluxion.core.agent import Agent
    from pydantic import Field, BaseModel

    llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)

    

    # Define a task and available agents
    task = "Summarize sales data and generate a report."

    class DataLoaderAgent(Agent):
        class InputSchema(BaseModel):
            source: str = Field(..., description="The source of the data, e.g., 'sales.csv'.")

        class OutputSchema(BaseModel):
            data: str = Field(..., description="The loaded data as a string.")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.input_schema = self.InputSchema
            self.output_schema = self.OutputSchema
           

        def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
            return {"data": f"Sales data loaded successfully. {inputs['source']}"}
        
    class DataSummarizerAgent(Agent):
        class InputSchema(BaseModel):
            data: str = Field(..., description="The data to summarize.")

        class OutputSchema(BaseModel):
            summary: str = Field(..., description="The summary of the data.")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.input_schema = self.InputSchema
            self.output_schema = self.OutputSchema

        def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {"summary": "{} records summarized.".format(len(data["data"]))}
        
    loader_agent = DataLoaderAgent(name="sales.DataLoader", description="Loads data from a specified source.")
    summarizer_agent = DataSummarizerAgent(name="sales.DataSummarizer")

    # Initialize the CoordinationAgent
    coordination_agent = CoordinationAgent(name="CoordinationAgent", llm_module=llm_chat_module, agents_groups=["sales"])


    # Generate a tool call
    messages = [
        {"role": "user", "content": task},
    ]
    tool_call = coordination_agent.execute(messages)
    print("Generated Tool Call:", json.dumps(tool_call, indent=2))
