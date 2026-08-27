"""
Prompt templates for video & anime summarisation (Map-Reduce chunking architecture).
"""

SYSTEM_PROMPT = """You are an expert AI video content analyst and summariser.
Your task is to analyze transcript segments (which include start and end timestamps in seconds) and provide a concise, structured summary.

Always respond in strictly valid JSON matching the exact schema requested. Do not include markdown code block wraps (e.g. ```json ... ```) or conversational commentary outside the JSON.
"""

MAP_PROMPT_TEMPLATE = """Analyze the following transcript segment batch from media: "{media_title}".

Transcript Segment:
{batch_text}

Generate a structured JSON object with the following exact keys:
1. "segment_summary": A concise 1-2 sentence summary of what occurs in this segment.
2. "local_key_points": A list of 1-3 key events or plot points in this segment.
3. "notable_moments": A list of notable scenes in this segment. Each item must be an object with:
   - "timestamp_start": float (start time in seconds from transcript)
   - "timestamp_end": float (end time in seconds from transcript)
   - "label": short string title for the moment
   - "description": 1-2 sentence description of what happens
"""

VIDEO_SUMMARY_TEMPLATE = """You are synthesizing segment analyses collected across the media: "{media_title}".

Aggregated Segment Data:
{aggregated_data}

Generate the final structured JSON summary with the following exact keys:
1. "overview": A cohesive paragraph (3-5 sentences) summarizing the main theme or plot of the entire video.
2. "key_points": A list of 3-6 bullet points covering core takeaways or major developments across the video.
3. "key_moments": A list of notable scenes, highlights, or topic transitions. Each item must be an object with:
   - "timestamp_start": float (exact start time in seconds)
   - "timestamp_end": float (exact end time in seconds)
   - "label": short string title for the moment
   - "description": 1-2 sentence description of what happens
4. "tags": A list of 3-7 relevant keywords or genre tags (e.g., ["Action", "Romance", "Betrayal"]).

Ensure all timestamps align with the provided segment numbers.
"""


def batch_transcript_chunks(
    transcript_chunks: list[dict], 
    batch_size: int = 50
) -> list[str]:
    """
    Groups raw transcript chunks into text blocks formatted strictly as
    '[{start}s - {end}s] {text}' to optimize token usage.
    """
    if not transcript_chunks:
        return []

    formatted_lines = []
    for chunk in transcript_chunks:
        start = round(float(chunk.get("start", 0.0)), 2)
        end = round(float(chunk.get("end", 0.0)), 2)
        text = chunk.get("text", "").strip()
        if text:
            formatted_lines.append(f"[{start}s - {end}s] {text}")

    batches = []
    for i in range(0, len(formatted_lines), batch_size):
        batch_lines = formatted_lines[i : i + batch_size]
        batches.append("\n".join(batch_lines))

    return batches


def format_map_prompt(batch_text: str, media_title: str = "Unknown Video") -> str:
    """Formats a single transcript batch into a Map prompt."""
    return MAP_PROMPT_TEMPLATE.format(
        media_title=media_title,
        batch_text=batch_text
    )


def format_reduce_prompt(aggregated_data: str, media_title: str = "Unknown Video") -> str:
    """Formats the aggregated map results into a Reduce prompt for final summary synthesis."""
    return VIDEO_SUMMARY_TEMPLATE.format(
        media_title=media_title,
        aggregated_data=aggregated_data
    )


def format_summary_prompt(
    transcript_chunks: list[dict], 
    media_title: str = "Unknown Video", 
    max_words: int | None = None,
) -> str:
    """Legacy helper: formats all transcript chunks into a single reduce prompt payload."""
    batches = batch_transcript_chunks(transcript_chunks, batch_size=50)
    aggregated_text = "\n\n".join(batches)
    return format_reduce_prompt(aggregated_data=aggregated_text, media_title=media_title)