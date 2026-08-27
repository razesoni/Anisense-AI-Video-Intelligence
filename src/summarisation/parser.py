import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# --- Pydantic Schema Definitions ---

class KeyMoment(BaseModel):
    timestamp_start: float = Field(..., description="Start time in seconds")
    timestamp_end: float = Field(..., description="End time in seconds")
    label: str = Field(..., description="Short title for the event or scene")
    description: str = Field(..., description="Brief description of the event")

class SummaryResponse(BaseModel):
    overview: str = Field(..., description="High-level narrative summary")
    key_points: List[str] = Field(default_factory=list, description="Bullet point takeaways")
    key_moments: List[KeyMoment] = Field(default_factory=list, description="Timestamped chapter markers")
    tags: List[str] = Field(default_factory=list, description="Keywords or genres")


class MapSegmentOutput(BaseModel):
    segment_summary: str = Field(default="", description="1-2 sentence summary of this segment")
    local_key_points: List[str] = Field(default_factory=list, description="Local key events in segment")
    notable_moments: List[KeyMoment] = Field(default_factory=list, description="Notable scenes in segment")


# --- Parsing & Cleaning Logic ---

def extract_json_str(raw_llm_response: str) -> str:
    """
    Extracts pure JSON substring from raw model output, 
    stripping markdown formatting or extra conversational fluff.
    """
    text = raw_llm_response.strip()
    
    # Remove markdown code blocks if present (```json ... ``` or ``` ... ```)
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if match:
        text = match.group(1).strip()
    else:
        # If no markdown fences, attempt to find first '{' and last '}'
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1].strip()
        elif first_brace != -1:
            text = text[first_brace:].strip()

    return text


def repair_truncated_json(json_str: str) -> str:
    """
    Attempts basic repair on truncated JSON strings (e.g. closing open quotes and braces).
    """
    text = json_str.strip()
    if not text.startswith('{'):
        return text

    # Remove trailing unclosed comma or colon
    text = re.sub(r'[,:\s]+$', '', text)
    
    # Count open/close quotes and brackets
    in_string = False
    escape = False
    stack = []
    
    for char in text:
        if escape:
            escape = False
            continue
        if char == '\\':
            escape = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if not in_string:
            if char in '{[':
                stack.append(char)
            elif char in '}]':
                if stack:
                    stack.pop()

    if in_string:
        text += '"'

    # Close any unclosed arrays or objects in reverse order
    for open_char in reversed(stack):
        if open_char == '{':
            text += '}'
        elif open_char == '[':
            text += ']'

    return text


def parse_summary_output(raw_llm_response: str) -> Optional[SummaryResponse]:
    """
    Parses and validates LLM output into a typed Pydantic object.
    """
    if not raw_llm_response:
        return None

    cleaned_json_str = extract_json_str(raw_llm_response)
    
    for attempt in [cleaned_json_str, repair_truncated_json(cleaned_json_str)]:
        try:
            data = json.loads(attempt)
            if isinstance(data, dict):
                return SummaryResponse(
                    overview=data.get("overview", "No overview provided."),
                    key_points=data.get("key_points", []),
                    key_moments=[
                        KeyMoment(**m) for m in data.get("key_moments", [])
                        if isinstance(m, dict) and "timestamp_start" in m and "timestamp_end" in m
                    ],
                    tags=data.get("tags", [])
                )
        except Exception:
            continue
            
    print(f"Error parsing LLM response. Raw string: {raw_llm_response[:100]}...")
    return None


def parse_map_output(raw_llm_response: str) -> Optional[MapSegmentOutput]:
    """
    Parses and validates a Map phase batch LLM output.
    """
    if not raw_llm_response:
        return None

    cleaned_json_str = extract_json_str(raw_llm_response)
    
    for attempt in [cleaned_json_str, repair_truncated_json(cleaned_json_str)]:
        try:
            data = json.loads(attempt)
            if isinstance(data, dict):
                moments = []
                raw_moments = data.get("notable_moments", [])
                if isinstance(raw_moments, list):
                    for m in raw_moments:
                        if isinstance(m, dict) and "timestamp_start" in m and "timestamp_end" in m:
                            try:
                                moments.append(KeyMoment(
                                    timestamp_start=float(m["timestamp_start"]),
                                    timestamp_end=float(m["timestamp_end"]),
                                    label=str(m.get("label", "Key Scene")),
                                    description=str(m.get("description", ""))
                                ))
                            except (ValueError, TypeError):
                                pass
                return MapSegmentOutput(
                    segment_summary=str(data.get("segment_summary", "")),
                    local_key_points=[str(p) for p in data.get("local_key_points", []) if p],
                    notable_moments=moments
                )
        except Exception:
            continue

    print(f"Error parsing Map LLM response: {raw_llm_response[:100]}...")
    return None


def generate_fallback_summary(transcript_chunks: list[dict], media_title: str = "Video") -> SummaryResponse:
    """
    Generates a high-quality fallback summary directly from transcript chunks
    when LLM generation or parsing is unavailable.
    """
    clean_title = media_title.replace("-", " ").replace("_", " ").title()
    
    if not transcript_chunks:
        return SummaryResponse(
            overview=f"Video content processing completed for '{clean_title}'. Transcript contains no readable dialogue.",
            key_points=[f"Processed video file: '{clean_title}'."],
            key_moments=[],
            tags=[clean_title, "Anime", "Video Intelligence"]
        )

    # Gather full text segments
    sentences = []
    key_moments: list[KeyMoment] = []
    
    # Take up to 5 representative key moments throughout the video timeline
    chunk_step = max(1, len(transcript_chunks) // 5)
    for i in range(0, len(transcript_chunks), chunk_step):
        chunk = transcript_chunks[i]
        text = chunk.get("text", "").strip()
        if text and len(key_moments) < 5:
            start = float(chunk.get("start", 0.0))
            end = float(chunk.get("end", start + 5.0))
            label = f"Scene {len(key_moments) + 1}"
            desc = text[:120] + "..." if len(text) > 120 else text
            key_moments.append(
                KeyMoment(
                    timestamp_start=round(start, 2),
                    timestamp_end=round(end, 2),
                    label=label,
                    description=desc
                )
            )

    all_texts = [c.get("text", "").strip() for c in transcript_chunks if c.get("text", "").strip()]
    full_text_sample = " ".join(all_texts[:10])
    
    overview = (
        f"Summary for '{clean_title}': This media covers key interactions and narrative events. "
        f"{full_text_sample[:250]}..." if full_text_sample else f"Video ingestion and transcription completed for '{clean_title}'."
    )
    
    key_points = [
        f"Media title: {clean_title}",
        f"Total transcript segments processed: {len(transcript_chunks)}",
        f"Initial dialogue preview: {all_texts[0][:100]}..." if all_texts else "Audio content indexed successfully."
    ]
    if len(all_texts) > 3:
        key_points.append(f"Mid-point dialogue preview: {all_texts[len(all_texts)//2][:100]}...")

    # Extract tags from title
    title_words = [w for w in clean_title.split() if len(w) > 2]
    tags = list(dict.fromkeys(title_words + ["Anime", "AI Summary", "Ingested"]))

    return SummaryResponse(
        overview=overview,
        key_points=key_points,
        key_moments=key_moments,
        tags=tags
    )