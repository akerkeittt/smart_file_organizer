import os
from pathlib import Path
from typing import Optional


class FileSystemAdapter:
    """
    Thin abstraction over the local file system.
    All file I/O in the application goes through this adapter.
    """

    @staticmethod
    def file_exists(file_path: str) -> bool:
        return Path(file_path).exists()

    @staticmethod
    def get_file_name(file_path: str) -> str:
        return Path(file_path).name

    @staticmethod
    def get_extension(file_path: str) -> str:
        return Path(file_path).suffix.lower()

    @staticmethod
    def read_text(file_path: str, encoding: str = "utf-8") -> str:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def read_bytes(file_path: str) -> bytes:
        with open(file_path, "rb") as f:
            return f.read()
