import re
import json
from pathlib import Path
from typing import Dict, List


def split_into_sentences(text: str) -> List[str]:

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def create_timestamped_chunks(
    video_name: str,
    segments: List[Dict],
    max_words: int = 120,
    min_words: int = 30,
    overlap_sentences: int = 1
) -> List[Dict]:

    chunks = []

    video_stem = Path(video_name).stem
    parts = video_stem.split("_")
    anime_name = parts[0] if len(parts) > 0 else ""
    season = parts[1] if len(parts) > 1 else ""
    episode = parts[2] if len(parts) > 2 else ""

    current_sentences = []
    current_start = None
    current_end = None
    current_word_count = 0

    chunk_number = 1

    for segment in segments:

        text = segment["text"]

        sentences = split_into_sentences(text)

        for sentence in sentences:

            sentence_words = len(sentence.split())

            # Start a new chunk
            if current_start is None:
                current_start = segment["start"]

            # Check whether adding this sentence exceeds the limit
            if (
                current_word_count + sentence_words > max_words
                and current_sentences
            ):

                chunk_text = " ".join(current_sentences)

                chunks.append({
                    "chunk_id": f"chunk_{chunk_number:04d}",
                    "video_id": f"{video_stem}_chunk_{chunk_number:04d}",
                    "anime_name": anime_name,
                    "season": season,
                    "episode": episode,
                    "start": current_start,
                    "end": current_end,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split())
                })

                chunk_number += 1

                # Keep a small amount of context
                if overlap_sentences > 0:
                    current_sentences = current_sentences[
                        -overlap_sentences:
                    ]
                else:
                    current_sentences = []

                current_word_count = sum(
                    len(s.split())
                    for s in current_sentences
                )

                current_start = segment["start"]

            current_sentences.append(sentence)

            current_word_count += sentence_words
            current_end = segment["end"]

            # If enough content has accumulated,
            # allow the chunk to close naturally.
            if (
                current_word_count >= min_words
                and sentence.endswith((".", "!", "?"))
            ):
                pass

    # Add final chunk
    if current_sentences:

        chunk_text = " ".join(current_sentences)

        chunks.append({
            "chunk_id": f"chunk_{chunk_number:04d}",
            "video_id": f"{video_stem}_chunk_{chunk_number:04d}",
            "anime_name": anime_name,
            "season": season,
            "episode": episode,
            "start": current_start,
            "end": current_end,
            "text": chunk_text,
            "word_count": len(chunk_text.split())
        })

    return chunks


def segment_transcript(file_path):
    file_path = Path(file_path)
    dir_path = file_path if file_path.is_dir() else file_path.parent
    transcript_files = [file_path] if file_path.is_file() else [
        path for path in dir_path.iterdir() if path.is_file()
    ]

    for transcript_file in transcript_files:
        with open(str(transcript_file), "r", encoding="utf-8") as f:
            transcript = json.load(f)

        segmented_transcript = create_timestamped_chunks(transcript_file.name, transcript)

        file_name_without_ext = transcript_file.stem
        output_path = dir_path / f"{file_name_without_ext}.json"

        with open(str(output_path), "w", encoding="utf-8") as f:
            json.dump(segmented_transcript, f, ensure_ascii=False, indent=2)
    
        
