from _pytest import pytester_assertions
from _pytest import pytester_assertions
from _pytest import pytester_assertions
from _pytest import pytester_assertions
from _pytest import pytester_assertions
import json
from pathlib import Path
from config.settings import (
    settings,
    AUDIO_DIR,
    SUMMARY_DIR,
    VECTOR_STORE_DIR,
    CLEANED_TRANSCRIPTS,
    RAW_TRANSCRIPTS,
)
from src.audio_processing.extractor import AudioExtractor
from src.audio_processing.transcriber import AudioTranscriber
from src.transcript_cleaning.cleaner import clean_transcript
from src.transcript_cleaning.segmenter import segment_transcript
from src.indexing.vector_db import ChromaManager
from src.indexing.summary_indexing import SummaryIndexing
from src.summarisation.llm_client import LLMClient
from src.summarisation.prompts import (
    batch_transcript_chunks,
    format_map_prompt,
    format_reduce_prompt,
    format_summary_prompt,
)
from src.summarisation.parser import (
    parse_map_output,
    parse_summary_output,
    generate_fallback_summary,
)

class IngestionPipeline:
    def __init__(self):
        self.audio_extractor = AudioExtractor(settings, AUDIO_DIR)
        self.transcriber = AudioTranscriber(settings, RAW_TRANSCRIPTS)
        self.chroma_manager = ChromaManager(VECTOR_STORE_DIR)
        self.summary_indexing = SummaryIndexing(VECTOR_STORE_DIR)
        self.llm_client = LLMClient()
        
        # Ensure target directories exist
        for directory in [AUDIO_DIR, SUMMARY_DIR, RAW_TRANSCRIPTS, CLEANED_TRANSCRIPTS]:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def run(self, video_path: str | Path, progress_callback=None) -> dict:
        def report(stage, state):
            if progress_callback:
                progress_callback(stage, state)

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found at {video_path}")
        
        video_stem = video_path.stem
        audio_file_path = Path(AUDIO_DIR) / f"{video_stem}.{settings.audio_format}"
        raw_transcript_path = Path(RAW_TRANSCRIPTS) / f"{video_stem}.json"
        cleaned_transcript_path = Path(CLEANED_TRANSCRIPTS) / f"{video_stem}.json"
        summary_file_path = Path(SUMMARY_DIR) / f"{video_stem}.json"
        
        report("audio", "active")
        self.audio_extractor.extract_audio(video_path=video_path)
        report("audio", "done")
        
        report("transcription", "active")
        self.transcriber.audio_transcribe(audio_path=audio_file_path)
        report("transcription", "done")

        report("cleaning", "active")
        clean_transcript(input_path=raw_transcript_path, output_path=cleaned_transcript_path)
        segment_transcript(file_path=cleaned_transcript_path)
        report("cleaning", "done")

        report("indexing", "active")
        self.chroma_manager.index_transcript(
            transcript_path=cleaned_transcript_path,
        )
        report("indexing", "done")

        report("summarization", "active")
        transcript_chunks = []
        if cleaned_transcript_path.exists():
            try:
                with open(cleaned_transcript_path, "r", encoding="utf-8") as f:
                    transcript_chunks = json.load(f)
            except Exception as e:
                print(f"Error reading cleaned transcript: {e}")

        media_title = video_stem.replace("-", " ").replace("_", " ")
        summary = None

        # --- MAP PHASE ---
        batches = batch_transcript_chunks(transcript_chunks, batch_size=50)
        map_results = []
        for index, batch_text in enumerate(batches, start=1):
            try:
                map_prompt = format_map_prompt(batch_text=batch_text, media_title=media_title)
                map_raw_response = self.llm_client.generate_summary(prompt=map_prompt)
                map_output = parse_map_output(map_raw_response)
                if map_output:
                    map_results.append(map_output)
                else:
                    print(f"Map batch {index}/{len(batches)} returned unparseable JSON; skipping batch.")
            except Exception as batch_error:
                print(f"Map batch {index}/{len(batches)} error: {batch_error}")

        # --- REDUCE PHASE ---
        if map_results:
            try:
                aggregated_blocks = []
                for i, res in enumerate(map_results, start=1):
                    block = f"--- Segment {i} ---\nSummary: {res.segment_summary}\nKey Points: {', '.join(res.local_key_points)}"
                    if res.notable_moments:
                        moments_str = "; ".join([f"[{m.timestamp_start}s-{m.timestamp_end}s] {m.label}: {m.description}" for m in res.notable_moments])
                        block += f"\nNotable Moments: {moments_str}"
                    aggregated_blocks.append(block)

                aggregated_text = "\n\n".join(aggregated_blocks)
                reduce_prompt = format_reduce_prompt(aggregated_data=aggregated_text, media_title=media_title)
                reduce_raw_response = self.llm_client.generate_summary(prompt=reduce_prompt)
                summary = parse_summary_output(reduce_raw_response)
            except Exception as reduce_error:
                print(f"Reduce phase generation error: {reduce_error}")

        # Fallback if Map-Reduce fails or yields no valid output
        if summary is None:
            print("Using fallback summarizer for transcript chunks...")
            summary = generate_fallback_summary(
                transcript_chunks=transcript_chunks,
                media_title=media_title,
            )

        summary_file_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_summary_path = summary_file_path.with_suffix(".tmp")
        with open(temporary_summary_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=4, ensure_ascii=False)
        temporary_summary_path.replace(summary_file_path)
        report("summarization", "done")

        report("summary indexing", "active")
        parts = video_stem.split("_")
        anime_name = parts[0] if len(parts) > 0 else ""
        season = parts[1] if len(parts) > 1 else ""
        episode = parts[2] if len(parts) > 2 else ""
        self.summary_indexing.index_summary(summary_path=summary_file_path, anime_name=anime_name, season=season, episode=episode, video_id=video_stem)
        report("summary indexing", "done")
        
        return {
            "status": "success",
            "video_id": video_stem,
            "video_path": str(video_path),
            "summary_path": str(summary_file_path) if summary else None,
            "cleaned_transcript_path": str(cleaned_transcript_path)
        }