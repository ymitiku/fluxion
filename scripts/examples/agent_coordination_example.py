from fluxion.core.agents.llm_agent import LLMChatAgent, LLMQueryAgent
from fluxion.models.message_model import Message, MessageHistory
from fluxion.core.modules.llm_modules import LLMChatModule, LLMQueryModule
from ast import literal_eval

def evaluate_math_expression(expression: str) -> str:
    """ Evaluate a mathematical expression.

    :param expression: The mathematical expression to evaluate.
    :return: The result of the expression.
    """
    print("Current expression: ", expression)

    output =  str(eval(expression))
    return output

# MathAgent: Solves math problems

class MathAgent(LLMChatAgent):
    def __init__(self, name, llm_module):
        super().__init__(
            name=name,
            llm_module=llm_module,
            system_instructions=(
                "You are a math-solving agent. Solve mathematical problems accurately. "
                "If the input is not a valid math problem, respond with an error message.\n"
                "Do not generate additional information or context. \n"
                "Your task is to get the mathematical expression and evaluate it.\n"
                "You can use the evaluate_math_expression tool to evaluate the expression."
            ),
            max_tool_call_depth=1
        )
        self.register_tool(evaluate_math_expression)

    

# TranslationAgent: Handles language translations
class TranslationAgent(LLMQueryAgent):
    def __init__(self, name, llm_module):
        super().__init__(
            name=name,
            llm_module=llm_module,
            system_instructions=(
                "You are a translation agent. Translate the given text accurately into the specified language. "
                "If no target language is specified, default to translating into French."
                "Do not generate additional information or context."
                "Translate the given text into the specified language."
            )
        )
        

# ChatAgent: Engages in casual conversation
class ChatAgent(LLMQueryAgent):
    def __init__(self, name, llm_module):
        super().__init__(
            name=name,
            llm_module=llm_module,
            system_instructions=(
                "You are a friendly chat agent. Engage in casual conversation, answer general questions, "
                "and make the interaction enjoyable. Generate jokes or play simple games if asked."
            )
        )

# SummarizationAgent: Summarizes long documents
class SummarizationAgent(LLMQueryAgent):
    def __init__(self, name, llm_module):
        super().__init__(
            name=name,
            llm_module=llm_module,
            system_instructions=(
                "You are a summarization agent. Summarize the given text or document concisely. "
                "Ensure that the summary captures the essence of the content."
            )
        )



from fluxion.core.agents.coordination_agent import CoordinationAgent

# Initialize the LLM module
llm_chat_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2")
llm_query_module = LLMQueryModule(endpoint="http://localhost:11434/api/generate", model="llama3.2")

# Create instances of specialized agents
math_agent = MathAgent(name="group1.MathAgent", llm_module=llm_chat_module)
translation_agent = TranslationAgent(name="group1.TranslationAgent", llm_module=llm_query_module)
chat_agent = ChatAgent(name="group1.ChatAgent", llm_module=llm_query_module)
summarization_agent = SummarizationAgent(name="group1.SummarizationAgent", llm_module=llm_query_module)

# Initialize the CoordinationAgent
coordination_agent = CoordinationAgent(
    name="CoordinationAgent",
    llm_module=llm_chat_module,
    agents_groups=["group1"]
)


# Define example tasks
tasks = [
    "What is 5 + 7 * 2?",
    "Translate 'Hello, how are you?' into French.",
    "Tell me a joke.",
    "Summarize the following Document. \n"
    """
    Document:
    Fluxion is a Python library for building and managing flow-based agentic workflows. Designed with modularity, 
    scalability, and extensibility in mind, Fluxion simplifies the integration of locally or remotely hosted 
    language models (LLMs) powered by Ollama. By leveraging its robust architecture, developers can create intelligent 
    systems capable of natural conversation, contextual reasoning, tool invocation, and autonomous decision-making, 
    enabling seamless orchestration of complex, dynamic workflows.
    """
]

# Process tasks through CoordinationAgent
for task in tasks:
    messages = MessageHistory(messages=[Message(role="user", content=task)])
    response = coordination_agent.coordinate_agents(messages=messages)
    print(f"Task: {task}")
    print(f"Response: {response[-1].content}\n")
    print("~" * 50)
