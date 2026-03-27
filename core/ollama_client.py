# pyre-ignore-all-errors
import requests
import json
from typing import List

class OllamaClient:
    def __init__(self, model: str = "llama3.2:1b", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        :param model: The name of the model to use (e.g., 'llama3').
        :param base_url: The base URL of the Ollama API.
        """
        self.model = model
        self.base_url = base_url

    def generate_tags(self, text: str) -> List[str]:
        """
        Send text to the Ollama model and retrieve tags.
        """
        # Truncate text to avoid model overwhelm (first 2500 chars)
        truncated_text = text[:2500]  # type: ignore
        
        prompt = f"""Extract 3 to 5 relevant keywords from the text below.
Output STRICTLY a single line of comma-separated words.
DO NOT write sentences. DO NOT write summaries.

Examples of valid output:
finance, invoice, payment
legal, contract, agreement

Text:
{truncated_text}
"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "")
            
            # Clean up the output to ensure it's a list of tags
            tags = [tag.strip() for tag in response_text.split(",") if tag.strip()]
            return tags
        except requests.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return []
