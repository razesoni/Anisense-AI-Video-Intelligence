from rank_bm25 import BM25Okapi
from typing import List, Dict

class LocalKeywordDB:
    def __init__(self):
        self.documents = []
        self.corpus = []
        self.bm25 = None

    def index_chunks(self, chunks: List[Dict], video_id: str):
        """Indexes normalized chunks into the BM25 corpus."""
        for i, chunk in enumerate(chunks):
            doc_id = chunk.get("video_id", f"{video_id}_chunk_{i}")
            
            # Tokenize the normalized text by splitting on spaces
            tokens = chunk.get("normalized_text", "").split()
            self.corpus.append(tokens)
            
            # Store the metadata needed for frontend display
            self.documents.append({
                "id": doc_id,
                "text": chunk["text"], # Keep natural text for display
                "video_id": video_id,
                "start_time": chunk["start"],
                "end_time": chunk["end"]
            })
            
        # Re-initialize the BM25 model with the updated corpus
        self.bm25 = BM25Okapi(self.corpus)

    def search(self, normalized_query: str, n_results: int = 5) -> List[Dict]:
        """Searches the BM25 index and returns top scoring documents."""
        if not self.bm25:
            return []
        
        query_tokens = normalized_query.split()
        scores = self.bm25.get_scores(query_tokens)
        
        # Pair scores with documents and sort descending
        ranked_docs = sorted(zip(scores, self.documents), key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in ranked_docs[:n_results]:
            if score > 0: # Only return actual matches
                doc_data = doc.copy()
                doc_data["keyword_score"] = score
                results.append(doc_data)
                
        return results