import requests
from fluxion_ai.core.modules.llm_modules import LLMChatModule
from fluxion_ai.core.agents.llm_agent import LLMChatAgent
from fluxion_ai.core.registry.tool_registry import tool
from fluxion_ai.models.message_model import Message, MessageHistory



api_key = "5d6ec24598b18640b52f5351029d9dde" # Enter your API key here
base_url = "http://api.openweathermap.org/data/2.5/weather?"


@tool
def get_current_whether(city_name: str) -> str:
    """ Get the current weather in a city.

    :param city_name: The city to get the weather for.
    :return: Dictionary containing the temperature, description, and humidity.
    """

    city_name = city_name.replace(" ", "+")
    

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    
    response = requests.get(complete_url)
    data = response.json()

    
    return {
        "temperature": int(data["main"]["temp"]) - 273.15,
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }





if __name__ == "__main__":
    

    # Initialize the LLMChatModule
    llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=60)

    # Initialize the LLMChatAgent
    llm_agent = LLMChatAgent(name="llm_chat_agent", llm_module=llm_module, system_instructions="Provide accurate answers. Note that the tool names have a <module.function> format.")
    

    llm_agent.register_tool(get_current_whether)
    # Execute

    messages = MessageHistory(messages=[
        Message(role="user", content="What is the weather in Paris?")
    ])
    result = llm_agent.execute(messages)
    print("Query: ", messages[0].content)
    print("Response:", result[-1].content)