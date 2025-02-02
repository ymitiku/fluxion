from fluxion_ai.core.agents.llm_agent import PersistentLLMChatAgent
from fluxion_ai.core.modules.llm_modules import LLMChatModule, DeepSeekR1ChatModule
from fluxion_ai.models.message_model import MessageHistory, Message

class ChatbotAgent(PersistentLLMChatAgent):
    """ A chatbot agent that uses a persistent LLM module to generate responses.  

    This agent is designed to interact with users in a conversational manner. It uses a persistent LLM module to generate responses.

    ChatbotAgent:
    example-usage::
        from fluxion_ai.prebuilt_agents.chatbot import ChatbotAgent

        # Initialize the ChatbotAgent
        chatbot = ChatbotAgent(
            name="PersistentChatbot", 
            system_instructions="You are a friendly chatbot. Answer questions, provide helpful insights, and engage in casual conversation with users.", 
            llm_endpoint="http://localhost:11434/api/chat", 
            llm_model="llama3.2"
        )

        # Start the conversation
        chatbot.start_conversation()

    This agent can be extended to receive messages from different streams such as stdin, sockets, or APIs.

    ChatbotAgent:
    extending-the-agent::
        class MyChatbotAgent(ChatbotAgent):
            def receive_message(self):
                # Implement the method to receive messages from a custom source
                pass

            def send_message(self, message: str):
                # Implement the method to send messages to a custom destination
                pass


        chatbot = MyChatbotAgent(
            name="MyChatbot", 
            system_instructions="You are a friendly chatbot. Answer questions, provide helpful insights, and engage in casual conversation with users.",
            llm_endpoint="http://localhost:11434/api/chat", 
            llm_model="llama3.2"
        )

        chatbot.start_conversation()
    """

    def __init__(
        self, 
        name: str, 
        system_instructions: str, 
        llm_endpoint: str, 
        llm_model: str, 
        max_history_size: int = 50,
        timeout: int = 120
    ):
        if llm_model.startswith("deepseek-r1"): # Deepseek models require a different module
            llm_module = DeepSeekR1ChatModule(endpoint=llm_endpoint, model=llm_model, timeout=timeout)
        else:
            llm_module = LLMChatModule(endpoint=llm_endpoint, model=llm_model, timeout=timeout)

        super().__init__(name=name, llm_module=llm_module, system_instructions=system_instructions, max_state_size=max_history_size)

        # Define color codes for the user and chatbot
        self.user_color = "\033[94m"  # Blue for user input
        self.bot_color = "\033[92m"   # Green for chatbot response
        self.reset_color = "\033[0m"  # Reset to default color

    
    def receive_message(self):
        """Receive a message from the user."""
        return input(f"{self.user_color}You: {self.reset_color}")
    
    def send_message(self, message: str):
        """Send a message to the user."""
        print(f"{self.bot_color}Chatbot: {message}{self.reset_color}")
        print(f"{'~'*50}")  # Add a separator for clarity

    def pre_process_message(self, message: str):
        """Pre-process the messages before executing the agent."""
        return MessageHistory(messages=[Message(role="user", content=message)])
    
    def post_process_response(self, response: MessageHistory):
        """Post-process the response after executing the agent."""
        return response[-1].content
    
    def start_conversation(self):
        """Start a conversation loop with the user."""
        self.send_message("Use '/exit', '/quit', '/bye', or '/goodbye' to end the conversation.")
        while True:
            try:
                user_message = self.receive_message()
                if user_message.lower() in ["/exit", "/quit", "/bye", "/goodbye"]:
                    self.stop_conversation()
                    break
                bot_reply = self.get_bot_response(user_message)
                self.send_message(bot_reply)
            except KeyboardInterrupt:
                self.stop_conversation()
                break
            except Exception as e:
                self.send_message("Oops! Unexpected error occurred. Please try again.")
                print(str(e))
    def get_bot_response(self, message: str):
        """Respond to a message from the user."""
        messages = self.pre_process_message(message)
        response = self.execute(messages=messages)
        return self.post_process_response(response)

    def stop_conversation(self):
        """Stop the conversation."""
        bot_reply = self.get_bot_response("Nice chatting with you! Goodbye!")
        self.send_message(bot_reply)
