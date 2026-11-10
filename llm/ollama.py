import json
import os

import requests
from jsonschema import ValidationError, validate

from llm.provider import (
    LLMProvider,
    LLMTimeoutError,
    LLMResponseError
)


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        model=None,
        base_url=None,
        timeout=300
    ):
        self.model = model or os.getenv(
            "LLM_MODEL",
            "qwen2.5:1.3b"
        )

        self.base_url = (
            base_url
            or os.getenv(
                "LLM_BASE_URL",
                "http://localhost:11434"
            )
        ).rstrip("/")

        self.timeout = timeout

    def generate(self, prompt: str, schema: dict) -> dict:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

        except requests.exceptions.Timeout as exc:
            raise LLMTimeoutError(
                "Ollama request timed out."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise LLMResponseError(
                f"Could not communicate with Ollama: {exc}"
            ) from exc

        try:
            response_data = response.json()
            content = response_data["message"]["content"]
            result = json.loads(content)

        except (ValueError, KeyError, TypeError) as exc:
            raise LLMResponseError(
                "Ollama returned an invalid JSON response."
            ) from exc

        try:
            validate(instance=result, schema=schema)

        except ValidationError as exc:
            raise LLMResponseError(
                f"Ollama response did not match the schema: {exc.message}"
            ) from exc

        return result