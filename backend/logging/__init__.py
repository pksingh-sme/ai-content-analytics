import json
import logging
import logging.config
from datetime import datetime
from typing import Dict, Any, Optional
import os
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Set up structured logging configuration"""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Default log file if not provided
    if log_file is None:
        log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': log_level,
                'formatter': 'json',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': log_level,
                'formatter': 'json',
                'class': 'logging.FileHandler',
                'filename': str(log_file),
                'mode': 'a'
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'backend': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'frontend': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(config)
    
    # Set specific log levels for external libraries to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def log_file_upload(file_name: str, file_size: int, content_type: str, user_id: str = None, duration: float = None):
    """Structured logging for file uploads"""
    logger = get_logger('file_upload')
    logger.info(
        f"File uploaded: {file_name}",
        extra={
            'event_type': 'file_upload',
            'file_name': file_name,
            'file_size': file_size,
            'content_type': content_type,
            'user_id': user_id,
            'duration': duration,
            'operation': 'upload'
        }
    )


def log_rag_query(query_text: str, top_k: int, results_count: int, response_time: float, user_id: str = None):
    """Structured logging for RAG queries"""
    logger = get_logger('rag_query')
    logger.info(
        f"RAG query executed: {query_text[:50]}...",
        extra={
            'event_type': 'rag_query',
            'query_text': query_text[:200] + '...' if len(query_text) > 200 else query_text,
            'top_k': top_k,
            'results_count': results_count,
            'response_time': response_time,
            'user_id': user_id,
            'operation': 'query'
        }
    )


def log_agent_workflow(workflow_identifier: str, steps: list, execution_time: float, status: str, user_id: str = None):
    """Structured logging for agent workflows"""
    logger = get_logger('agent_workflow')
    logger.info(
        f"Agent workflow {workflow_identifier} {status}",
        extra={
            'event_type': 'agent_workflow',
            'workflow_identifier': workflow_identifier,
            'steps_count': len(steps),
            'step_ids': [step.get('step_id', 'unknown') for step in steps],
            'execution_time': execution_time,
            'status': status,
            'user_id': user_id,
            'operation': 'workflow'
        }
    )


def log_error(error_category: str, error_description: str, context: dict = None, user_id: str = None):
    """Structured logging for errors and exceptions"""
    logger = get_logger('error')
    logger.error(
        f"Error occurred: {error_category} - {error_description[:100]}...",
        extra={
            'event_type': 'error',
            'error_category': error_category,
            'error_description': error_description[:500] + '...' if len(error_description) > 500 else error_description,
            'context': context or {},
            'user_id': user_id,
            'operation': 'error'
        },
        exc_info=True
    )


def log_api_request(http_method: str, endpoint_url: str, status_code: int, response_time: float, user_id: str = None):
    """Structured logging for API requests"""
    logger = get_logger('api_request')
    logger.info(
        f"API {http_method} {endpoint_url} - {status_code}",
        extra={
            'event_type': 'api_request',
            'http_method': http_method,
            'endpoint_url': endpoint_url,
            'status_code': status_code,
            'response_time': response_time,
            'user_id': user_id,
            'operation': 'api_call'
        }
    )


# Initialize logging
setup_logging()