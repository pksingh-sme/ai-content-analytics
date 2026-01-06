import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.content import QueryRequest, QueryResponse, SearchResult
from ..utils.llm_client import get_llm_response
from ..utils.embeddings import semantic_search as vector_search
from ..utils.database import get_content_by_ids
from ..services.pinecone_service import pinecone_service


async def semantic_search_and_answer(
    query: str, 
    top_k: int = 5, 
    include_sources: bool = True
) -> QueryResponse:
    """
    Perform semantic search and generate AI-powered response using RAG pipeline
    """
    from ..services.rag_service import rag_pipeline
    
    # Execute the RAG pipeline
    result = await rag_pipeline.query(query, top_k)
    
    sources = []
    if include_sources and result.get('retrieved_documents'):
        for doc in result['retrieved_documents']:
            sources.append({
                "content": doc['content'],
                "score": doc['score'],
                "source": doc['source'],
                "page_number": doc['source'].get('page_number')
            })
    
    return QueryResponse(
        query=query,
        response=result['response'],
        sources=sources if include_sources else None,
        timestamp=datetime.utcnow()
    )


async def semantic_search(query: str, top_k: int = 5) -> List[SearchResult]:
    """
    Perform semantic search without generating response
    """
    return await vector_search(query, top_k=top_k)


async def query_with_rag(
    query: str,
    top_k: int = 5,
    llm_model: str = "gpt-4-turbo"
) -> Dict[str, Any]:
    """
    Query with RAG (Retrieval Augmented Generation)
    """
    from ..services.rag_service import rag_pipeline
    
    # Execute the RAG pipeline
    result = await rag_pipeline.query(query, top_k, model=llm_model)
    
    return {
        "query": query,
        "response": result['response'],
        "sources": result['retrieved_documents'],
        "timestamp": datetime.utcnow().isoformat(),
        "processing_time": result.get('processing_time', 0)
    }