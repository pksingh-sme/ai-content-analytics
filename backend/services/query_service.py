import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.content import QueryRequest, QueryResponse, SearchResult
from ..utils.llm_client import get_llm_response
from ..utils.embeddings import semantic_search as vector_search
from ..utils.database import get_content_by_ids


async def semantic_search_and_answer(
    query: str, 
    top_k: int = 5, 
    include_sources: bool = True
) -> QueryResponse:
    """
    Perform semantic search and generate AI-powered response
    """
    # Perform vector search to find relevant content
    search_results = await vector_search(query, top_k=top_k)
    
    # Prepare context from search results
    context_texts = []
    sources = []
    
    for result in search_results:
        context_texts.append(result.content)
        if include_sources:
            sources.append({
                "content": result.content,
                "score": result.score,
                "source": result.source,
                "page_number": result.page_number,
                "chunk_id": result.chunk_id
            })
    
    # Combine context for LLM
    context = "\n\n".join(context_texts)
    
    # Generate response using LLM
    llm_response = await get_llm_response(query, context)
    
    return QueryResponse(
        query=query,
        response=llm_response,
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
    # Search for relevant documents
    search_results = await semantic_search(query, top_k)
    
    # Prepare context from search results
    context = "\n\n".join([result.content for result in search_results])
    
    # Generate response with LLM using context
    response = await get_llm_response(
        query=query,
        context=context,
        model=llm_model
    )
    
    return {
        "query": query,
        "response": response,
        "sources": [result.dict() for result in search_results],
        "timestamp": datetime.utcnow().isoformat()
    }