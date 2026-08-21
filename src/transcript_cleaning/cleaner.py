import re
import sys
import spacy
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import RAW_TRANSCRIPTS, CLEANED_TRANSCRIPTS

nlp = spacy.load("en_core_web_sm", disable=["ner", "parser", "tagger", "lemmatizer"])

NOISE_PHRASES = [
    "music",
    "the end",
    "background music",
    "instrumentals",
    "outro"
]
    
FILLER_WORDS = [
    "uh",
    "um",
    "huh",
    "hmm",
    "erm",
    "ah"
]

def clean_text(text:str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    cleaned = []
    previous = None
    doc = nlp(text)
    
    for token in doc:
        if token.is_space:
            continue
        current = token.text.lower()

        if current in FILLER_WORDS or current in NOISE_PHRASES:
            continue

        if (previous is not None and current == previous and token.is_alpha):
            continue
    
        previous = current
        cleaned.append(token.text)

    cleaned_text = " ".join(cleaned)
    return cleaned_text
    
    
    
def clean_transcript(raw_path, cleaned_path):
    raw_dir = Path(raw_path)
    cleandir= Path(cleaned_path)
    cleandir.mkdir(parents=True, exist_ok=True)

    raw_transcript_files = [files for files in raw_dir.iterdir() if files.is_file()]

    for raw_transcript_file in raw_transcript_files:
        with open(str(raw_transcript_file), "r", encoding="utf-8") as f:
            transcript = json.load(f)
    
        cleaned_transcript = []
        for seg in transcript:
            seg_start = float(seg['start'])
            seg_end = float(seg['end'])
            cleaned_text = clean_text(seg['text'])

            cleaned_transcript.append({
                "start" : seg_start,
                "end" : seg_end,
                "text" : cleaned_text
            })
        cleaned_file = cleandir / raw_transcript_file.name
        with open(str(cleaned_file), "w", encoding="utf-8") as f:
            json.dump(cleaned_transcript, f, ensure_ascii=False, indent=2)
        print(f"Success: {cleaned_file}")
        

if __name__ == "__main__":
    clean_transcript(RAW_TRANSCRIPTS, CLEANED_TRANSCRIPTS)
