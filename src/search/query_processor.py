"""Query processor module for sanitizing and formatting search queries for vector and keyword search engines."""

import html
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProcessedQuery(BaseModel):
    """Container for processed search queries and associated filters."""
    raw_query: str = Field(description="Original user input query")
    clean_query: str = Field(description="Sanitized and trimmed query text")
    keyword_query: str = Field(description="Normalized query string suitable for BM25/keyword indexing")
    metadata_filters: Dict[str, Any] = Field(default_factory=dict, description="ChromaDB-compatible filter dictionary")
    search_scope: str = Field(default="both", description="Search target scope: 'transcript', 'summary', or 'both'")


class QueryProcessor:
    """Processor responsible for cleaning, sanitizing, and preparing search inputs."""

    def __init__(self, max_query_length: int = 500):
        self.max_query_length = max_query_length

    def sanitize(self, raw_query: str) -> str:
        """Sanitizes raw input text by stripping tags, normalizing whitespace, and unescaping HTML entities.
        
        Args:
            raw_query: The raw string provided by the user.

        Returns:
            Sanitized single-line query string.

        Raises:
            ValueError: If the query is empty or consists only of whitespace.
        """
        if not raw_query or not isinstance(raw_query, str):
            raise ValueError("Query string must be a non-empty string.")

        # 1. Unescape HTML entities
        text = html.unescape(raw_query)

        # 2. Strip any HTML/XML tags
        text = re.sub(r"<[^>]*>", "", text)

        # 3. Replace non-printable ASCII/control characters
        text = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", text)

        # 4. Normalize whitespace (tabs, newlines, multiple spaces -> single space)
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            raise ValueError("Query string contains no valid searchable text after sanitization.")

        # 5. Truncate if exceeds max allowed length
        if len(text) > self.max_query_length:
            text = text[: self.max_query_length].rstrip()

        return text

    def process(
        self,
        raw_query: str,
        filters: Optional[Dict[str, Any]] = None,
        search_scope: str = "both",
    ) -> ProcessedQuery:
        """Processes and formats a raw query string into a structured ProcessedQuery.

        Args:
            raw_query: The raw query input string.
            filters: Optional dictionary of metadata key-value filters.
            search_scope: Scope of search ('transcript', 'summary', or 'both').

        Returns:
            ProcessedQuery object with cleaned, normalized, and filter fields.
        """
        clean_text = self.sanitize(raw_query)

        # Normalize for keyword search
        try:
            from src.transcript_cleaning.normalizer import normalize_text
            keyword_text = normalize_text(clean_text)
            if not keyword_text:
                keyword_text = clean_text.lower()
        except Exception:
            keyword_text = clean_text.lower()

        # Build ChromaDB metadata filters
        chroma_filters: Dict[str, Any] = {}
        if filters:
            conditions: List[Dict[str, Any]] = [{k: {"$eq": v}} for k, v in filters.items() if v is not None]
            if len(conditions) == 1:
                chroma_filters = conditions[0]
            elif len(conditions) > 1:
                chroma_filters = {"$and": conditions}

        # Normalize search scope
        scope = search_scope.lower().strip() if search_scope else "both"
        if scope not in {"transcript", "summary", "both"}:
            scope = "both"

        return ProcessedQuery(
            raw_query=raw_query,
            clean_query=clean_text,
            keyword_query=keyword_text,
            metadata_filters=chroma_filters,
            search_scope=scope,
        )


def process_search_query(
    raw_query: str,
    filters: Optional[Dict[str, Any]] = None,
    search_scope: str = "both",
) -> Dict[str, Any]:
    """Helper function for backward compatibility with simple dictionary returns."""
    processor = QueryProcessor()
    processed = processor.process(raw_query, filters=filters, search_scope=search_scope)
    return processed.model_dump()