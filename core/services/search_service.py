from typing import Dict, List
from core.repository.metadata_repository import MetadataRepository


class SearchService:
    """
    Search service backed by SQLite FTS5.
    """

    def __init__(self, repository: MetadataRepository):
        self._repo = repository

    def search(self, query: str) -> List[Dict]:
        """
        Search files by query string (matches against path, name, and tags).
        Returns a list of dicts: {path, name, tags}.
        An empty query returns all files.
        """
        if not query or not query.strip():
            return self._repo.get_all_files()
        return self._repo.search_fts(query)
