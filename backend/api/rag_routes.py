from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..models.content import QueryRequest
from ..services.rag_service import rag_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/rag/query")
async def rag_query(request: QueryRequest):
    """
    Execute a RAG (Retrieval Augmented Generation) query
    """
    try:
        result = await rag_pipeline.query(
            query=request.query,
            top_k=request.top_k
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@router.get("/rag/stats")
async def get_rag_stats():
    """
    Get statistics about the RAG pipeline and vector index
    """
    try:
        stats = await rag_pipeline.get_index_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/rag/batch")
async def batch_rag_query(queries: list, top_k: int = 5):
    """
    Execute multiple RAG queries in batch
    """
    try:
        if not isinstance(queries, list):
            raise HTTPException(status_code=400, detail="Queries must be a list")
        
        results = await rag_pipeline.batch_query(queries, top_k)
        return results
    except Exception as e:
        logger.error(f"Error in batch RAG query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch RAG query failed: {str(e)}")