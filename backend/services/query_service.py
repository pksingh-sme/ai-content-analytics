import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import logging

from ..models.content import QueryRequest, QueryResponse, SearchResult
from ..utils.llm_client import get_llm_response
from ..utils.embeddings import semantic_search as vector_search
from ..utils.database import get_content_by_ids
from ..services.pinecone_service import pinecone_service
from ..logging import get_logger
from ..logging.metrics import metrics_tracker

logger = get_logger(__name__)


async def semantic_search_and_answer(
    query: str, 
    top_k: int = 5, 
    include_sources: bool = True
) -> QueryResponse:
    """
    Perform semantic search and generate AI-powered response using RAG pipeline
    """
    start_time = time.time()
    
    logger.info(
        f"Starting semantic search and answer",
        extra={
            "query": query[:100] + "..." if len(query) > 100 else query,
            "top_k": top_k,
            "include_sources": include_sources
        }
    )
    
    try:
        from ..services.rag_service import rag_pipeline
        
        # Execute the RAG pipeline
        result = await rag_pipeline.query(query, top_k)
        
        # Log RAG retrieval
        retrieved_count = len(result.get('retrieved_documents', []))
        metrics_tracker.log_rag_retrieval(query, retrieved_count)
        
        sources = []
        if include_sources and result.get('retrieved_documents'):
            for doc in result['retrieved_documents']:
                sources.append({
                    "content": doc['content'],
                    "score": doc['score'],
                    "source": doc['source'],
                    "page_number": doc['source'].get('page_number')
                })
        
        response_time = time.time() - start_time
        
        # Log the query with response time
        metrics_tracker.log_query(query, response_time, sources)
        
        logger.info(
            f"Semantic search and answer completed",
            extra={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "response_time": response_time,
                "retrieved_count": retrieved_count
            }
        )
        
        return QueryResponse(
            query=query,
            response=result['response'],
            sources=sources if include_sources else None,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        response_time = time.time() - start_time
        
        logger.error(
            f"Semantic search and answer failed: {str(e)}",
            extra={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "response_time": response_time,
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        # Track the error in metrics
        metrics_tracker.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "top_k": top_k,
                "response_time": response_time
            }
        )
        
        raise e


async def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Perform semantic search without generating response
    """
    return await vector_search(query, top_k=top_k)


async def query_with_rag(
    query: str,
    top_k: int = 5,
    llm_model: str = "gpt-4-turbo"
) -> Dict[str, Any]:
    """
    Query with RAG (Retrieval Augmented Generation)
    """
    start_time = time.time()
    
    logger.info(
        f"Starting RAG query",
        extra={
            "query": query[:100] + "..." if len(query) > 100 else query,
            "top_k": top_k,
            "llm_model": llm_model
        }
    )
    
    try:
        from ..services.rag_service import rag_pipeline
        
        # Execute the RAG pipeline
        result = await rag_pipeline.query(query, top_k, model=llm_model)
        
        # Log RAG retrieval
        retrieved_count = len(result.get('retrieved_documents', []))
        metrics_tracker.log_rag_retrieval(query, retrieved_count)
        
        response_time = time.time() - start_time
        
        # Log the query with response time
        metrics_tracker.log_query(query, response_time, result.get('retrieved_documents', []))
        
        logger.info(
            f"RAG query completed",
            extra={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "response_time": response_time,
                "retrieved_count": retrieved_count
            }
        )
        
        return {
            "query": query,
            "response": result['response'],
            "sources": result['retrieved_documents'],
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": result.get('processing_time', response_time)
        }
    except Exception as e:
        response_time = time.time() - start_time
        
        logger.error(
            f"RAG query failed: {str(e)}",
            extra={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "response_time": response_time,
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        # Track the error in metrics
        metrics_tracker.log_error(
            error_type=type(e).__name__,
            error_message=str(e),
            context={
                "query": query[:100] + "..." if len(query) > 100 else query,
                "top_k": top_k,
                "llm_model": llm_model,
                "response_time": response_time
            }
        )
        
        raise e