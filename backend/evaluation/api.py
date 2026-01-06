from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..models.content import QueryRequest
from .evaluation_service import evaluation_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/evaluation/rag")
async def evaluate_rag_pipeline(request: QueryRequest):
    """
    Evaluate the full RAG pipeline and return metrics
    """
    try:
        result = await evaluation_service.evaluate_full_rag_pipeline(
            query=request.query,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        logger.error(f"Error in RAG evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG evaluation failed: {str(e)}")

@router.post("/evaluation/rag-relevance")
async def evaluate_rag_relevance(
    query: str,
    retrieved_docs: list,
    top_k: int = 5
):
    """
    Evaluate RAG retrieval relevance metrics
    """
    try:
        metrics = await evaluation_service.evaluate_rag_relevance(query, retrieved_docs, top_k)
        return metrics
    except Exception as e:
        logger.error(f"Error in RAG relevance evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG relevance evaluation failed: {str(e)}")

@router.post("/evaluation/hallucination")
async def detect_hallucination(
    response: str,
    retrieved_docs: list
):
    """
    Detect hallucinations in LLM response
    """
    try:
        metrics = await evaluation_service.detect_hallucination(response, retrieved_docs)
        return metrics
    except Exception as e:
        logger.error(f"Error in hallucination detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hallucination detection failed: {str(e)}")

@router.get("/evaluation/summary")
async def get_evaluation_summary():
    """
    Get summary of all evaluations
    """
    try:
        summary = evaluation_service.get_evaluation_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting evaluation summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting evaluation summary failed: {str(e)}")

@router.get("/evaluation/logs")
async def get_evaluation_logs():
    """
    Get all evaluation logs
    """
    try:
        return {"logs": evaluation_service.metrics_log}
    except Exception as e:
        logger.error(f"Error getting evaluation logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting evaluation logs failed: {str(e)}")