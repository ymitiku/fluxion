from fluxion_ai.modules.community_modules import TogetherAIChatModule
from typing import Any, Dict, List

api_key = "" # Add your API key here


chat_module = TogetherAIChatModule(endpoint="https://api.together.xyz/v1/chat/completions", model="deepseek-ai/DeepSeek-R1", headers={"Authorization": f"Bearer {api_key}"}, response_key="choices")



messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
]


response = chat_module.execute(messages=messages)

print("Response:", response)