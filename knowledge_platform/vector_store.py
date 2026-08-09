"""Durable vector storage for the Knowledge Platform."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteVectorStore:
    """SQLite-backed vector store using JSON-encoded vectors and metadata."""

    def __init__(self, path: str | Path = "~/.yasinai/vectors.db") -> None:
        self.path = Path(path).expanduser()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                vector TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def store_vector(self, text_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        self._connection.execute(
            """INSERT INTO vectors(id, vector, metadata) VALUES (?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 vector=excluded.vector,
                 metadata=excluded.metadata""",
            (
                text_id,
                json.dumps(vector),
                json.dumps(metadata or {}, ensure_ascii=False, default=str),
            ),
        )
        self._connection.commit()

    def get_all_records(self) -> List[Dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT id, vector, metadata FROM vectors ORDER BY id"
        ).fetchall()
        return [
            {
                "id": row["id"],
                "vector": json.loads(row["vector"]),
                "metadata": json.loads(row["metadata"]),
            }
            for row in rows
        ]

    def delete(self, text_id: str) -> bool:
        cursor = self._connection.execute("DELETE FROM vectors WHERE id = ?", (text_id,))
        self._connection.commit()
        return cursor.rowcount > 0

    def clear(self) -> None:
        self._connection.execute("DELETE FROM vectors")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
