"""
Test script to verify evaluation and reliability features
"""
import asyncio
from backend.evaluation.evaluation_service import evaluation_service

async def test_evaluation_features():
    """Test the evaluation and reliability features"""
    print("Testing Evaluation and Reliability Features...")
    
    try:
        # Test RAG relevance evaluation
        mock_docs = [
            {'content': 'Artificial intelligence is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.', 'score': 0.9},
            {'content': 'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.', 'score': 0.85},
            {'content': 'Deep learning uses neural networks with multiple layers to model complex patterns in data.', 'score': 0.8}
        ]
        
        rag_metrics = await evaluation_service.evaluate_rag_relevance(
            query="What is artificial intelligence?",
            retrieved_docs=mock_docs,
            top_k=3
        )
        print(f"✓ RAG relevance evaluation completed: {rag_metrics}")
        
        # Test hallucination detection
        response = "Artificial intelligence is a branch of computer science that aims to create software or machines that exhibit human-like intelligence. This field has been developing rapidly since the 1950s."
        hallucination_metrics = await evaluation_service.detect_hallucination(
            response=response,
            retrieved_docs=mock_docs
        )
        print(f"✓ Hallucination detection completed: {hallucination_metrics}")
        
        # Test full RAG pipeline evaluation
        full_result = await evaluation_service.evaluate_full_rag_pipeline(
            query="What are the main applications of artificial intelligence?",
            top_k=3
        )
        print(f"✓ Full RAG pipeline evaluation completed")
        print(f"  Query: {full_result['query'][:50]}...")
        print(f"  Precision: {full_result['rag_metrics']['precision']:.3f}")
        print(f"  F1 Score: {full_result['rag_metrics']['f1_score']:.3f}")
        print(f"  Confidence: {full_result['hallucination_metrics']['confidence']:.3f}")
        
        # Test evaluation logging
        log_id = await evaluation_service.log_evaluation_metrics(
            query="Test query for logging",
            response="Test response for logging",
            retrieved_docs=mock_docs,
            rag_metrics=rag_metrics,
            hallucination_metrics=hallucination_metrics,
            additional_metadata={'test_case': 'evaluation_test'}
        )
        print(f"✓ Evaluation metrics logged with ID: {log_id}")
        
        # Test evaluation summary
        summary = await evaluation_service.get_evaluation_summary()
        print(f"✓ Evaluation summary retrieved: {summary['total_evaluations']} total evaluations")
        
        print("\n✓ All evaluation features working correctly!")
        
    except Exception as e:
        print(f"✗ Error during evaluation testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_evaluation_features())