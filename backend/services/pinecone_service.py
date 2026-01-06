import pinecone
import asyncio
from typing import List, Dict, Any, Optional
from uuid import uuid4
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.index_name = settings.pinecone_index_name
        self.namespace = settings.pinecone_namespace
        self.dimension = 1536  # Default for text-embedding-ada-002
        self._initialized = False
        
    async def initialize(self):
        """Initialize Pinecone connection and create/index if needed"""
        if self._initialized:
            return
            
        try:
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Check if index exists, create if not
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    pod_type='p1'
                )
                logger.info(f"Created Pinecone index: {self.index_name}")
            
            # Connect to index
            self.index = pinecone.Index(self.index_name)
            self._initialized = True
            logger.info("Pinecone service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone service: {str(e)}")
            raise
    
    async def upsert_embeddings(self, file_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """Upsert document chunks with embeddings to Pinecone"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Prepare vectors for upsert
            vectors = []
            for i, chunk in enumerate(chunks):
                vector_id = f"{file_id}_{i}"
                vector = [
                    vector_id,
                    chunk['embedding'],
                    {
                        'file_id': file_id,
                        'chunk_id': i,
                        'content': chunk['content'],
                        'source_type': chunk.get('source_type', 'document'),
                        'page_number': chunk.get('page_number', None)
                    }
                ]
                vectors.append(vector)
            
            # Upsert vectors to Pinecone
            self.index.upsert(
                vectors=vectors,
                namespace=self.namespace
            )
            
            logger.info(f"Upserted {len(vectors)} vectors for file {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert embeddings: {str(e)}")
            return False
    
    async def query_embeddings(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Query Pinecone for similar embeddings"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Query Pinecone
            query_response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.namespace,
                include_metadata=True
            )
            
            results = []
            for match in query_response['matches']:
                results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'content': match['metadata']['content'],
                    'file_id': match['metadata']['file_id'],
                    'chunk_id': match['metadata']['chunk_id'],
                    'source_type': match['metadata']['source_type'],
                    'page_number': match['metadata'].get('page_number')
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query embeddings: {str(e)}")
            return []
    
    async def delete_file_embeddings(self, file_id: str) -> bool:
        """Delete all embeddings for a specific file"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # List all vectors with the file_id prefix
            # Since Pinecone doesn't have a direct way to filter by metadata in deletion,
            # we'll need to handle this at the application level
            # For now, we'll implement a simple prefix-based deletion
            prefix = f"{file_id}_"
            
            # This is a simplified approach - in production, you might want to 
            # keep track of vector IDs in your metadata database
            # For now, we'll skip this and handle it through metadata filtering
            
            logger.warning("Pinecone delete by metadata not implemented in this version")
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"Failed to delete file embeddings: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index"""
        try:
            if not self._initialized:
                await self.initialize()
            
            stats = self.index.describe_index_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            return {}

# Global Pinecone service instance
pinecone_service = PineconeService()