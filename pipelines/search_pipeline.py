"""Search Pipeline orchestrating QueryProcessor, SimilarityEngine, SnippetExtractor, and MetadataDB."""

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import chromadb
from config.settings import VECTOR_STORE_DIR
from src.search.metadata_db import MetadataDB
from src.search.query_processor import QueryProcessor
from src.search.similarity_engine import SimilarityEngine
from src.search.snippet_extractor import SnippetExtractor

logger = logging.getLogger(__name__)


class SearchPipeline:
    """Orchestrator pipeline connecting QueryProcessor, SimilarityEngine, SnippetExtractor, and MetadataDB."""

    def __init__(
        self,
        vector_store_dir: Optional[Any] = None,
        query_processor: Optional[QueryProcessor] = None,
        similarity_engine: Optional[SimilarityEngine] = None,
        snippet_extractor: Optional[SnippetExtractor] = None,
        metadata_db: Optional[MetadataDB] = None,
    ):
        """Initializes the search pipeline and connects persistent ChromaDB collections."""
        v_dir = vector_store_dir or VECTOR_STORE_DIR
        self.client = chromadb.PersistentClient(path=str(v_dir))

        segment_col = self.client.get_or_create_collection("video_segments")
        summary_col = self.client.get_or_create_collection("anime_summaries")

        self.query_processor = query_processor or QueryProcessor()
        self.similarity_engine = similarity_engine or SimilarityEngine(
            segment_collection=segment_col,
            summary_collection=summary_col,
        )
        self.snippet_extractor = snippet_extractor or SnippetExtractor()
        self.metadata_db = metadata_db or MetadataDB()

    def run_search(
        self,
        query: str,
        top_k: int = 4,
        search_scope: str = "both",
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Runs end-to-end semantic video search workflow.

        Workflow:
        1. Sanitize & process query string inputs using QueryProcessor.
        2. Execute two-stage retrieval + re-ranking via SimilarityEngine.
        3. Merge overlapping transcript snippets & format timestamps via SnippetExtractor.
        4. Fetch full video asset metadata from MetadataDB to attach to each search hit.

        Args:
            query: The user search input string.
            top_k: Maximum number of search result snippets to return.
            search_scope: Scope ('transcript', 'summary', or 'both').
            filters: Optional dictionary of metadata filter conditions.

        Returns:
            Dictionary containing query, total_results, execution_time_ms, and results list.
        """
        start_time = time.perf_counter()

        # Step 1: Query Processing
        processed_query = self.query_processor.process(
            raw_query=query,
            filters=filters,
            search_scope=search_scope,
        )

        # Step 2: Similarity Engine Search & Re-ranking
        raw_hits = self.similarity_engine.search(
            query=processed_query.clean_query,
            top_k=top_k,
            search_scope=processed_query.search_scope,
            metadata_filters=processed_query.metadata_filters,
        )

        # Step 3: Snippet Extraction and Merging
        formatted_snippets = self.snippet_extractor.extract_and_merge(raw_hits)

        # Step 4: Metadata Enrichment
        enriched_results: List[Dict[str, Any]] = []

        for snippet in formatted_snippets:
            video_meta = self.metadata_db.get_video_metadata(snippet.video_id)
            if not video_meta.get("video_path"):
                logger.info("Skipping search result for unavailable video: %s", snippet.video_id)
                continue

            hit_dict = snippet.model_dump()

            # Combine snippet details with video metadata
            hit_dict.update({
                "video_id": video_meta.get("id", snippet.video_id),
                "video_title": video_meta.get("video_title", snippet.video_id),
                "season": video_meta.get("season", "Season 1"),
                "episode": video_meta.get("episode", "Episode"),
                "filename": video_meta.get("filename", f"{snippet.video_id}.mp4"),
                "media_url": video_meta.get("media_url", f"/media/{snippet.video_id}.mp4"),
                "watch_url": f"/video/{quote(video_meta.get('id', snippet.video_id), safe='')}?t={snippet.start_seconds}",
                "semantic_match_percent": int(round(snippet.confidence_score)),
            })

            enriched_results.append(hit_dict)
            if len(enriched_results) >= top_k:
                break

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "query": processed_query.clean_query,
            "total_results": len(enriched_results),
            "execution_time_ms": round(elapsed_ms, 2),
            "results": enriched_results[:top_k],
        }
