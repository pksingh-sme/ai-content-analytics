import asyncio
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os
from datetime import datetime

from ..models.content import SearchResult
from ..config import settings
from ..utils.database import save_embedding, get_embedding, search_embeddings


# Initialize the sentence transformer model
model = SentenceTransformer(settings.embedding_model)


class EmbeddingService:
    def __init__(self):
        self.model = model
        self.index = None
        self.id_map = {}  # Maps index positions to document IDs
        self.load_index()
    
    def load_index(self):
        """Load the FAISS index if it exists"""
        index_path = "embeddings.index"
        id_map_path = "id_map.pkl"
        
        if os.path.exists(index_path) and os.path.exists(id_map_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(id_map_path, 'rb') as f:
                    self.id_map = pickle.load(f)
            except:
                # If loading fails, create a new index
                self.index = None
                self.id_map = {}
        else:
            self.index = None
            self.id_map = {}
    
    def save_index(self):
        """Save the FAISS index"""
        if self.index is not None:
            faiss.write_index(self.index, "embeddings.index")
            with open("id_map.pkl", 'wb') as f:
                pickle.dump(self.id_map, f)
    
    async def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts)
        return np.array(embeddings).astype('float32')
    
    async def add_to_index(self, file_id: str, texts: List[str]):
        """Add texts to the vector index"""
        embeddings = await self.generate_embeddings(texts)
        
        # Initialize index if it doesn't exist
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        start_idx = len(self.id_map)
        self.index.add(embeddings)
        
        # Update ID map
        for i, text in enumerate(texts):
            self.id_map[start_idx + i] = {
                'file_id': file_id,
                'text': text,
                'added_at': datetime.utcnow().isoformat()
            }
        
        # Save index
        self.save_index()
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts"""
        if self.index is None or self.index.ntotal == 0:
            return []
        
        # Generate embedding for query
        query_embedding = await self.generate_embeddings([query])
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Perform search
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx in self.id_map:  # Valid index
                item = self.id_map[idx]
                results.append({
                    'content': item['text'],
                    'score': float(score),
                    'source': {
                        'file_id': item['file_id'],
                        'added_at': item['added_at']
                    },
                    'chunk_id': str(idx)
                })
        
        return results


# Global embedding service instance
embedding_service = EmbeddingService()


async def generate_embeddings(file_id: str, text: str, chunk_size: int = 512):
    """
    Generate and store embeddings for text content
    """
    # Split text into chunks
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Add chunks to embedding index
    if chunks:
        await embedding_service.add_to_index(file_id, chunks)


async def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Perform semantic search using embeddings
    """
    results = await embedding_service.search(query, top_k)
    
    search_results = []
    for result in results:
        search_results.append(SearchResult(
            content=result['content'],
            score=result['score'],
            source=result['source'],
            chunk_id=result.get('chunk_id')
        ))
    
    return search_results