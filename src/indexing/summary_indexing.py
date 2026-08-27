import json
import chromadb
from pathlib import Path

class SummaryIndexing:
    def __init__(self, vector_path):
        self.client = chromadb.PersistentClient(path=str(vector_path))
        self.summary_collection = self.client.get_or_create_collection("anime_summaries") 
        
    def index_summary(self, summary_path: Path, anime_name: str, season: str, episode: str, video_id: str):
        summary_path = Path(summary_path)
        if not summary_path.exists():
            raise FileNotFoundError(f"Summary path {summary_path} does not exist.")
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
                
            overview = summaries.get('overview', '')
            key_points = summaries.get('key_points', [])
            tags = summaries.get('tags', [])
            key_moments = summaries.get('key_moments', [])

            document_text = (
                f"Anime: {anime_name} Season: {season} Episode: {episode}\n"
                f"Overview: {overview}\n"
                f"Key points: {', '.join(key_points)}\n"
                f"Tags: {', '.join(tags)}\n"
            )
            
            metadata = {
                "anime_name": str(anime_name),
                "season": str(season),
                "episode": str(episode),
                "tags": json.dumps(tags),
                "key_moments": json.dumps(key_moments)
            }
            
            self.summary_collection.upsert(
                ids=[str(video_id)],
                documents=[document_text],
                metadatas=[metadata]
            )