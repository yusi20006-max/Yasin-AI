"""Durable storage abstraction for YasinAI long-term memory."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteMemoryStore:
    """Small, dependency-free SQLite-backed store for long-term memories."""

    def __init__(self, path: str | Path = "~/.yasinai/memory.db") -> None:
        self.path = Path(path).expanduser()
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(str(self.path))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA busy_timeout = 5000")
        if str(self.path) != ":memory:":
            self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def store(self, key: str, content: Any, timestamp: float, metadata: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(content, ensure_ascii=False, default=str)
        metadata_json = json.dumps(metadata, ensure_ascii=False, default=str)
        self._connection.execute(
            """INSERT INTO memories(key, content, timestamp, metadata)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET
                 content=excluded.content,
                 timestamp=excluded.timestamp,
                 metadata=excluded.metadata""",
            (key, payload, timestamp, metadata_json),
        )
        self._connection.commit()
        return {"key": key, "content": content, "timestamp": timestamp, "metadata": metadata}

    def retrieve(self, key: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT key, content, timestamp, metadata FROM memories WHERE key = ?", (key,)
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def delete(self, key: str) -> bool:
        cursor = self._connection.execute("DELETE FROM memories WHERE key = ?", (key,))
        self._connection.commit()
        return cursor.rowcount > 0

    def list_all(self) -> list[dict[str, Any]]:
        rows = self._connection.execute(
            "SELECT key, content, timestamp, metadata FROM memories ORDER BY timestamp DESC"
        ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def clear(self) -> None:
        self._connection.execute("DELETE FROM memories")
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "key": row["key"],
            "content": json.loads(row["content"]),
            "timestamp": row["timestamp"],
            "metadata": json.loads(row["metadata"]),
        }
