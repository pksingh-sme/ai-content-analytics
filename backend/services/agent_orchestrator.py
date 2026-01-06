import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import logging
from enum import Enum
import time

from ..logging import get_logger
from ..logging.metrics import metrics_tracker

logger = get_logger(__name__)

from ..config import settings
from ..utils.llm_client import get_llm_response
from ..utils.embeddings import semantic_search
from ..services.pinecone_service import pinecone_service
from ..services.blip2_service import blip2_service

logger = logging.getLogger(__name__)

class AgentStepType(Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    TOOL_EXECUTION = "tool_execution"
    DECISION_MAKING = "decision_making"
    INFORMATION_EXTRACTION = "information_extraction"
    SUMMARIZATION = "summarization"

class AgentStep:
    def __init__(
        self, 
        step_id: str, 
        step_type: AgentStepType, 
        description: str, 
        parameters: Dict[str, Any],
        dependencies: List[str] = None
    ):
        self.step_id = step_id
        self.step_type = step_type
        self.description = description
        self.parameters = parameters
        self.dependencies = dependencies or []
        self.status = "pending"
        self.result = None
        self.error = None
        self.execution_time = None

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, 'Agent'] = {}
        self.workflows: Dict[str, List[AgentStep]] = {}
        self.results: Dict[str, Any] = {}
        
    async def create_agent(
        self, 
        agent_id: str, 
        name: str, 
        description: str, 
        capabilities: List[str]
    ):
        """Create a new agent with specified capabilities"""
        agent = Agent(agent_id, name, description, capabilities)
        self.agents[agent_id] = agent
        return agent
    
    async def register_workflow(
        self, 
        workflow_id: str, 
        steps: List[AgentStep]
    ):
        """Register a multi-step workflow"""
        self.workflows[workflow_id] = steps
        return True
    
    async def execute_workflow(
        self, 
        workflow_id: str, 
        initial_context: Dict[str, Any],
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """Execute a multi-step workflow"""
        start_time = time.time()
        
        if workflow_id not in self.workflows:
            error_msg = f"Workflow {workflow_id} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(
            f"Starting execution of workflow: {workflow_id}",
            extra={
                "workflow_id": workflow_id,
                "initial_context_keys": list(initial_context.keys())
            }
        )
        
        workflow = self.workflows[workflow_id]
        context = initial_context.copy()
        execution_results = []
        
        step_count = 0
        
        for step in workflow[:max_steps]:
            step_start_time = time.time()
            logger.info(f"Executing step: {step.step_id} ({step.step_type.value})")
            
            try:
                # Execute the step
                step_result = await self._execute_step(step, context)
                
                # Update context with step result
                context[step.step_id] = step_result
                execution_results.append({
                    'step_id': step.step_id,
                    'result': step_result,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                step.status = "completed"
                step.result = step_result
                step_count += 1
                
                step_execution_time = time.time() - step_start_time
                logger.info(
                    f"Step {step.step_id} completed",
                    extra={
                        "step_id": step.step_id,
                        "step_type": step.step_type.value,
                        "execution_time": step_execution_time
                    }
                )
                
            except Exception as e:
                step_execution_time = time.time() - step_start_time
                logger.error(f"Error executing step {step.step_id}: {str(e)}")
                step.status = "failed"
                step.error = str(e)
                execution_results.append({
                    'step_id': step.step_id,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Log the error
                logger.error(
                    f"Agent workflow step failed: {str(e)}",
                    extra={
                        "workflow_id": workflow_id,
                        "step_id": step.step_id,
                        "step_type": step.step_type.value,
                        "execution_time": step_execution_time,
                        "error_type": type(e).__name__
                    },
                    exc_info=True
                )
                
                # Track the error in metrics
                metrics_tracker.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={
                        "workflow_id": workflow_id,
                        "step_id": step.step_id,
                        "step_type": step.step_type.value
                    }
                )
                
                # Optionally continue or fail fast based on configuration
                # For now, we'll continue execution
                continue
        
        execution_time = time.time() - start_time
        
        # Log the agent workflow execution
        metrics_tracker.log_agent_workflow(workflow_id, step_count, execution_time)
        
        logger.info(
            f"Workflow {workflow_id} execution completed",
            extra={
                "workflow_id": workflow_id,
                "steps_completed": step_count,
                "execution_time": execution_time,
                "status": "completed"
            }
        )
        
        return {
            'workflow_id': workflow_id,
            'status': 'completed',
            'results': execution_results,
            'final_context': context,
            'timestamp': datetime.utcnow().isoformat(),
            'execution_time': execution_time
        }
    
    async def _execute_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a single step in the workflow"""
        start_time = datetime.utcnow()
        
        try:
            if step.step_type == AgentStepType.RESEARCH:
                result = await self._execute_research_step(step, context)
            elif step.step_type == AgentStepType.ANALYSIS:
                result = await self._execute_analysis_step(step, context)
            elif step.step_type == AgentStepType.SYNTHESIS:
                result = await self._execute_synthesis_step(step, context)
            elif step.step_type == AgentStepType.VALIDATION:
                result = await self._execute_validation_step(step, context)
            elif step.step_type == AgentStepType.TOOL_EXECUTION:
                result = await self._execute_tool_step(step, context)
            elif step.step_type == AgentStepType.DECISION_MAKING:
                result = await self._execute_decision_step(step, context)
            elif step.step_type == AgentStepType.INFORMATION_EXTRACTION:
                result = await self._execute_extraction_step(step, context)
            elif step.step_type == AgentStepType.SUMMARIZATION:
                result = await self._execute_summarization_step(step, context)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            step.execution_time = execution_time
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            step.execution_time = execution_time
            step.error = str(e)
            raise
    
    async def _execute_research_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a research step - typically semantic search"""
        query = step.parameters.get('query', '')
        if not query:
            # Try to construct query from context
            query = context.get('query', context.get('question', ''))
        
        top_k = step.parameters.get('top_k', 5)
        results = await semantic_search(query, top_k)
        
        return {
            'query': query,
            'results': [result.dict() for result in results],
            'count': len(results)
        }
    
    async def _execute_analysis_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute an analysis step - typically LLM analysis of data"""
        data_to_analyze = step.parameters.get('data', context.get('data', ''))
        analysis_prompt = step.parameters.get('prompt', 'Analyze the following data:')
        
        analysis = await get_llm_response(
            query=analysis_prompt,
            context=str(data_to_analyze)
        )
        
        return {
            'analysis': analysis,
            'input_data': str(data_to_analyze)[:500] + '...' if len(str(data_to_analyze)) > 500 else str(data_to_analyze)
        }
    
    async def _execute_synthesis_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a synthesis step - combine multiple pieces of information"""
        synthesis_prompt = step.parameters.get('prompt', 'Synthesize the following information:')
        information_to_synthesize = step.parameters.get('data', context)
        
        synthesis = await get_llm_response(
            query=synthesis_prompt,
            context=str(information_to_synthesize)
        )
        
        return {
            'synthesis': synthesis,
            'input_context': str(information_to_synthesize)[:500] + '...' if len(str(information_to_synthesize)) > 500 else str(information_to_synthesize)
        }
    
    async def _execute_validation_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a validation step - verify accuracy of information"""
        data_to_validate = step.parameters.get('data', context)
        validation_criteria = step.parameters.get('criteria', 'Check for accuracy and relevance')
        
        validation_query = f"Validate the following data based on these criteria: {validation_criteria}\n\nData: {data_to_validate}"
        validation_result = await get_llm_response(
            query=validation_query,
            context=""
        )
        
        return {
            'validation': validation_result,
            'data': str(data_to_validate)[:500] + '...' if len(str(data_to_validate)) > 500 else str(data_to_validate),
            'criteria': validation_criteria
        }
    
    async def _execute_tool_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a tool execution step - call external tools"""
        tool_name = step.parameters.get('tool', '')
        tool_params = step.parameters.get('parameters', {})
        
        if tool_name == 'semantic_search':
            query = tool_params.get('query', context.get('query', ''))
            top_k = tool_params.get('top_k', 5)
            results = await semantic_search(query, top_k)
            return [result.dict() for result in results]
        
        elif tool_name == 'image_caption':
            image_path = tool_params.get('image_path', '')
            if image_path:
                caption = blip2_service.generate_caption(image_path)
                return {'caption': caption, 'image_path': image_path}
        
        elif tool_name == 'image_question':
            image_path = tool_params.get('image_path', '')
            question = tool_params.get('question', '')
            if image_path and question:
                answer = blip2_service.answer_question(image_path, question)
                return {'answer': answer, 'image_path': image_path, 'question': question}
        
        else:
            # For other tools, we'll add them as they're needed
            return {
                'tool': tool_name,
                'parameters': tool_params,
                'status': 'not_implemented'
            }
    
    async def _execute_decision_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a decision-making step"""
        decision_context = step.parameters.get('context', context)
        decision_criteria = step.parameters.get('criteria', 'Make the best decision based on the provided context')
        
        decision_query = f"Make a decision based on the following context and criteria:\nContext: {decision_context}\nCriteria: {decision_criteria}"
        decision = await get_llm_response(
            query=decision_query,
            context=""
        )
        
        return {
            'decision': decision,
            'context': str(decision_context)[:500] + '...' if len(str(decision_context)) > 500 else str(decision_context),
            'criteria': decision_criteria
        }
    
    async def _execute_extraction_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute an information extraction step"""
        text_to_extract_from = step.parameters.get('text', context.get('text', ''))
        extraction_type = step.parameters.get('type', 'entities')
        extraction_prompt = step.parameters.get('prompt', f'Extract {extraction_type} from the following text:')
        
        extraction_query = f"{extraction_prompt}\n\nText: {text_to_extract_from}"
        extracted_info = await get_llm_response(
            query=extraction_query,
            context=""
        )
        
        return {
            'extracted_info': extracted_info,
            'text': str(text_to_extract_from)[:500] + '...' if len(str(text_to_extract_from)) > 500 else str(text_to_extract_from),
            'type': extraction_type
        }
    
    async def _execute_summarization_step(self, step: AgentStep, context: Dict[str, Any]) -> Any:
        """Execute a summarization step"""
        text_to_summarize = step.parameters.get('text', context.get('text', ''))
        summary_length = step.parameters.get('length', 'concise')
        
        summary_prompt = f"Provide a {summary_length} summary of the following text:"
        summary_query = f"{summary_prompt}\n\nText: {text_to_summarize}"
        summary = await get_llm_response(
            query=summary_query,
            context=""
        )
        
        return {
            'summary': summary,
            'original_text': str(text_to_summarize)[:500] + '...' if len(str(text_to_summarize)) > 500 else str(text_to_summarize),
            'length': summary_length
        }

# Global agent orchestrator instance
agent_orchestrator = AgentOrchestrator()