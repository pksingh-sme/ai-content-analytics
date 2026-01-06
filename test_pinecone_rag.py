"""
Test script to verify Pinecone integration and RAG pipeline
"""
import asyncio
import os
from backend.services.pinecone_service import pinecone_service
from backend.services.rag_service import rag_pipeline

async def test_pinecone_integration():
    """Test Pinecone integration"""
    print("Testing Pinecone integration...")
    
    try:
        # Initialize Pinecone service
        await pinecone_service.initialize()
        print("✓ Pinecone service initialized successfully")
        
        # Test with a sample embedding
        sample_embedding = [0.1] * 1536  # Sample embedding vector
        sample_chunks = [{
            'content': 'This is a test document for Pinecone integration',
            'embedding': sample_embedding,
            'source_type': 'test',
            'chunk_id': 0
        }]
        
        # Test upsert
        success = await pinecone_service.upsert_embeddings("test_file", sample_chunks)
        if success:
            print("✓ Successfully upserted test embedding to Pinecone")
        else:
            print("✗ Failed to upsert test embedding")
        
        # Test query
        results = await pinecone_service.query_embeddings(sample_embedding, top_k=1)
        print(f"✓ Retrieved {len(results)} results from Pinecone")
        
        # Test RAG pipeline
        print("\nTesting RAG pipeline...")
        result = await rag_pipeline.query("What is this system?", top_k=1)
        print(f"✓ RAG pipeline executed successfully")
        print(f"  Query: {result['query']}")
        print(f"  Response: {result['response'][:100]}...")
        
        # Get index stats
        stats = await rag_pipeline.get_index_stats()
        print(f"✓ Index stats retrieved: {stats}")
        
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pinecone_integration())