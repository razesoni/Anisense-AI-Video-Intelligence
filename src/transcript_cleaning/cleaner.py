import re
import spacy
import json
from pathlib import Path

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
    
    
    
def clean_transcript(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)
    input_files = [input_path] if input_path.is_file() else [
        file_path for file_path in input_path.iterdir() if file_path.is_file()
    ]
    output_dir = output_path if output_path.suffix == "" else output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_files:
        with open(str(input_file), "r", encoding="utf-8") as f:
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
        cleaned_file = output_path if output_path.suffix else output_dir / input_file.name
        with open(str(cleaned_file), "w", encoding="utf-8") as f:
            json.dump(cleaned_transcript, f, ensure_ascii=False, indent=2)
        print(f"Success: {cleaned_file}")
