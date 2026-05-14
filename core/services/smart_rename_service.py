# pyre-ignore-all-errors

import os
import re
import requests
from pathlib import Path


class SmartRenameService:

    def __init__(self, model="llama3.2:1b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _clean_filename(self, text: str) -> str:
        text = text.strip()
        text = text.replace('"', "")
        text = text.replace("'", "")
        text = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ_\-\s]", "", text)
        text = re.sub(r"\s+", "_", text)
        return text[:80]

    def generate_name(self, original_path: str, tags: list[str]) -> str:
        ext = Path(original_path).suffix

        prompt = f"""
You are a file naming assistant.

Create a short, clear filename based on these tags:
{", ".join(tags)}

Rules:
- Return only one filename
- No explanation
- No file extension
- Use English words
- Use underscores instead of spaces
- Maximum 6 words
"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        data = response.json()
        raw_name = data.get("response", "renamed_file")

        clean_name = self._clean_filename(raw_name)

        if not clean_name:
            clean_name = "renamed_file"

        return clean_name + ext

    def rename_file(self, file_path: str, tags: list[str]) -> str:
        old_path = Path(file_path)

        if not old_path.exists():
            raise FileNotFoundError("File not found")

        new_name = self.generate_name(str(old_path), tags)
        new_path = old_path.parent / new_name

        counter = 1
        while new_path.exists():
            new_path = old_path.parent / f"{new_path.stem}_{counter}{old_path.suffix}"
            counter += 1

        os.rename(old_path, new_path)

        return str(new_path)