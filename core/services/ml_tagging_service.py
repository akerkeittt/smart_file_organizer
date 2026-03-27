# pyre-ignore-all-errors
from typing import List
from core.ollama_client import OllamaClient


class MLTaggingService:
    """
    Semantic tag generation service.
    Wraps OllamaClient as an internal implementation detail.
    """

    MAX_TEXT_LENGTH = 15_000

    def __init__(self, ollama_client: OllamaClient):
        self._client = ollama_client

    def generate_tags(self, text: str) -> List[str]:
        """
        Generate semantic tags for the given text.
        Truncates input if it exceeds MAX_TEXT_LENGTH.
        Returns an empty list on failure.
        """
        if not text or text.startswith("Error"):
            return []

        # Truncate long texts to avoid overloading the model
        if len(text) > self.MAX_TEXT_LENGTH:
            text = text[: self.MAX_TEXT_LENGTH]

        return self._client.generate_tags(text)
