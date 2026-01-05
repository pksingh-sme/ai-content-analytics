import asyncio
from typing import Dict, Any, List
from datetime import datetime

from ..models.content import AgentRequest, AgentResponse
from ..services.query_service import semantic_search_and_answer
from ..utils.llm_client import get_llm_response


async def execute_agent_workflow(
    query: str,
    workflow_type: str = "default",
    context: Dict[str, Any] = {}
) -> AgentResponse:
    """
    Execute multi-step AI workflow based on the requested workflow type
    """
    steps = []
    
    try:
        if workflow_type == "research":
            # Multi-step research workflow
            steps = await _execute_research_workflow(query, context)
        elif workflow_type == "analysis":
            # Analytical workflow
            steps = await _execute_analysis_workflow(query, context)
        elif workflow_type == "summarization":
            # Summarization workflow
            steps = await _execute_summarization_workflow(query, context)
        else:
            # Default workflow
            steps = await _execute_default_workflow(query, context)
        
        # Generate final response based on all steps
        step_summaries = [step.get("summary", "") for step in steps if step.get("summary")]
        context_summary = "\n\n".join(step_summaries)
        
        final_response = await get_llm_response(
            query=query,
            context=context_summary
        )
        
        return AgentResponse(
            query=query,
            steps=steps,
            final_response=final_response,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        # Add error step
        error_step = {
            "step": "error",
            "description": f"Workflow execution failed: {str(e)}",
            "status": "failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        steps.append(error_step)
        
        return AgentResponse(
            query=query,
            steps=steps,
            final_response=f"Workflow failed: {str(e)}",
            timestamp=datetime.utcnow()
        )


async def _execute_default_workflow(query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Default workflow: simple query -> search -> response
    """
    steps = []
    
    # Step 1: Semantic search
    search_result = await semantic_search_and_answer(query, top_k=5)
    steps.append({
        "step": 1,
        "description": "Performed semantic search",
        "action": "semantic_search",
        "query": query,
        "results_count": len(search_result.sources) if search_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Found {len(search_result.sources) if search_result.sources else 0} relevant sources"
    })
    
    return steps


async def _execute_research_workflow(query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Research workflow: multi-step research process
    """
    steps = []
    
    # Step 1: Initial search
    initial_search = await semantic_search_and_answer(query, top_k=5)
    steps.append({
        "step": 1,
        "description": "Initial research query",
        "action": "initial_search",
        "query": query,
        "results_count": len(initial_search.sources) if initial_search.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Initial search found {len(initial_search.sources) if initial_search.sources else 0} sources"
    })
    
    # Step 2: Follow-up questions based on initial results
    follow_up_query = f"Based on these results, what are the key themes and insights related to {query}?"
    follow_up_result = await semantic_search_and_answer(follow_up_query, top_k=3)
    steps.append({
        "step": 2,
        "description": "Follow-up research for key themes",
        "action": "follow_up_search",
        "query": follow_up_query,
        "results_count": len(follow_up_result.sources) if follow_up_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Follow-up search identified key themes from {len(follow_up_result.sources) if follow_up_result.sources else 0} additional sources"
    })
    
    # Step 3: Synthesis
    synthesis_query = f"Synthesize the findings from previous steps about {query} into a comprehensive analysis"
    synthesis_result = await semantic_search_and_answer(synthesis_query, top_k=3)
    steps.append({
        "step": 3,
        "description": "Synthesize findings",
        "action": "synthesis",
        "query": synthesis_query,
        "results_count": len(synthesis_result.sources) if synthesis_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": "Synthesized findings into comprehensive analysis"
    })
    
    return steps


async def _execute_analysis_workflow(query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analysis workflow: structured analytical process
    """
    steps = []
    
    # Step 1: Data gathering
    gathering_query = f"Find all relevant information about {query}"
    gathering_result = await semantic_search_and_answer(gathering_query, top_k=7)
    steps.append({
        "step": 1,
        "description": "Gather relevant data",
        "action": "data_gathering",
        "query": gathering_query,
        "results_count": len(gathering_result.sources) if gathering_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Gathered data from {len(gathering_result.sources) if gathering_result.sources else 0} sources"
    })
    
    # Step 2: Analysis
    analysis_query = f"Analyze the gathered information about {query}. Identify patterns, trends, and relationships."
    analysis_result = await semantic_search_and_answer(analysis_query, top_k=5)
    steps.append({
        "step": 2,
        "description": "Analyze gathered information",
        "action": "analysis",
        "query": analysis_query,
        "results_count": len(analysis_result.sources) if analysis_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": "Completed analysis identifying patterns and trends"
    })
    
    # Step 3: Conclusion
    conclusion_query = f"Provide a conclusion based on the analysis of {query}"
    conclusion_result = await semantic_search_and_answer(conclusion_query, top_k=3)
    steps.append({
        "step": 3,
        "description": "Draw conclusions",
        "action": "conclusion",
        "query": conclusion_query,
        "results_count": len(conclusion_result.sources) if conclusion_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": "Drew conclusions from the analysis"
    })
    
    return steps


async def _execute_summarization_workflow(query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Summarization workflow: extract and summarize key information
    """
    steps = []
    
    # Step 1: Identify key documents
    search_query = f"Find the most relevant documents about {query}"
    search_result = await semantic_search_and_answer(search_query, top_k=10)
    steps.append({
        "step": 1,
        "description": "Identify key documents",
        "action": "document_identification",
        "query": search_query,
        "results_count": len(search_result.sources) if search_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": f"Identified {len(search_result.sources) if search_result.sources else 0} key documents"
    })
    
    # Step 2: Extract key points
    extract_query = f"Extract the key points from these documents about {query}"
    extract_result = await semantic_search_and_answer(extract_query, top_k=8)
    steps.append({
        "step": 2,
        "description": "Extract key points",
        "action": "key_point_extraction",
        "query": extract_query,
        "results_count": len(extract_result.sources) if extract_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": "Extracted key points from documents"
    })
    
    # Step 3: Generate summary
    summary_query = f"Generate a concise summary of {query} based on the extracted key points"
    summary_result = await semantic_search_and_answer(summary_query, top_k=5)
    steps.append({
        "step": 3,
        "description": "Generate summary",
        "action": "summary_generation",
        "query": summary_query,
        "results_count": len(summary_result.sources) if summary_result.sources else 0,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "summary": "Generated concise summary"
    })
    
    return steps