import re
import sys
import json
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config.settings import CLEANED_TRANSCRIPTS, SEGMENTED_TRANSCRIPTS


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
    segments: List[Dict],
    max_words: int = 120,
    min_words: int = 30,
    overlap_sentences: int = 1
) -> List[Dict]:

    chunks = []

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
            "start": current_start,
            "end": current_end,
            "text": chunk_text,
            "word_count": len(chunk_text.split())
        })

    return chunks


def segment_transcript(clean_path, segmented_path):
    cleaned_dir = Path(clean_path)
    segmented_dir = Path(segmented_path)
    segmented_dir.mkdir(parents=True, exist_ok=True)

    cleaned_transcript_files = [f for f in cleaned_dir.iterdir() if f.is_file()]

    for cleaned_transcript_file in cleaned_transcript_files:
        with open(str(cleaned_transcript_file), "r", encoding="utf-8") as f:
            transcript = json.load(f)

        segmented_transcript = create_timestamped_chunks(transcript)

        file_name_without_ext = cleaned_transcript_file.stem
        output_path = segmented_dir / f"{file_name_without_ext}.json"

        with open(str(output_path), "w", encoding="utf-8") as f:
            json.dump(segmented_transcript, f, ensure_ascii=False, indent=2)

        print(f"Saved segmented transcript: {output_path}")


if __name__ == "__main__":
    segment_transcript(CLEANED_TRANSCRIPTS, SEGMENTED_TRANSCRIPTS)
    
        
