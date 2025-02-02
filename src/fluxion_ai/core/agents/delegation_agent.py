from fluxon.parser import parse_json_with_recovery
from fluxion_ai.core.agents.agent import Agent
from fluxion_ai.core.agents.llm_agent import LLMChatAgent
from fluxion_ai.core.registry.agent_registry import AgentRegistry
from fluxion_ai.core.registry.agent_delegation_registry import AgentDelegationRegistry
from fluxion_ai.models.message_model import MessageHistory, Message
from typing import Dict, Any, List
import json

class DelegationAgent(LLMChatAgent):
    """
    An agent that delegates tasks to other agents or handles tasks directly when delegation is not possible. It uses an LLMChatModule for execution
    and a generic agent for handling tasks when delegation fails. Once it decides which agent to delegate the task it directly passes the messages to the agent.

    DelegationAgent:
    Example usage::
        from fluxion_a.core.agents.delegation_agent import DelegationAgent
        from fluxion_a.core.agents.llm_agent import LLMChatAgent
        from fluxion_a.core.registry.agent_registry import AgentRegistry
        from fluxion_a.core.modules.llm_modules import LLMChatModule
        from fluxion_a.core.agents.llm_agent import LLMQueryAgent
        from pydantic import Field, BaseModel

        class DataSummarizerAgent(LLMChatAgent):
            
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.system_instructions = self.system_instructions or (
                    "You are a data summarizer agent responsible for summarizing data from various sources."
                )
                
            
            def execute(self, data_source: str) -> Dict[str, Any]:
                return {"result": f"Data from '{data_source}' summarized successfully.", "status": "completed"}
            
        class DataLoaderAgent(LLMChatAgent):
            

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.system_instructions = self.system_instructions or (
                    "You are a data loader agent responsible for loading data from various sources."
                )
            
            def execute(self, data_source: str) -> Dict[str, Any]:
                return {"status": "completed", "result": f"Data from '{data_source}' loaded successfully."}

        class GenericAgent(LLMQueryAgent):
            def execute(self, task_description: str) -> Dict[str, Any]:
                return {"status": "completed", "result": f"Task '{task_description}' handled by generic agent."}

        llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)
        
        generic_agent = GenericAgent(name="GenericAgent", llm_module=None)
        data_summarizer_agent = DataSummarizerAgent(name="DataSummarizer", llm_module=llm_chat_module)
        data_loader_agent = DataLoaderAgent(name="DataLoader", llm_module=llm_chat_module)

        # Initialize DelegationAgent
        delegation_agent = DelegationAgent(name="DelegationAgent", llm_module=llm_chat_module, generic_agent=generic_agent)

        # Add agents to delegation list
        delegation_agent.delegate_task("Summarize the data from the sales report.", "DataSummarizer")
        delegation_agent.delegate_task("Load the data from the sales report.", "DataLoader")

        task_description = "There is dataset located at 'data/sales_report.csv' that needs to be analyzed. Load the dataset."

        # Decide and delegate
        result = delegation_agent.decide_and_delegate(task_description)
        print("Delegation Result:", json.dumps(result, indent=2))


        task_description = "Summarize the data from the sales report."
        result = delegation_agent.decide_and_delegate(task_description)
        print("Delegation Result:", json.dumps(result, indent=2))
    """
    def __init__(self, *args, generic_agent: Agent= None, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_instructions = self.system_instructions or (
            "You are a delegation agent responsible for assigning tasks to other agents or handling tasks directly when delegation is not possible."
        )
        assert generic_agent is not None, "A generic agent must be provided."
        self.generic_agent = generic_agent
        self.delegation_registry = AgentDelegationRegistry()

    def delegate_task(self, task_description: str, agent_name: str):
        """
        Delegates a task to a specified agent by adding it to the delegation registry.

        Args:
            task_description (str): High-level description of the task.
            agent_name (str): Name of the agent to delegate the task to.

        Raises:
            ValueError: If the agent is not registered.
        """
        """
        Delegates a task to a specified agent by adding it to the delegation list.

        Args:
            task_description (str): High-level description of the task.
            agent_name (str): Name of the agent to delegate the task to.

        Raises:
            ValueError: If the agent is not registered.
        """

        self.delegation_registry.add_delegation(agent_name, task_description)
          
    def decide_and_delegate(self, messages: MessageHistory) -> MessageHistory:
        """
        Uses LLM to decide which agent to delegate the task to. If no valid response is generated,
        the generic agent handles the task.

        Args:
            messages (Dict[str, Any]): Inputs for the LLM.

        Returns:
            Dict[str, Any]: The result of the delegated task or the task handled by the generic agent.
        """
        task_delegations = [
            {
                "task_description": metadata["task_description"],
                "agent_name": agent_name,
                "agent_description": metadata["agent_metadata"]["description"],
            }
            for agent_name, metadata in self.delegation_registry.list_delegations()
        ]

        # Construct the user prompt
        user_prompt = (
            "Agent task delegations:\n" + json.dumps(task_delegations, indent=2) + "\n\n"
            "Generic agent metadata:\n" + json.dumps(self.generic_agent.metadata(), indent=2) + "\n\n"
            "Instructions:\n"
            "1. Review the task description and the list of available agents.\n"
            "2. Select the best agent to perform the task.\n"
            "3. If no agent is suitable, indicate that the task should be handled directly.\n"
            "Respond with the following structure:\n"
            "{\n"
            "    \"agent_name\": \"<name_of_the_agent>\"\n"
            "}\n"
            "If no agent is suitable:\n"
            "{\n"
            "    \"agent_name\": \"generic_agent\"\n"
            "}"
            "- Strictly adhere to the structure for successful delegation.\n"
            "- Do not include any additional information in your response.\n"
            "- Do not assign the task to an agent if the task is not delegated to the agent.\n"
            "- If the task is not delegated to an agent, the generic agent will handle the task."

        )
        initial_messages = messages
        # Query the LLM for delegation

        messages = MessageHistory(messages = [
            Message(role="system", content=user_prompt)
        ] + initial_messages.messages)

        response = self.execute(messages=messages)


        try:
            # Parse the response
            decision = parse_json_with_recovery(response[-1].content)
            if not decision or "agent_name" not in decision:
                return self.generic_agent.execute(messages=initial_messages)
            
            agent_name = decision["agent_name"]
            agent_metadata = self.delegation_registry.get_delegation(agent_name)
            if not agent_metadata:
                raise ValueError(f"Agent '{agent_name}' is not available in the delegation list.")

            return self.execute_agent(agent_name, initial_messages)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback to generic agent if decision fails
            return self.generic_agent.execute(messages=initial_messages)

    def execute_agent(self, agent_name: str, messages: MessageHistory) -> MessageHistory:
        """
        Executes a task by invoking the specified agent.

        Args:
            agent_name (str): The name of the agent to execute.
            inputs (Dict[str, Any]): Inputs for the agent.

        Returns:
            Dict[str, Any]: The result of the agent's execution.
        """
        agent = AgentRegistry.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' is not registered.")

        return agent.execute(messages = messages)

# Example Usage
if __name__ == "__main__":
    from fluxion_ai.core.modules.llm_modules import LLMChatModule
    from fluxion_ai.core.agents.llm_agent import LLMChatAgent, LLMQueryAgent
    from pydantic import Field, BaseModel

    class DataSummarizerAgent(LLMChatAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.system_instructions = self.system_instructions or (
                "You are a data summarizer agent responsible for summarizing data from various sources."
            )
            
        def execute(self, messages: MessageHistory) -> MessageHistory:
            # return {"result": f"Sales data summarized successfully.", "status": "completed"}
            new_message = Message(role="assistant", content="Sales data summarized successfully.")
            return MessageHistory(messages = [new_message])
        
    class DataLoaderAgent(LLMChatAgent):
        
       
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.system_instructions = self.system_instructions or (
                "You are a data loader agent responsible for loading data from various sources."
            )
        
        def execute(self, messages: MessageHistory) -> MessageHistory:
            return MessageHistory(messages = [Message(role="assistant", content="Sales data loaded successfully.")])


    # Mock generic agent
    class GenericAgent(LLMQueryAgent):
        def execute(self, messages: MessageHistory) -> MessageHistory:
            return MessageHistory(messages = [Message(role="assistant", content="Task handled by generic agent.")])


    # Mock LLMChatModule for demonstration purposes
    llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)

    
    generic_agent = GenericAgent(name="GenericAgent", llm_module=None)
    data_summarizer_agent = DataSummarizerAgent(name="DataSummarizer", llm_module=llm_chat_module)
    data_loader_agent = DataLoaderAgent(name="DataLoader", llm_module=llm_chat_module)

    # Initialize DelegationAgent
    delegation_agent = DelegationAgent(name="DelegationAgent", llm_module=llm_chat_module, generic_agent=generic_agent)


    # Add agents to delegation list
    delegation_agent.delegate_task("Summarize the data from the sales report.", "DataSummarizer")
    delegation_agent.delegate_task("Load the data from the sales report.", "DataLoader")

    task_description = "There is dataset located at 'data/sales_report.csv' that needs to be analyzed. Load the dataset."

    
    messages = MessageHistory(messages = [Message(role="user", content=task_description)])
    # Decide and delegate
    result = delegation_agent.decide_and_delegate(messages = messages)
    print("Delegation Result:", json.dumps(json.loads(result.model_dump_json()), indent=2))

    task_description = "Summarize the data from the sales report."
    messages = MessageHistory(messages = [Message(role="user", content=task_description)])
    result = delegation_agent.decide_and_delegate(messages=messages)
    print("Delegation Result:", json.dumps(json.loads(result.model_dump_json()), indent=2))
