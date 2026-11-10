
import time
import requests

URL = "http://localhost:11434/api/chat"

prompt = """
You are a proofreading assistant.

Correct the grammar of this text and return JSON.

Text:
He go to school yesterday.

Return:
{
    "corrected_text": "He went to school yesterday."
}
"""

payload = {
    "model": "qwen2.5:3b",
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ],
    "stream": False,
    "format": {
        "type": "object",
        "properties": {
            "corrected_text": {
                "type": "string"
            }
        },
        "required": ["corrected_text"]
    },
    "options": {
        "temperature": 0.2
    }
}

print("Sending request to Ollama...")

start = time.time()

try:
    response = requests.post(
        URL,
        json=payload,
        timeout=300
    )

    elapsed = time.time() - start

    response.raise_for_status()

    print(f"\nResponse received in {elapsed:.2f} seconds")
    print(response.json()["message"]["content"])

except Exception as e:
    print(f"\nError: {e}")
