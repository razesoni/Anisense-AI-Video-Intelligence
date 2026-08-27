"""Similarity Engine implementing two-stage vector retrieval and Cross-Encoder re-ranking."""

import logging
import math
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SimilarityEngine:
    """Two-stage similarity search engine combining bi-encoder retrieval and cross-encoder re-ranking."""

    def __init__(
        self,
        segment_collection: Optional[Any] = None,
        summary_collection: Optional[Any] = None,
        cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        transcript_priority_multiplier: float = 1.05,
    ):
        """Initializes the similarity engine dynamically with ChromaDB collections and a CrossEncoder model.

        Args:
            segment_collection: Dynamic ChromaDB collection containing video transcript segments.
            summary_collection: Dynamic ChromaDB collection containing video summaries.
            cross_encoder_model: Model name for cross-encoder re-ranking.
            transcript_priority_multiplier: Multiplier boost (e.g. 1.05x) applied to transcript matches.
        """
        self.segment_collection = segment_collection
        self.summary_collection = summary_collection
        self.transcript_priority_multiplier = transcript_priority_multiplier
        self.cross_encoder_model_name = cross_encoder_model
        self.cross_encoder = None

        self._init_cross_encoder()

    def _init_cross_encoder(self) -> None:
        """Loads CrossEncoder model lazily with graceful error fallback if unavailable."""
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder model: {self.cross_encoder_model_name}")
            self.cross_encoder = CrossEncoder(self.cross_encoder_model_name)
        except Exception as e:
            logger.warning(
                f"Failed to load CrossEncoder model '{self.cross_encoder_model_name}': {e}. "
                "Will use bi-encoder distance fallback."
            )
            self.cross_encoder = None

    def search(
        self,
        query: str,
        top_k: int = 5,
        search_scope: str = "both",
        candidate_multiplier: int = 3,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Executes two-stage retrieval: Bi-Encoder retrieval followed by Cross-Encoder re-ranking.

        Args:
            query: Sanitized user query text string.
            top_k: Top k number of sorted results to return.
            search_scope: Scope filter ('transcript', 'summary', or 'both').
            candidate_multiplier: Candidate expansion factor (default 3x top_k).
            metadata_filters: Optional dictionary of ChromaDB metadata filter conditions.

        Returns:
            List of candidate hit dictionaries with confidence scores, sorted descending.
        """
        if not query or not query.strip():
            return []

        scope = search_scope.lower().strip() if search_scope else "both"
        candidate_pool_size = max(top_k * candidate_multiplier, top_k)
        candidates: List[Dict[str, Any]] = []

        # --- STAGE 1: Bi-Encoder Retrieval ---
        if scope in {"transcript", "both"} and self.segment_collection is not None:
            candidates.extend(
                self._query_collection(
                    collection=self.segment_collection,
                    query=query,
                    n_results=candidate_pool_size,
                    source="transcript",
                    metadata_filters=metadata_filters,
                )
            )

        if scope in {"summary", "both"} and self.summary_collection is not None:
            candidates.extend(
                self._query_collection(
                    collection=self.summary_collection,
                    query=query,
                    n_results=candidate_pool_size,
                    source="summary",
                    metadata_filters=metadata_filters,
                )
            )

        if not candidates:
            return []

        # --- STAGE 2: Cross-Encoder Re-ranking ---
        if self.cross_encoder is None:
            # Re-try loading in case package finished installing
            self._init_cross_encoder()

        if self.cross_encoder is not None:
            try:
                pairs = [(query, cand["text"]) for cand in candidates]
                scores = self.cross_encoder.predict(pairs)

                for i, score in enumerate(scores):
                    raw_logit = float(score)
                    # Convert raw logit to sigmoid probability [0, 1]
                    sigmoid_score = 1.0 / (1.0 + math.exp(-raw_logit))
                    score_percent = sigmoid_score * 100.0

                    # Apply granular transcript match boost
                    if candidates[i]["source"] == "transcript":
                        score_percent = min(100.0, score_percent * self.transcript_priority_multiplier)

                    candidates[i]["confidence_score"] = round(score_percent, 2)
            except Exception as e:
                logger.error(f"CrossEncoder re-ranking error: {e}. Using bi-encoder fallback scores.")
                self._fallback_scoring(candidates)
        else:
            self._fallback_scoring(candidates)

        # Sort candidates descending by final confidence score
        candidates.sort(key=lambda c: c["confidence_score"], reverse=True)
        return candidates[:top_k]

    def _query_collection(
        self,
        collection: Any,
        query: str,
        n_results: int,
        source: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Queries a ChromaDB collection instance safely."""
        hits: List[Dict[str, Any]] = []
        try:
            # Check item count in collection if available
            total_items = collection.count() if hasattr(collection, "count") else 100
            if total_items == 0:
                return []

            fetch_n = min(n_results, total_items)
            kwargs: Dict[str, Any] = {
                "query_texts": [query],
                "n_results": fetch_n,
            }
            if metadata_filters:
                kwargs["where"] = metadata_filters

            res = collection.query(**kwargs)

            if res and "documents" in res and res["documents"] and len(res["documents"]) > 0:
                docs = res["documents"][0]
                ids = res["ids"][0] if "ids" in res and res["ids"] else [f"{source}_{i}" for i in range(len(docs))]
                metas = res["metadatas"][0] if "metadatas" in res and res["metadatas"] else [{} for _ in docs]
                dists = res["distances"][0] if "distances" in res and res["distances"] else [1.0 for _ in docs]

                for doc, doc_id, meta, dist in zip(docs, ids, metas, dists):
                    dist_val = float(dist)
                    base_sim = max(0.0, (1.0 - dist_val / 2.0)) * 100.0

                    vid = meta.get("video_id") or meta.get("anime_name") or doc_id.rsplit("_", 1)[0]
                    start = float(meta.get("start_time") or meta.get("start_seconds") or 0.0)
                    end = float(meta.get("end_time") or meta.get("end_seconds") or (start + 5.0 if source == "transcript" else 0.0))

                    hits.append({
                        "id": doc_id,
                        "video_id": str(vid),
                        "text": str(doc),
                        "start_seconds": start,
                        "end_seconds": end,
                        "source": source,
                        "distance": dist_val,
                        "confidence_score": round(base_sim, 2),
                        "metadata": meta,
                    })
        except Exception as e:
            logger.error(f"Error querying ChromaDB collection ({source}): {e}")

        return hits

    def _fallback_scoring(self, candidates: List[Dict[str, Any]]) -> None:
        """Applies fallback scoring using bi-encoder distances when CrossEncoder is not available."""
        for cand in candidates:
            dist = cand.get("distance", 1.0)
            score = max(0.0, (1.0 - dist / 2.0)) * 100.0
            if cand["source"] == "transcript":
                score = min(100.0, score * self.transcript_priority_multiplier)
            cand["confidence_score"] = round(score, 2)