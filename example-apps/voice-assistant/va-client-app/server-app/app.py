from flask import Flask, send_from_directory, jsonify, request
from typing import List
from flask_cors import CORS
import tempfile
import os
import json
from fluxion.core.modules.llm_modules import LLMChatModule
from fluxion.core.agents.llm_agent import LLMChatAgent
import speech_recognition as sr
from fluxion.utils.audio_utils import AudioUtils
from pydub import AudioSegment # Requires pydub and ffmpeg
import random
from googlesearch import search

def perform_google_search(query: str, num_results: int) -> List[str]:
    """ Perform a Google search and return the top `num_results` results

    Args:
        query (str): The search query
        num_results (int): The number of search results to return

    Returns:
        List[str]: A list of search results where each result contains link, title and description
    """
    search_results = []
    for item in search(query, num_results=num_results, lang="en", region="ie", ssl_verify=False, advanced=True, sleep_interval=5):
        search_results.append("Url: {} \nTitle: {} \nDescription: {}".format(item.url, item.title, item.description))
    return search_results

def reformat_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.set_frame_rate(16000)
    audio.export(output_path, format="wav")


llm_module = LLMChatModule(endpoint="http://localhost:11434/api/chat", model="llama3.2", timeout=30)
agent_instructions = """You are a chatbot designed to assist user by answering their questions and queries
"""
llm_agent = LLMChatAgent("Generic Chatbot", llm_module)
llm_agent.tool_registry.register_tool(perform_google_search)
audio_utils = AudioUtils(sr.Recognizer())


app = Flask(__name__, static_folder="../client-app/dist", static_url_path="/")
CORS(app)  # Enables cross-origin resource sharing


@app.route("/")
def serve_react():
    """Serves the React app's index.html."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static_files(path):
    """Serves static files like JavaScript, CSS, etc."""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

def send_to_llm(history, message):
    messages = history + [
        {
            "role": "user",
            "content": message
        }
    ]
    response = llm_agent.execute(messages=messages)
    print(response)
    return response[-1]["content"]

# Example API endpoints
@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.get_json()
    history = [{"role": "user" if item["sender"] == "user" else "assistant", "content": item["content"]} for item in data.get("history", [])]

    message = data.get("message")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    response = send_to_llm(history, message)
    return jsonify({"response": response})

def get_random_filename():
    return  ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))


@app.route("/send-audio", methods=["POST"])
def send_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    history_json = json.loads(request.form.get("history", "[]"))
    history = [{"role": "user" if item["sender"] == "user" else "assistant", "content": item["content"]} for item in history_json]


    original_audio_path = "/tmp/" + get_random_filename() + ".wav"
    audio.save(original_audio_path)
    reformatted_audio_path = "/tmp/" + get_random_filename() + ".wav"

    reformat_wav(original_audio_path, reformatted_audio_path)

    audio_text = audio_utils.transcribe_audio(reformatted_audio_path)

    os.remove(original_audio_path)
    os.remove(reformatted_audio_path)

    response = send_to_llm(history, audio_text)
    return jsonify({
        "response": response,
        "audio_text": audio_text
    })


if __name__ == "__main__":
    app.run(debug=True, port=8000)
