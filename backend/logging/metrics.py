import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path
import logging

from . import get_logger

logger = get_logger(__name__)

class MetricsTracker:
    """Service to track and store application metrics"""
    
    def __init__(self):
        self.metrics_file = Path("logs/metrics.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        
        # Initialize metrics storage
        self.metrics = {
            'queries_processed': 0,
            'total_response_time': 0.0,
            'query_count': 0,
            'rag_retrieval_count': 0,
            'file_upload_count': 0,
            'agent_workflow_count': 0,
            'error_count': 0,
            'request_history': []
        }
        
        # Load existing metrics if file exists
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    self.metrics = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load metrics file: {e}")
    
    def log_query(self, query: str, response_time: float, sources: List[Dict[str, Any]] = None):
        """Log a query with its response time"""
        self.metrics['queries_processed'] += 1
        self.metrics['total_response_time'] += response_time
        self.metrics['query_count'] += 1
        
        # Add to request history (keep last 100 entries)
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'query',
            'query': query[:100] + '...' if len(query) > 100 else query,  # Truncate long queries
            'response_time': response_time
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_rag_retrieval(self, query: str, results_count: int):
        """Log a RAG retrieval operation"""
        self.metrics['rag_retrieval_count'] += 1
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'rag_retrieval',
            'query': query[:100] + '...' if len(query) > 100 else query,
            'results_count': results_count
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_file_upload(self, filename: str, file_size: int, content_type: str):
        """Log a file upload operation"""
        self.metrics['file_upload_count'] += 1
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'file_upload',
            'filename': filename,
            'file_size': file_size,
            'content_type': content_type
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_agent_workflow(self, workflow_id: str, steps_completed: int, execution_time: float):
        """Log an agent workflow execution"""
        self.metrics['agent_workflow_count'] += 1
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'agent_workflow',
            'workflow_id': workflow_id,
            'steps_completed': steps_completed,
            'execution_time': execution_time
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log an error or exception"""
        self.metrics['error_count'] += 1
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': error_message[:200] + '...' if len(error_message) > 200 else error_message,
            'context': context
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def get_average_response_time(self) -> float:
        """Get the average response time for queries"""
        if self.metrics['query_count'] == 0:
            return 0.0
        return self.metrics['total_response_time'] / self.metrics['query_count']
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics"""
        avg_response_time = self.get_average_response_time()
        
        return {
            'queries_processed': self.metrics['queries_processed'],
            'average_response_time': avg_response_time,
            'rag_retrieval_count': self.metrics['rag_retrieval_count'],
            'file_upload_count': self.metrics['file_upload_count'],
            'agent_workflow_count': self.metrics['agent_workflow_count'],
            'error_count': self.metrics['error_count'],
            'total_requests': sum([
                self.metrics['query_count'],
                self.metrics['rag_retrieval_count'],
                self.metrics['file_upload_count'],
                self.metrics['agent_workflow_count']
            ])
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save metrics file: {e}")

# Global metrics tracker instance
metrics_tracker = MetricsTracker()