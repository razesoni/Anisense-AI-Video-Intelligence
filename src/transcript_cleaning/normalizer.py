import sys
import spacy
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config.settings import SEGMENTED_TRANSCRIPTS, NORMALIZED_TRANSCRIPTS

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


def normalize_transcript(input_path, output_path):
    in_dir = Path(input_path)
    out_dir = Path(output_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    segmented_files = [f for  f in in_dir.iterdir() if f.suffix == ".json"]  
        
    for chunk_file in segmented_files:    
        with open(chunk_file,"r") as f:
            data = json.load(f)
        
        normalized_chunks = []
        for chunk in data:
            chunk_copy = chunk.copy()
            chunk_copy['normalized_text'] = normalize_text(chunk['text'])
            normalized_chunks.append(chunk_copy)

        out_file_path = out_dir / chunk_file.name
        with open(out_file_path,"w") as f:
            json.dump(normalized_chunks,f,indent=4)

        print(f"normalized {chunk_file} completed.")

if __name__ == "__main__":
    normalize_transcript(SEGMENTED_TRANSCRIPTS, NORMALIZED_TRANSCRIPTS)