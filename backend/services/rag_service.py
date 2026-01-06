import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from ..models.content import SearchResult
from ..utils.llm_client import get_llm_response
from ..utils.embeddings import semantic_search
from ..services.pinecone_service import pinecone_service
from ..config import settings

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.top_k = 5
        self.context_window_size = 2000  # Maximum context size in characters
    
    async def retrieve(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Retrieve relevant documents based on the query"""
        try:
            results = await semantic_search(query, top_k)
            logger.info(f"Retrieved {len(results)} results for query: {query[:50]}...")
            return results
        except Exception as e:
            logger.error(f"Error in retrieval: {str(e)}")
            return []
    
    async def augment_context(self, query: str, retrieved_results: List[SearchResult]) -> str:
        """Augment the query with retrieved context"""
        if not retrieved_results:
            return f"Query: {query}\n\nNo relevant documents found."
        
        # Combine retrieved documents into context
        context_parts = [f"Query: {query}", "Relevant Documents:"]
        
        total_chars = 0
        for i, result in enumerate(retrieved_results):
            doc_text = f"\nDocument {i+1}: {result.content}"
            
            # Check if adding this document would exceed context window
            if total_chars + len(doc_text) > self.context_window_size:
                logger.info(f"Context window limit reached. Stopping at {i+1} documents.")
                break
            
            context_parts.append(doc_text)
            total_chars += len(doc_text)
        
        return "\n".join(context_parts)
    
    async def generate_response(self, query: str, context: str, model: str = None) -> str:
        """Generate a response based on the query and context"""
        try:
            if model is None:
                model = settings.default_llm_model
            
            response = await get_llm_response(
                query=query,
                context=context,
                model=model
            )
            return response
        except Exception as e:
            logger.error(f"Error in generation: {str(e)}")
            return f"Sorry, I encountered an error generating a response: {str(e)}"
    
    async def query(self, query: str, top_k: int = 5, model: str = None) -> Dict[str, Any]:
        """Execute the full RAG pipeline"""
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Retrieve relevant documents
            retrieved_results = await self.retrieve(query, top_k)
            
            # Step 2: Augment context with retrieved documents
            context = await self.augment_context(query, retrieved_results)
            
            # Step 3: Generate response based on context
            response = await self.generate_response(query, context, model)
            
            end_time = datetime.utcnow()
            
            return {
                "query": query,
                "response": response,
                "retrieved_documents": [
                    {
                        "content": result.content,
                        "score": result.score,
                        "source": result.source
                    } for result in retrieved_results
                ],
                "context_used": context,
                "processing_time": (end_time - start_time).total_seconds(),
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            return {
                "query": query,
                "response": f"Sorry, an error occurred: {str(e)}",
                "retrieved_documents": [],
                "context_used": "",
                "processing_time": (datetime.utcnow() - start_time).total_seconds(),
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def batch_query(self, queries: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """Execute RAG pipeline for multiple queries"""
        results = []
        for query in queries:
            result = await self.query(query, top_k)
            results.append(result)
        return results
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index"""
        try:
            stats = await pinecone_service.get_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"error": str(e)}

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()