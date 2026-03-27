import os
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

class FileHandler:
    def __init__(self, db_path: str = "tags_db.json"):
        """
        Initialize the file handler and load existing tags.
        """
        self.db_path = Path(db_path)
        self.file_tags: Dict[str, List[str]] = self._load_tags()

    def _load_tags(self) -> Dict[str, List[str]]:
        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading tags: {e}")
        return {}

    def save_tags(self, file_path: str, tags: List[str]):
        """
        Save tags for a specific file to the JSON database.
        """
        self.file_tags[file_path] = tags
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self.file_tags, f, indent=4)
        except Exception as e:
            print(f"Error saving tags: {e}")

    def get_tags(self, file_path: str) -> List[str]:
        """
        Retrieve existing tags for a file.
        """
        return self.file_tags.get(file_path, [])

    def search_files(self, search_query: str) -> List[str]:
        """
        Search for files matching the given comma-separated tag query.
        """
        query_tags = [q.strip().lower() for q in search_query.split(",") if q.strip()]
        if not query_tags:
            return list(self.file_tags.keys())

        matching_files = []
        for file_path, tags in self.file_tags.items():
            lower_tags = [t.lower() for t in tags]
            # Match if any query tag is a substring of any file tag
            if any(q in t for q in query_tags for t in lower_tags):
                matching_files.append(file_path)
        return matching_files

    def extract_text(self, file_path: str) -> str:
        """
        Extract text content based on the file extension.
        """
        ext = Path(file_path).suffix.lower()
        
        try:
            if ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            elif ext == ".pdf":
                if PyPDF2 is None:
                    return "Error: PyPDF2 not installed. Use 'pip install PyPDF2' to read PDFs."
                text = ""
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                return text
            elif ext in [".png", ".jpg", ".jpeg"]:
                if pytesseract is None or Image is None:
                    return "Error: pytesseract or Pillow not installed. Use 'pip install pytesseract Pillow' to scan images."
                image = Image.open(file_path)
                return pytesseract.image_to_string(image)
            else:
                return f"Unsupported file formatting for text extraction: {ext}"
        except Exception as e:
            return f"Error reading file {file_path}: {e}"
