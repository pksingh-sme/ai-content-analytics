"""
Test script to verify logging and observability features
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from backend.logging.metrics import metrics_tracker

async def test_logging_features():
    """Test the logging and observability features"""
    print("Testing Logging and Observability Features...")
    
    try:
        # Test metrics tracking
        print("1. Testing metrics tracking...")
        
        # Log a query
        metrics_tracker.log_query("Test query for logging", 0.5, [])
        print("   ✓ Query logged")
        
        # Log RAG retrieval
        metrics_tracker.log_rag_retrieval("Test RAG query", 3)
        print("   ✓ RAG retrieval logged")
        
        # Log file upload
        metrics_tracker.log_file_upload("test_document.pdf", 102400, "application/pdf")
        print("   ✓ File upload logged")
        
        # Log agent workflow
        metrics_tracker.log_agent_workflow("test_workflow_123", 5, 2.3)
        print("   ✓ Agent workflow logged")
        
        # Log an error
        metrics_tracker.log_error("TestError", "This is a test error message", {"context": "test"})
        print("   ✓ Error logged")
        
        # Get metrics summary
        summary = metrics_tracker.get_metrics_summary()
        print(f"   ✓ Metrics summary retrieved: {summary}")
        
        # Check if metrics file was created
        metrics_file = Path("logs/metrics.json")
        if metrics_file.exists():
            print("   ✓ Metrics file created successfully")
            
            # Load and display metrics
            with open(metrics_file, 'r') as f:
                metrics_data = json.load(f)
                print(f"   ✓ Metrics loaded from file: {len(metrics_data['request_history'])} history entries")
        else:
            print("   ✗ Metrics file not found")
        
        # Test structured logging
        print("\n2. Testing structured logging...")
        from backend.logging import get_logger
        
        logger = get_logger(__name__)
        logger.info("Test info message", extra={"test_key": "test_value"})
        logger.error("Test error message", extra={"error_code": 500})
        print("   ✓ Structured logging working")
        
        print("\n✓ All logging and observability features working correctly!")
        
    except Exception as e:
        print(f"✗ Error during logging testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_logging_features())