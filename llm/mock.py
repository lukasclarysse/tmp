from llm.provider import (
    LLMProvider,
    LLMResponseError,
    LLMTimeoutError
)


class MockLLM(LLMProvider):

    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.call_count = 0

    def generate(self, prompt: str, schema: dict) -> dict:

        self.call_count += 1

        if not self.responses:
            raise LLMResponseError(
                "MockLLM has no responses configured."
            )

        response = self.responses.pop(0)

        if response == "TIMEOUT":
            raise LLMTimeoutError(
                "Simulated timeout."
            )

        if response == "INVALID":
            raise LLMResponseError(
                "Simulated invalid response."
            )

        return response