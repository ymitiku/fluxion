import requests

def send_post_request(url, params):
    """
    Sends a POST request to the LLM server.

    Args:
        url (str): The URL to send the request to.
        params (dict): The data to send in the request.

    Returns:
        dict: The response from the server.
    """
    response = requests.post(url, json=params)
    return response.json()


params = {
    "model": "llama3.2",
    "prompt": "Translate the following English text to French: 'Hello, how are you?'",
    "stream": False,
}

url = "http://localhost:11434/api/generate"
response = send_post_request(url, params)
print(response)