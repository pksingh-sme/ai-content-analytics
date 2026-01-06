import asyncio
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime

from ..models.content import SearchResult
from ..config import settings
from ..utils.database import save_embedding, get_embedding, search_embeddings
from ..services.pinecone_service import pinecone_service


# Initialize the sentence transformer model
model = SentenceTransformer(settings.embedding_model)


class EmbeddingService:
    def __init__(self):
        self.model = model
        
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts)
        # Convert to list of lists for JSON serialization
        return embeddings.tolist()
    
    async def add_embeddings_to_pinecone(self, file_id: str, texts: List[str]):
        """Add texts and embeddings to Pinecone"""
        # Generate embeddings for texts
        embeddings = await self.generate_embeddings(texts)
        
        # Prepare chunks for Pinecone
        chunks = []
        for i, text in enumerate(texts):
            chunks.append({
                'content': text,
                'embedding': embeddings[i],
                'source_type': 'document',  # This would be dynamic in a full implementation
                'chunk_id': i
            })
        
        # Upsert to Pinecone
        success = await pinecone_service.upsert_embeddings(file_id, chunks)
        return success
    
    async def search_pinecone(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts in Pinecone"""
        # Generate embedding for query
        query_embeddings = await self.generate_embeddings([query])
        query_embedding = query_embeddings[0]  # Get the first (and only) embedding
        
        # Query Pinecone
        results = await pinecone_service.query_embeddings(query_embedding, top_k)
        
        return results


# Global embedding service instance
embedding_service = EmbeddingService()


async def generate_embeddings(file_id: str, text: str, chunk_size: int = 512):
    """
    Generate and store embeddings for text content in Pinecone
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
    
    # Add chunks to Pinecone
    if chunks:
        await embedding_service.add_embeddings_to_pinecone(file_id, chunks)


async def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Perform semantic search using Pinecone embeddings
    """
    results = await embedding_service.search_pinecone(query, top_k)
    
    search_results = []
    for result in results:
        search_results.append(SearchResult(
            content=result['content'],
            score=result['score'],
            source={
                'file_id': result['file_id'],
                'chunk_id': result['chunk_id'],
                'source_type': result['source_type'],
                'page_number': result.get('page_number')
            },
            chunk_id=result.get('chunk_id')
        ))
    
    return search_results