import os
import requests
from dotenv import load_dotenv
load_dotenv()
import json

HF_API_TOKEN = os.getenv('HF_API_TOKEN')  # Optional, for higher rate limits
LLAMA3_API_URL = os.getenv('LLAMA3_API_URL', 'http://localhost:11434/api/chat')

# Hugging Face Inference API endpoints
INTENT_MODEL = 'Falconsai/intent_classification'
SENTIMENT_MODEL = 'tabularisai/multilingual-sentiment-analysis'
LLAMA3_MODEL = 'meta-llama/Llama-3.1-8B-Instruct'  # Updated to latest/popular variant


def hf_intent_classification(text):
    url = f'https://api-inference.huggingface.co/models/{INTENT_MODEL}'
    headers = {'Authorization': f'Bearer {HF_API_TOKEN}'} if HF_API_TOKEN else {}
    response = requests.post(url, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()
    return {"error": response.text}

def hf_sentiment_analysis(text):
    url = f'https://api-inference.huggingface.co/models/{SENTIMENT_MODEL}'
    headers = {'Authorization': f'Bearer {HF_API_TOKEN}'} if HF_API_TOKEN else {}
    response = requests.post(url, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()
    return {"error": response.text}

# Llama 3 chat completion via local Ollama API
# history: list of {"role": "user"|"assistant", "content": ...}
def local_llama3_chat_completion(messages, system_prompt=None):
    url = LLAMA3_API_URL
    # Ollama expects a 'messages' list with role/content, and optionally a system prompt
    payload = {
        "model": "llama3",
        "messages": messages
    }
    if system_prompt:
        payload["system"] = system_prompt
    try:
        response = requests.post(url, json=payload, timeout=60, stream=True)
        content = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if 'message' in chunk and 'content' in chunk['message']:
                        content += chunk['message']['content']
                except Exception as e:
                    print("[Llama3 Ollama] Chunk parse error:", e)
        return content.strip() if content else "Sorry, I could not process your request right now."
    except Exception as e:
        print(f"[Llama3 Ollama] Exception: {e}")
        return "Sorry, I could not process your request right now."

def llama3_chat_completion(user_message, system_prompt=None, max_tokens=256):
    messages = [{"role": "user", "content": user_message}]
    return local_llama3_chat_completion(messages, system_prompt=system_prompt) 