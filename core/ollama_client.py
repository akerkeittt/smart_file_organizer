import requests
import json
from typing import List

class OllamaClient:
    def __init__(self, model: str = "llama3.2:3b", base_url: str = "http://localhost:11434"):
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
        prompt = f"""You are a tagging system.

Generate ONLY 3 to 7 tags.
Each tag must be 1-2 words.
Return ONLY comma-separated tags.
NO explanations.

Content:
{text}"""

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
