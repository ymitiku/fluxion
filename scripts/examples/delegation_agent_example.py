from fluxion_ai.models.message_model import Message, MessageHistory
from fluxion_ai.core.agents.delegation_agent import DelegationAgent
from fluxion_ai.core.modules.llm_modules import LLMChatModule
from fluxion_ai.core.agents.agent import Agent

# Mock specialized agents
class GenericAgent(Agent):
    def execute(self, messages: MessageHistory):
        return MessageHistory(messages=[Message(role="tool", content="Task handled by Generic Agent.")])

class DataSummarizerAgent(Agent):

    def execute(self, messages):
        return MessageHistory(messages=[Message(role="tool", content="Data summarized successfully.")])

class DataLoaderAgent(Agent):

    def execute(self, messages):
        return MessageHistory(messages=[Message(role="tool", content="Data loaded successfully.")])

# Initialize the LLM module
llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=120)

# Initialize agents
generic_agent = GenericAgent(name="GenericAgent")
data_summarizer_agent = DataSummarizerAgent(name="DataSummarizer")
data_loader_agent = DataLoaderAgent(name="DataLoader")

# Initialize DelegationAgent
delegation_agent = DelegationAgent(name="DelegationAgent", llm_module=llm_chat_module, generic_agent=generic_agent)

# Add agents to delegation registry
delegation_agent.delegate_task("Summarize the data from the sales report.", "DataSummarizer")
delegation_agent.delegate_task("Load the data from the sales report.", "DataLoader")

# Task 1: Load the dataset
task_description = "There is dataset located at 'data/sales_report.csv' that needs to be analyzed. Load the dataset."
messages = MessageHistory(messages=[Message(role="user", content=task_description)])
result = delegation_agent.decide_and_delegate(messages=messages)
print("Task: ", task_description)
print("Delegation Result:", result[-1].content)

# Task 2: Summarize the data
task_description = "Summarize the data from the sales report."
messages = MessageHistory(messages=[Message(role="user", content=task_description)])
result = delegation_agent.decide_and_delegate(messages=messages)
print("Task: ", task_description)
print("Delegation Result:", result[-1].content)


# Task 3: Generic task
task_description = "Search for information on the internet. Search for Agentic AI."
messages = MessageHistory(messages=[Message(role="user", content=task_description)])
result = delegation_agent.decide_and_delegate(messages=messages)
print("Task: ", task_description)
print("Delegation Result:", result[-1].content)
