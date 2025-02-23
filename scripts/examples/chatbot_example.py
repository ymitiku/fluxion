from fluxion_ai.prebuilt_agents.chatbot import ChatbotAgent

chatbot = ChatbotAgent(
    name="PersistentChatbot", 
    system_instructions="You are a friendly chatbot. Answer questions, provide helpful insights, and engage in casual conversation with users.", 
    llm_endpoint="http://localhost:11434/api/chat", 
    llm_model="llama3.2",
    timeout = 120
)

# Start the conversation
chatbot.start_conversation()