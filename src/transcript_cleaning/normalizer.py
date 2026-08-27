import spacy
from pathlib import Path
import json

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])



def normalize_text(text: str) -> str:
    doc = nlp(text)
    normalized_tokens = []

    for token in doc:
        if token.is_punct or token.is_space or token.is_currency or token.is_quote:
            continue

        if token.is_stop:
            continue

        normalized_tokens.append(token.lemma_.lower())

    return " ".join(normalized_tokens)


def normalize_transcript(input_path):
    input_path = Path(input_path)
    segmented_files = [input_path] if input_path.is_file() else [
        path for path in input_path.iterdir() if path.suffix == ".json"
    ]
        
    for chunk_file in segmented_files: 
        with open(chunk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        normalized_chunks = []
        for chunk in data:
            chunk_copy = chunk.copy()
            chunk_copy['normalized_text'] = normalize_text(chunk['text'])
            normalized_chunks.append(chunk_copy)

        with open(chunk_file, "w", encoding="utf-8") as f:
            json.dump(normalized_chunks, f, indent=4, ensure_ascii=False)

    