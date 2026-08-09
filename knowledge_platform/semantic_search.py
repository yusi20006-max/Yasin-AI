"""Semantic retrieval for the YasinAI Knowledge Platform.

The embedding implementation is intentionally dependency-free. Vector records
can be kept in memory for library use or persisted through SQLite for durable
application use.
"""

from __future__ import annotations

import logging
import math
import os
import re
from typing import Any, Dict, List, Optional, Protocol

from knowledge_platform.vector_store import SQLiteVectorStore

logger = logging.getLogger(__name__)


class VectorStoreProtocol(Protocol):
    def store_vector(self, text_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None: ...
    def get_all_records(self) -> List[Dict[str, Any]]: ...
    def clear(self) -> None: ...

    def close(self) -> None: ...


class EmbeddingEngine:
    """Generate TF-IDF-like vectors using only the Python standard library."""

    def __init__(self) -> None:
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.documents: List[str] = []

    def tokenize(self, text: str) -> List[str]:
        text_clean = re.sub(r"[^\w\s]", "", text.lower())
        return [word for word in text_clean.split() if word]

    def fit(self, texts: List[str]) -> None:
        self.documents = list(texts)
        self.vocabulary.clear()
        self.idf.clear()
        if not texts:
            return

        occurrences: Dict[str, int] = {}
        for doc in texts:
            for token in set(self.tokenize(doc)):
                if token not in self.vocabulary:
                    self.vocabulary[token] = len(self.vocabulary)
                occurrences[token] = occurrences.get(token, 0) + 1

        count = len(texts)
        for term, frequency in occurrences.items():
            self.idf[term] = math.log((1 + count) / (1 + frequency)) + 1

    def get_embedding(self, text: str) -> List[float]:
        vector = [0.0] * max(len(self.vocabulary), 1)
        if not self.vocabulary:
            return vector
        tokens = self.tokenize(text)
        if not tokens:
            return vector

        tf: Dict[str, int] = {}
        for token in tokens:
            if token in self.vocabulary:
                tf[token] = tf.get(token, 0) + 1
        for term, count in tf.items():
            vector[self.vocabulary[term]] = (count / len(tokens)) * self.idf.get(term, 1.0)

        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector


class VectorStore:
    """In-memory vector store retained as the lightweight library backend."""

    def __init__(self) -> None:
        self.records: List[Dict[str, Any]] = []

    def store_vector(self, text_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        self.records = [record for record in self.records if record["id"] != text_id]
        self.records.append({"id": text_id, "vector": vector, "metadata": metadata or {}})

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.records

    def clear(self) -> None:
        self.records.clear()


class SemanticSearch:
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(value * value for value in v1))
        norm_b = math.sqrt(sum(value * value for value in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(self, query_vector: List[float], records: List[Dict[str, Any]], limit: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        scored = []
        for record in records:
            score = self.cosine_similarity(query_vector, record["vector"])
            if score >= threshold:
                scored.append({"id": record["id"], "score": score, "metadata": record["metadata"]})
        scored.sort(key=lambda result: result["score"], reverse=True)
        return scored[:limit]


class Retriever:
    """Persistent semantic retriever with a pluggable vector store."""

    def __init__(self, store: Optional[VectorStoreProtocol] = None, path: Optional[str] = None) -> None:
        self.embedding_engine = EmbeddingEngine()
        if store is not None:
            self.vector_store = store
        else:
            default_path = os.environ.get("YASINAI_VECTOR_PATH", "~/.yasinai/vectors.db")
            self.vector_store = SQLiteVectorStore(path or default_path)
        self.search_engine = SemanticSearch()
        self._rebuild_embeddings()

    def _rebuild_embeddings(self) -> None:
        records = self.vector_store.get_all_records()
        texts = [record["metadata"].get("text", "") for record in records]
        self.embedding_engine.fit(texts)
        for record in records:
            record["vector"] = self.embedding_engine.get_embedding(record["metadata"].get("text", ""))
            self.vector_store.store_vector(record["id"], record["vector"], record["metadata"])

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        meta = dict(metadata or {})
        meta["text"] = text
        self.vector_store.store_vector(doc_id, [], meta)
        self._rebuild_embeddings()

    def retrieve(self, query: str, limit: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        records = self.vector_store.get_all_records()
        if not records or limit <= 0:
            return []
        if not query or not query.strip():
            results = [
                {"id": record["id"], "score": 0.0, "metadata": record["metadata"]}
                for record in records
            ]
            return results[:limit] if threshold <= 0.0 else []

        query_vector = self.embedding_engine.get_embedding(query)
        results = self.search_engine.search(query_vector, records, limit=len(records), threshold=threshold)
        for result in results:
            text = result["metadata"].get("text", "")
            if query.lower() in text.lower():
                result["score"] = max(result["score"], 1.0)
        results.sort(key=lambda result: result["score"], reverse=True)
        return results[:limit]

    def delete(self, doc_id: str) -> bool:
        deleted = self.vector_store.delete(doc_id) if hasattr(self.vector_store, "delete") else False
        if deleted:
            self._rebuild_embeddings()
        return deleted

    def clear(self) -> None:
        self.vector_store.clear()
        self.embedding_engine.fit([])

    def close(self) -> None:
        close = getattr(self.vector_store, "close", None)
        if close:
            close()


__all__ = ["EmbeddingEngine", "VectorStore", "SQLiteVectorStore", "SemanticSearch", "Retriever"]
