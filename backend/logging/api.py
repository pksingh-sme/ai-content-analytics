from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from .metrics import metrics_tracker

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/logging/metrics")
async def get_metrics():
    """
    Get application metrics summary
    """
    try:
        metrics = metrics_tracker.get_metrics_summary()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting metrics failed: {str(e)}")

@router.get("/logging/metrics/history")
async def get_metrics_history():
    """
    Get recent metrics history
    """
    try:
        return {"history": metrics_tracker.metrics['request_history']}
    except Exception as e:
        logger.error(f"Error getting metrics history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting metrics history failed: {str(e)}")

@router.get("/logging/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "timestamp": "datetime.utcnow().isoformat()"}