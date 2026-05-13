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

    def get_similar_files(self, file_path: str, limit: int = 5) -> List[Dict]:
        """
        Get similar files based on Jaccard similarity of tags.
        Returns a list of dicts: {path, name, tags, similarity}.
        """
        all_files = self._repo.get_all_files()
        
        target_tags = set()
        for f in all_files:
            if f["path"] == file_path:
                raw_tags = f.get("tags", [])
                target_tags = {t.strip().lower() for t in raw_tags if t.strip()}
                break
                
        if not target_tags:
            return []
            
        similar_files = []
        for f in all_files:
            if f["path"] == file_path:
                continue
                
            raw_tags = f.get("tags", [])
            tags = {t.strip().lower() for t in raw_tags if t.strip()}
            if not tags:
                continue
                
            intersection = len(target_tags.intersection(tags))
            if intersection == 0:
                continue
                
            union = len(target_tags.union(tags))
            score = intersection / union
            
            if score > 0:
                f_copy = dict(f)
                f_copy["similarity"] = score
                similar_files.append(f_copy)
                
        similar_files.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return similar_files[:limit]
