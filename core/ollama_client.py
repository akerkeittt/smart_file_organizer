import requests
from typing import List, Optional


class OllamaClient:
    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.2,
    ):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

    def _build_prompt(self, text: str) -> str:
        text = text[:2500]

        return f"""
You are a semantic analysis system.

Your task:
Extract 3–5 high-level semantic tags that describe the meaning of the text.

Rules:
- Focus on meaning, not exact words
- Use general concepts (e.g. "finance", "education", "health", "technology")
- No sentences
- No explanations
- Output ONLY comma-separated lowercase words

Examples:
Text: "I paid my invoice and checked my bank balance"
Output: finance, banking, payment

Text: "The student is learning Python programming"
Output: education, programming, python, technology

Now analyze:

{text}

Output:
""".strip()

    def generate_tags(self, text: str) -> List[str]:
        prompt = self._build_prompt(text)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "top_p": 0.9
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "")

            return self._parse_tags(response_text)

        except requests.RequestException as e:
            print(f"[Ollama Error]: {e}")
            return []

    def _parse_tags(self, text: str) -> List[str]:
        if not text:
            return []

        # чистка ответа
        text = text.lower().strip()

        # убираем возможные лишние символы
        for char in ["\n", ".", ";"]:
            text = text.replace(char, ",")

        tags = [
            tag.strip()
            for tag in text.split(",")
            if tag.strip()
        ]

        # убираем дубликаты, сохраняя порядок
        seen = set()
        unique_tags = []

        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags[:5]