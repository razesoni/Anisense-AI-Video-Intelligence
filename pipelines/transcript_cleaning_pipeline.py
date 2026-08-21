import json
from pathlib import Path

from src.transcript_cleaning.cleaner import clean_transcript
from src.transcript_cleaning.segmenter import create_timestamped_chunks
from src.transcript_cleaning.normalizer import normalize_text


RAW_DIR = Path("data/transcripts/raw")
CLEANED_DIR = Path("data/transcripts/cleaned")


def process_file(input_file: Path):

    print("\n" + "=" * 60)
    print(f"Processing: {input_file.name}")
    print("=" * 60)

    # Load
    with open(
        input_file,
        "r",
        encoding="utf-8"
    ) as f:

        raw_transcript = json.load(f)

    # Clean
    cleaned_segments = clean_transcript(
        raw_transcript
    )

    # Chunk
    chunks = create_timestamped_chunks(
        cleaned_segments,
        max_words=120,
        min_words=30,
        overlap_sentences=1
    )

    # Normalize
    for chunk in chunks:

        chunk["text"] = normalize_text(
            chunk["text"]
        )

    # Final structure
    result = {
        "source_file": input_file.name,

        "statistics": {
            "raw_segments": len(raw_transcript),
            "cleaned_segments": len(cleaned_segments),
            "chunks": len(chunks)
        },

        "segments": cleaned_segments,

        "chunks": chunks
    }

    # Output
    CLEANED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        CLEANED_DIR /
        f"{input_file.stem}_cleaned.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Raw segments     : {len(raw_transcript)}")
    print(f"Cleaned segments  : {len(cleaned_segments)}")
    print(f"Final chunks      : {len(chunks)}")
    print(f"Saved to          : {output_file}")


def process_all_transcripts():

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = list(
        RAW_DIR.glob("*.json")
    )

    if not files:
        print("No transcript files found.")
        return

    for file in files:
        process_file(file)


if __name__ == "__main__":
    process_all_transcripts()