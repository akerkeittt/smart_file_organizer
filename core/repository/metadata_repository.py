import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class MetadataRepository:
    """
    The only database access layer.
    Uses SQLite for structured storage and FTS5 for full-text search.
    """

    def __init__(self, db_path: str = "smart_organizer.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._initialize_db()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA foreign_keys=ON;")
        return self._conn

    def _initialize_db(self):
        conn = self._get_connection()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path   TEXT    NOT NULL UNIQUE,
                file_name   TEXT    NOT NULL,
                added_at    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS file_tags (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id  INTEGER NOT NULL,
                tag      TEXT    NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_file_tags_file_id ON file_tags(file_id);
        """)

        # FTS5 virtual table — created separately because CREATE VIRTUAL TABLE
        # does not support IF NOT EXISTS in all SQLite builds, so we guard it.
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS files_fts
                USING fts5(file_path, file_name, tags);
            """)
        except sqlite3.OperationalError:
            pass  # table already exists

        conn.commit()

    # ------------------------------------------------------------------
    # File CRUD
    # ------------------------------------------------------------------

    def add_file(self, file_path: str, file_name: str) -> int:
        """Insert a file record. Returns the file id. Skips if already present."""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT id FROM files WHERE file_path = ?", (file_path,)
        )
        row = cursor.fetchone()
        if row:
            return row["id"]

        cursor = conn.execute(
            "INSERT INTO files (file_path, file_name, added_at) VALUES (?, ?, ?)",
            (file_path, file_name, datetime.now().isoformat()),
        )
        file_id = cursor.lastrowid
        self._update_fts(conn, file_id, file_path, file_name, [])
        conn.commit()
        return file_id

    def get_file_id(self, file_path: str) -> Optional[int]:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT id FROM files WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row["id"] if row else None

    def delete_file(self, file_path: str):
        """Remove file and its tags (via cascade) and from FTS."""
        conn = self._get_connection()
        conn.execute("DELETE FROM files WHERE file_path = ?", (file_path,))
        conn.execute("DELETE FROM files_fts WHERE file_path = ?", (file_path,))
        conn.commit()

    # ------------------------------------------------------------------
    # Tag CRUD
    # ------------------------------------------------------------------

    def save_tags(self, file_path: str, tags: List[str]):
        """Replace all tags for a file and update the FTS index."""
        conn = self._get_connection()
        file_id = self.get_file_id(file_path)
        if file_id is None:
            file_name = Path(file_path).name
            file_id = self.add_file(file_path, file_name)

        # Clear old tags
        conn.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))

        # Insert new tags
        conn.executemany(
            "INSERT INTO file_tags (file_id, tag) VALUES (?, ?)",
            [(file_id, tag) for tag in tags],
        )

        # Update FTS index
        self._update_fts(conn, file_id, file_path, Path(file_path).name, tags)
        conn.commit()

    def get_tags(self, file_path: str) -> List[str]:
        conn = self._get_connection()
        file_id = self.get_file_id(file_path)
        if file_id is None:
            return []
        rows = conn.execute(
            "SELECT tag FROM file_tags WHERE file_id = ?", (file_id,)
        ).fetchall()
        return [r["tag"] for r in rows]

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_all_files(self) -> List[Dict]:
        """Return a list of dicts: {file_path, file_name, tags}."""
        conn = self._get_connection()
        files = conn.execute("SELECT id, file_path, file_name FROM files").fetchall()
        result = []
        for f in files:
            tags = conn.execute(
                "SELECT tag FROM file_tags WHERE file_id = ?", (f["id"],)
            ).fetchall()
            result.append({
                "path": f["file_path"],
                "name": f["file_name"],
                "tags": [t["tag"] for t in tags],
            })
        return result

    def search_fts(self, query: str) -> List[Dict]:
        """Full-text search via FTS5. Returns matching file dicts."""
        conn = self._get_connection()
        # FTS5 match query — wrap each term with * for prefix matching
        terms = [t.strip() for t in query.split() if t.strip()]
        if not terms:
            return self.get_all_files()

        fts_query = " OR ".join(f'"{t}"*' for t in terms)

        try:
            rows = conn.execute(
                "SELECT file_path, file_name, tags FROM files_fts WHERE files_fts MATCH ?",
                (fts_query,),
            ).fetchall()
        except sqlite3.OperationalError:
            return []

        result = []
        for r in rows:
            tag_list = [t.strip() for t in r["tags"].split(",") if t.strip()] if r["tags"] else []
            result.append({
                "path": r["file_path"],
                "name": r["file_name"],
                "tags": tag_list,
            })
        return result

    # ------------------------------------------------------------------
    # FTS helpers
    # ------------------------------------------------------------------

    def _update_fts(self, conn: sqlite3.Connection, file_id: int,
                    file_path: str, file_name: str, tags: List[str]):
        """Insert or replace an FTS row for the given file."""
        # Delete old FTS row (if any)
        conn.execute(
            "DELETE FROM files_fts WHERE file_path = ?", (file_path,)
        )
        # Insert new
        tags_str = ", ".join(tags)
        conn.execute(
            "INSERT INTO files_fts (file_path, file_name, tags) VALUES (?, ?, ?)",
            (file_path, file_name, tags_str),
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
