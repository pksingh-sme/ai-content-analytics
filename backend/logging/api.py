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
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/logging/metrics/detailed")
async def get_detailed_metrics():
    """
    Get detailed metrics including percentiles and endpoint breakdown
    """
    try:
        metrics = metrics_tracker.get_metrics_summary()
        return metrics
    except Exception as e:
        logger.error(f"Error getting detailed metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting detailed metrics failed: {str(e)}")


@router.get("/logging/metrics/endpoints")
async def get_endpoint_metrics():
    """
    Get per-endpoint metrics
    """
    try:
        metrics = metrics_tracker.get_metrics_summary()
        return {"endpoint_metrics": metrics.get('endpoint_metrics', {})}
    except Exception as e:
        logger.error(f"Error getting endpoint metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting endpoint metrics failed: {str(e)}")


@router.get("/logging/metrics/errors")
async def get_error_metrics():
    """
    Get error metrics and types
    """
    try:
        metrics = metrics_tracker.get_metrics_summary()
        return {
            "error_count": metrics.get('error_count', 0),
            "error_types": metrics.get('error_types', {}),
            "failed_requests": metrics.get('failed_requests', 0)
        }
    except Exception as e:
        logger.error(f"Error getting error metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting error metrics failed: {str(e)}")


@router.get("/logging/metrics/performance")
async def get_performance_metrics():
    """
    Get performance metrics including response times and throughput
    """
    try:
        metrics = metrics_tracker.get_metrics_summary()
        return {
            "average_response_time": metrics.get('average_response_time', 0),
            "response_time_percentiles": metrics.get('response_time_percentiles', {}),
            "total_processing_time": metrics.get('total_processing_time', 0),
            "success_rate": metrics.get('success_rate', 0),
            "queries_processed": metrics.get('queries_processed', 0)
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Getting performance metrics failed: {str(e)}")


@router.delete("/logging/metrics/reset")
async def reset_metrics():
    """
    Reset all metrics (admin only)
    """
    try:
        # Reset metrics to initial state
        metrics_tracker.metrics = {
            'queries_processed': 0,
            'total_response_time': 0.0,
            'query_count': 0,
            'rag_retrieval_count': 0,
            'file_upload_count': 0,
            'agent_workflow_count': 0,
            'error_count': 0,
            'api_request_count': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'peak_concurrent_users': 0,
            'active_users': set(),
            'request_history': [],
            'response_times': [],
            'error_types': {},
            'endpoint_metrics': {}
        }
        metrics_tracker._save_metrics()
        return {"status": "success", "message": "Metrics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Resetting metrics failed: {str(e)}")