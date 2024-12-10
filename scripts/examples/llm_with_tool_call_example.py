import requests
from fluxion.modules.llm_modules import LLMChatModule
from fluxion.core.llm_agent import LLMChatAgent
from fluxion.core.registry.tool_registry import ToolRegistry



api_key = "" # Enter your API key here
base_url = "http://api.openweathermap.org/data/2.5/weather?"

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
    llm_agent = LLMChatAgent(name="llm_chat_agent", llm_module=llm_module, system_instructions="Provide accurate answers.")
    

    ToolRegistry.register_tool(get_current_whether)
    # Execute

    messages = [
        {
            "role": "user",
            "content": "What is the weather in Paris?"
        }
    ]

    result = llm_agent.execute(messages)
    print(result)
    """
    [
        {'role': 'system', 'content': 'Provide accurate answers.'}, 
        {'role': 'system', 'content': 'Provide accurate answers.'}, 
        {'role': 'user', 'content': 'What is the weather in Paris?'}, 
        {'role': 'assistant', 'content': '', 'tool_calls': [{'function': {'name': 'get_current_whether', 'arguments': {'city_name': 'Paris'}}}]}, 
        {'role': 'tool', 'content': "{'temperature': 6.850000000000023, 'description': 'overcast clouds', 'humidity': 91}"}, 
        {'role': 'assistant', 'content': 'The current weather in Paris is overcast with a temperature of 6.85°C (40.37°F) and high humidity at 91%.'}
    ]

    """