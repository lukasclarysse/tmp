from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str, schema: dict) -> dict:
        """
        Generate a structured response from an LLM.

        Args:
            prompt: Instructions and input text.
            schema: JSON schema describing the expected output.

        Returns:
            A validated Python dictionary.
        """
        pass


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""


class LLMTimeoutError(LLMProviderError):
    """Raised when the LLM takes too long to respond."""


class LLMResponseError(LLMProviderError):
    """Raised when the LLM returns invalid output."""