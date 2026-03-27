# pyre-ignore-all-errors
from typing import Callable, Dict, List, Optional

from core.adapters.file_system_adapter import FileSystemAdapter
from core.repository.metadata_repository import MetadataRepository
from core.services.content_analysis_service import ContentAnalysisService
from core.services.ml_tagging_service import MLTaggingService


class FileProcessingService:
    """
    Main orchestration layer.
    Coordinates file registration, text extraction, tag generation, and persistence.
    """

    def __init__(
        self,
        fs_adapter: FileSystemAdapter,
        repository: MetadataRepository,
        content_analysis: ContentAnalysisService,
        ml_tagging: MLTaggingService,
    ):
        self._fs = fs_adapter
        self._repo = repository
        self._content = content_analysis
        self._tagging = ml_tagging

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_file(self, file_path: str) -> Dict:
        """
        Register a file in the system (without tagging).
        Returns a file dict {path, name, tags}.
        """
        name = self._fs.get_file_name(file_path)
        self._repo.add_file(file_path, name)
        tags = self._repo.get_tags(file_path)
        return {"path": file_path, "name": name, "tags": tags}

    def process_file(
        self,
        file_path: str,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> List[str]:
        """
        Full pipeline: extract text → generate tags → persist.
        Returns the generated tags.
        Optional *on_status* callback receives status strings for UI updates.
        """
        name = self._fs.get_file_name(file_path)

        if on_status:
            on_status(f"Extracting: {name}")

        text = self._content.extract_text(file_path)

        if not text or text.startswith("Error"):
            return []

        if on_status:
            on_status(f"Tagging: {name}")

        tags = self._tagging.generate_tags(text)

        if tags:
            self._repo.save_tags(file_path, tags)

        return tags

    def update_tags(self, file_path: str, tags: List[str]) -> List[str]:
        """Manually update tags for a file."""
        self._repo.save_tags(file_path, tags)
        return tags

    def delete_files(self, paths: List[str]):
        """Delete multiple files from the DB and the physical filesystem."""
        import os
        for p in paths:
            self._repo.delete_file(p)
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def get_all_files(self) -> List[Dict]:
        """Return every registered file with its tags."""
        return self._repo.get_all_files()

    def get_tags(self, file_path: str) -> List[str]:
        """Get tags for a specific file."""
        return self._repo.get_tags(file_path)
