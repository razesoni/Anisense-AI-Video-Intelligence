import json
import chromadb
from pathlib import Path

class ChromaManager:
    def __init__(self, vector_path):
        self.client = chromadb.PersistentClient(path=str(vector_path))
        self.collection = self.client.get_or_create_collection("video_segments")

    def index_transcript(self, transcript_path: Path):
        transcript_path = Path(transcript_path)
        transcript_dir = transcript_path if transcript_path.is_dir() else transcript_path.parent
        transcript_files = [transcript_path] if transcript_path.is_file() else [
            path for path in transcript_dir.iterdir()
            if path.is_file() and path.name.endswith(".json")
        ]
        
        for transcript_file in transcript_files:
            print(f"Indexing {transcript_file.name}...")
            with open(transcript_file, 'r', encoding='utf-8') as f:
                segments = json.load(f)
                
            documents = []
            ids = []
            metadatas = []

            for i, segment in enumerate(segments):
                documents.append(segment['text'])
                ids.append(segment['video_id'])
                metadatas.append({
                    "video_id": segment['video_id'],
                    "anime_name": segment['anime_name'],
                    "episode_number": segment['episode'],
                    "season": segment['season'],
                    "start_time": segment['start'],
                    "end_time": segment['end'],
                })
                
            if ids:
                self.collection.upsert(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"Successfully indexed {len(segments)} segments from {transcript_file.name}")
                




                        