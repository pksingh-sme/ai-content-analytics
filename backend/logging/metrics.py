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
        
        # Initialize metrics storage with enhanced metrics
        self.metrics = {
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
            'response_times': [],  # Store last 1000 response times for percentiles
            'error_types': {},     # Track error type frequencies
            'endpoint_metrics': {} # Track per-endpoint metrics
        }
        
        # Load existing metrics if file exists
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    loaded_metrics = json.load(f)
                    # Merge loaded metrics with defaults
                    self.metrics.update(loaded_metrics)
                    # Ensure active_users is a set
                    if 'active_users' in self.metrics:
                        self.metrics['active_users'] = set(self.metrics['active_users'])
            except Exception as e:
                logger.warning(f"Could not load metrics file: {e}")
    
    def log_query(self, query: str, response_time: float, sources: List[Dict[str, Any]] = None, user_id: str = None):
        """Log a query with its response time"""
        self.metrics['queries_processed'] += 1
        self.metrics['total_response_time'] += response_time
        self.metrics['query_count'] += 1
        
        # Track response times for percentile calculations
        self.metrics['response_times'].append(response_time)
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
        
        # Track active users
        if user_id:
            self.metrics['active_users'].add(user_id)
            self._update_peak_concurrent_users()
        
        # Add to request history (keep last 100 entries)
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'query',
            'query': query[:100] + '...' if len(query) > 100 else query,
            'response_time': response_time,
            'sources_count': len(sources) if sources else 0,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_rag_retrieval(self, query: str, results_count: int, retrieval_time: float = None, user_id: str = None):
        """Log a RAG retrieval operation"""
        self.metrics['rag_retrieval_count'] += 1
        
        # Track retrieval time if provided
        if retrieval_time:
            self.metrics['total_processing_time'] += retrieval_time
        
        # Track active users
        if user_id:
            self.metrics['active_users'].add(user_id)
            self._update_peak_concurrent_users()
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'rag_retrieval',
            'query': query[:100] + '...' if len(query) > 100 else query,
            'results_count': results_count,
            'retrieval_time': retrieval_time,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_file_upload(self, filename: str, file_size: int, content_type: str, upload_time: float = None, user_id: str = None):
        """Log a file upload operation"""
        self.metrics['file_upload_count'] += 1
        
        # Track upload time if provided
        if upload_time:
            self.metrics['total_processing_time'] += upload_time
        
        # Track active users
        if user_id:
            self.metrics['active_users'].add(user_id)
            self._update_peak_concurrent_users()
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'file_upload',
            'filename': filename,
            'file_size': file_size,
            'content_type': content_type,
            'upload_time': upload_time,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_agent_workflow(self, workflow_id: str, steps_completed: int, execution_time: float, status: str = "completed", user_id: str = None):
        """Log an agent workflow execution"""
        self.metrics['agent_workflow_count'] += 1
        
        # Track processing time
        self.metrics['total_processing_time'] += execution_time
        
        # Track active users
        if user_id:
            self.metrics['active_users'].add(user_id)
            self._update_peak_concurrent_users()
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'agent_workflow',
            'workflow_id': workflow_id,
            'steps_completed': steps_completed,
            'execution_time': execution_time,
            'status': status,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None, user_id: str = None):
        """Log an error or exception"""
        self.metrics['error_count'] += 1
        self.metrics['failed_requests'] += 1
        
        # Track error types
        if error_type in self.metrics['error_types']:
            self.metrics['error_types'][error_type] += 1
        else:
            self.metrics['error_types'][error_type] = 1
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': error_message[:200] + '...' if len(error_message) > 200 else error_message,
            'context': context,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, response_time: float, user_id: str = None):
        """Log an API request with detailed metrics"""
        self.metrics['api_request_count'] += 1
        
        # Track success/failure
        if 200 <= status_code < 400:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Track endpoint metrics
        if endpoint not in self.metrics['endpoint_metrics']:
            self.metrics['endpoint_metrics'][endpoint] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_response_time': 0.0,
                'methods': {}
            }
        
        endpoint_metrics = self.metrics['endpoint_metrics'][endpoint]
        endpoint_metrics['total_requests'] += 1
        endpoint_metrics['total_response_time'] += response_time
        
        if 200 <= status_code < 400:
            endpoint_metrics['successful_requests'] += 1
        else:
            endpoint_metrics['failed_requests'] += 1
        
        # Track method-specific metrics
        if method not in endpoint_metrics['methods']:
            endpoint_metrics['methods'][method] = {
                'count': 0,
                'total_response_time': 0.0
            }
        
        method_metrics = endpoint_metrics['methods'][method]
        method_metrics['count'] += 1
        method_metrics['total_response_time'] += response_time
        
        # Track active users
        if user_id:
            self.metrics['active_users'].add(user_id)
            self._update_peak_concurrent_users()
        
        self.metrics['request_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'api_request',
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time': response_time,
            'user_id': user_id
        })
        
        # Keep only last 100 entries
        if len(self.metrics['request_history']) > 100:
            self.metrics['request_history'] = self.metrics['request_history'][-100:]
        
        self._save_metrics()
    
    def _update_peak_concurrent_users(self):
        """Update peak concurrent users count"""
        current_active = len(self.metrics['active_users'])
        if current_active > self.metrics['peak_concurrent_users']:
            self.metrics['peak_concurrent_users'] = current_active
    
    def get_average_response_time(self) -> float:
        """Get the average response time for queries"""
        if self.metrics['query_count'] == 0:
            return 0.0
        return self.metrics['total_response_time'] / self.metrics['query_count']
    
    def get_response_time_percentiles(self) -> Dict[str, float]:
        """Get response time percentiles (50th, 90th, 95th, 99th)"""
        if not self.metrics['response_times']:
            return {'p50': 0.0, 'p90': 0.0, 'p95': 0.0, 'p99': 0.0}
        
        sorted_times = sorted(self.metrics['response_times'])
        n = len(sorted_times)
        
        return {
            'p50': sorted_times[int(n * 0.5)],
            'p90': sorted_times[int(n * 0.9)],
            'p95': sorted_times[int(n * 0.95)],
            'p99': sorted_times[int(n * 0.99)]
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of all metrics"""
        avg_response_time = self.get_average_response_time()
        percentiles = self.get_response_time_percentiles()
        
        # Calculate success rate
        total_requests = self.metrics['api_request_count']
        success_rate = (self.metrics['successful_requests'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate current active users
        active_users_count = len(self.metrics['active_users'])
        
        return {
            'queries_processed': self.metrics['queries_processed'],
            'average_response_time': round(avg_response_time, 3),
            'response_time_percentiles': {
                'p50': round(percentiles['p50'], 3),
                'p90': round(percentiles['p90'], 3),
                'p95': round(percentiles['p95'], 3),
                'p99': round(percentiles['p99'], 3)
            },
            'rag_retrieval_count': self.metrics['rag_retrieval_count'],
            'file_upload_count': self.metrics['file_upload_count'],
            'agent_workflow_count': self.metrics['agent_workflow_count'],
            'error_count': self.metrics['error_count'],
            'api_request_count': self.metrics['api_request_count'],
            'successful_requests': self.metrics['successful_requests'],
            'failed_requests': self.metrics['failed_requests'],
            'success_rate': round(success_rate, 2),
            'active_users': active_users_count,
            'peak_concurrent_users': self.metrics['peak_concurrent_users'],
            'total_processing_time': round(self.metrics['total_processing_time'], 3),
            'error_types': self.metrics['error_types'],
            'endpoint_metrics': self.metrics['endpoint_metrics']
        }
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            # Convert set to list for JSON serialization
            metrics_to_save = self.metrics.copy()
            if 'active_users' in metrics_to_save:
                metrics_to_save['active_users'] = list(metrics_to_save['active_users'])
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_to_save, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save metrics file: {e}")

# Global metrics tracker instance
metrics_tracker = MetricsTracker()