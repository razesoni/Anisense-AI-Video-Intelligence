"""Snippet extractor module for formatting timestamps and merging overlapping/adjacent search hits."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FormattedSnippet(BaseModel):
    """Payload representing a deduplicated, formatted video search result snippet."""
    video_id: str = Field(description="Unique identifier of the video asset")
    start_seconds: float = Field(description="Start time in seconds")
    end_seconds: float = Field(description="End time in seconds")
    timestamp_label: str = Field(description="Human-readable timestamp display string (e.g. '08:17 - 08:35')")
    matched_text: str = Field(description="Extracted transcript segment or summary snippet text")
    confidence_score: float = Field(description="Normalized similarity/relevance score percentage (0-100)")
    source: str = Field(description="Source origin: 'transcript' or 'summary'")


def format_timestamp(seconds: float) -> str:
    """Formats floating-point seconds into human-readable timestamp strings (HH:MM:SS or MM:SS).

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted string (e.g. '08:17' or '01:15:30').
    """
    total_seconds = int(round(max(0.0, seconds)))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class SnippetExtractor:
    """Extractor responsible for deduplicating, padding, merging, and formatting search hit snippets."""

    def __init__(self, default_padding: float = 5.0):
        self.default_padding = default_padding

    def extract_and_merge(
        self,
        raw_results: List[Dict[str, Any]],
        padding: Optional[float] = None,
    ) -> List[FormattedSnippet]:
        """Merges overlapping or adjacent transcript hits from the same video and formats timestamps.

        Args:
            raw_results: List of raw search hit dictionaries from SimilarityEngine.
            padding: Optional padding in seconds to expand snippet boundaries.

        Returns:
            List of FormattedSnippet instances ready for client consumption.
        """
        if not raw_results:
            return []

        pad = padding if padding is not None else self.default_padding
        transcript_hits: List[Dict[str, Any]] = []
        summary_hits: List[FormattedSnippet] = []

        for item in raw_results:
            source = item.get("source", "transcript")
            video_id = str(item.get("video_id") or item.get("id") or "unknown")
            text = str(item.get("text") or item.get("document") or "").strip()
            score = float(item.get("confidence_score") or item.get("score") or item.get("rrf_score") or 0.0)

            if source == "summary":
                summary_hits.append(
                    FormattedSnippet(
                        video_id=video_id,
                        start_seconds=0.0,
                        end_seconds=0.0,
                        timestamp_label="Full Episode Summary",
                        matched_text=text,
                        confidence_score=round(score, 1),
                        source="summary",
                    )
                )
            else:
                start_sec = float(item.get("start_seconds") or item.get("start_time") or 0.0)
                end_sec = float(item.get("end_seconds") or item.get("end_time") or start_sec + 5.0)
                transcript_hits.append({
                    "video_id": video_id,
                    "start_seconds": start_sec,
                    "end_seconds": end_sec,
                    "text": text,
                    "score": score,
                    "source": "transcript",
                })

        # Process and merge transcript hits
        merged_transcript_snippets: List[FormattedSnippet] = []
        if transcript_hits:
            # Sort chronologically by video_id, then by start_seconds
            sorted_hits = sorted(transcript_hits, key=lambda x: (x["video_id"], x["start_seconds"]))

            current_group: Optional[Dict[str, Any]] = None

            for hit in sorted_hits:
                vid = hit["video_id"]
                orig_start = hit["start_seconds"]
                orig_end = hit["end_seconds"]
                padded_start = max(0.0, orig_start - pad)
                padded_end = orig_end + pad

                if current_group is None:
                    current_group = {
                        "video_id": vid,
                        "start_seconds": padded_start,
                        "end_seconds": padded_end,
                        "texts": [hit["text"]],
                        "max_score": hit["score"],
                    }
                    continue

                # Check if belongs to same video and overlaps/adjacent
                if (
                    hit["video_id"] == current_group["video_id"]
                    and padded_start <= current_group["end_seconds"]
                ):
                    current_group["end_seconds"] = max(current_group["end_seconds"], padded_end)
                    if hit["text"] not in current_group["texts"]:
                        current_group["texts"].append(hit["text"])
                    current_group["max_score"] = max(current_group["max_score"], hit["score"])
                else:
                    # Flush current group
                    merged_transcript_snippets.append(self._build_snippet(current_group))
                    current_group = {
                        "video_id": vid,
                        "start_seconds": padded_start,
                        "end_seconds": padded_end,
                        "texts": [hit["text"]],
                        "max_score": hit["score"],
                    }

            if current_group is not None:
                merged_transcript_snippets.append(self._build_snippet(current_group))

        # Combine summary hits and transcript hits
        all_snippets = merged_transcript_snippets + summary_hits
        # Sort by confidence score descending
        all_snippets.sort(key=lambda s: s.confidence_score, reverse=True)
        return all_snippets

    def _build_snippet(self, group: Dict[str, Any]) -> FormattedSnippet:
        start_sec = group["start_seconds"]
        end_sec = group["end_seconds"]
        start_str = format_timestamp(start_sec)
        end_str = format_timestamp(end_sec)

        if start_str == end_str:
            ts_label = start_str
        else:
            ts_label = f"{start_str} - {end_str}"

        combined_text = " ".join(group["texts"]).strip()

        return FormattedSnippet(
            video_id=group["video_id"],
            start_seconds=round(start_sec, 2),
            end_seconds=round(end_sec, 2),
            timestamp_label=ts_label,
            matched_text=combined_text,
            confidence_score=round(group["max_score"], 1),
            source="transcript",
        )


def format_video_snippets(fused_results: List[Dict[str, Any]], padding: float = 5.0) -> List[Dict[str, Any]]:
    """Helper function for backward compatibility returning plain dictionaries."""
    extractor = SnippetExtractor(default_padding=padding)
    snippets = extractor.extract_and_merge(fused_results, padding=padding)
    return [s.model_dump() for s in snippets]