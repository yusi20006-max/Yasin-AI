"""Local semantic search engine without external service dependencies."""

import math
import re
from typing import List, Dict, Tuple, Set, Any


class LocalSemanticRetriever:
    """A purely local information retrieval engine utilizing TF-IDF and Cosine Similarity."""

    def __init__(self):
        """Initializes the retriever."""
        # A list of dictionaries representing documents. Each has "id", "text", "metadata"
        self.documents: List[Dict[str, Any]] = []

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizes text into clean, lowercase words.

        Args:
            text: Input string.

        Returns:
            List of normalized word tokens.
        """
        # Convert to lowercase and match alphanumeric words
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def add_document(self, doc_id: str, text: str, metadata: Any = None) -> None:
        """Adds a document to the local corpus.

        Args:
            doc_id: Unique identifier for the document.
            text: The text content of the document.
            metadata: Associated metadata (e.g. timestamp, tags, memory type).
        """
        # Remove document if it already exists to prevent duplicate indexes
        self.documents = [doc for doc in self.documents if doc["id"] != doc_id]
        self.documents.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        })

    def search(self, query: str, limit: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Performs a semantic/lexical similarity search using TF-IDF.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            A list of tuples containing (Document, Similarity Score).
        """
        if not self.documents or not query.strip():
            return []

        # 1. Tokenize query and all documents
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        doc_tokens_list = [self._tokenize(doc["text"]) for doc in self.documents]

        # 2. Compute Document Frequencies (DF) for IDF calculation
        # IDF(t) = log(1 + (Total Documents) / (Documents containing term t))
        all_terms: Set[str] = set(query_tokens)
        df_counts: Dict[str, int] = {term: 0 for term in all_terms}

        for doc_tokens in doc_tokens_list:
            doc_unique_terms = set(doc_tokens)
            for term in all_terms:
                if term in doc_unique_terms:
                    df_counts[term] += 1

        num_docs = len(self.documents)
        idf: Dict[str, float] = {}
        for term, df in df_counts.items():
            # Standard smooth-IDF formula
            idf[term] = math.log(1 + (num_docs / (df + 1)))

        # 3. Calculate Query Vector (TF-IDF)
        query_tf: Dict[str, int] = {}
        for term in query_tokens:
            query_tf[term] = query_tf.get(term, 0) + 1

        query_vector: Dict[str, float] = {}
        query_norm_sq = 0.0
        for term in query_tokens:
            tf = query_tf[term]
            tfidf = tf * idf[term]
            query_vector[term] = tfidf
            query_norm_sq += tfidf * tfidf

        query_norm = math.sqrt(query_norm_sq)
        if query_norm == 0:
            return []

        # 4. Calculate Cosine Similarity with each Document Vector
        scored_docs: List[Tuple[Dict[str, Any], float]] = []

        for i, doc in enumerate(self.documents):
            doc_tokens = doc_tokens_list[i]
            if not doc_tokens:
                continue

            doc_tf: Dict[str, int] = {}
            for term in doc_tokens:
                doc_tf[term] = doc_tf.get(term, 0) + 1

            # Compute TF-IDF for document terms that appear in query
            dot_product = 0.0
            doc_norm_sq = 0.0

            # Calculate the full norm for this doc vector (relative to the query term space)
            # To be fair and robust, we calculate norm on all doc terms.
            # However, smooth IDF is only calculated for query terms, so we fallback to a default
            # log(1 + N) IDF for non-query terms so that we have complete vectors.
            for term, tf in doc_tf.items():
                term_idf = idf.get(term, math.log(1 + num_docs))
                tfidf = tf * term_idf
                doc_norm_sq += tfidf * tfidf
                if term in query_vector:
                    dot_product += query_vector[term] * tfidf

            doc_norm = math.sqrt(doc_norm_sq)
            if doc_norm == 0:
                continue

            similarity = dot_product / (query_norm * doc_norm)
            if similarity > 0:
                scored_docs.append((doc, similarity))

        # Sort descending by score, and limit
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:limit]
