import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .agent_orchestrator import AgentStep, AgentStepType

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, agent_id: str, name: str, description: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.created_at = datetime.utcnow()
        self.status = "active"
        self.task_queue = []
        self.is_running = False
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        task_id = task.get('task_id', f"task_{datetime.utcnow().timestamp()}")
        query = task.get('query', '')
        task_type = task.get('type', 'general')
        
        logger.info(f"Agent {self.name} executing task {task_id}: {query}")
        
        try:
            # Create a simple workflow based on task type
            if task_type == 'research':
                workflow = await self._create_research_workflow(query)
            elif task_type == 'analysis':
                workflow = await self._create_analysis_workflow(query)
            elif task_type == 'summarization':
                workflow = await self._create_summarization_workflow(query)
            else:
                workflow = await self._create_general_workflow(query)
            
            # Execute the workflow
            result = await self._execute_workflow(workflow, {'query': query, 'task_id': task_id})
            
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _create_research_workflow(self, query: str) -> List[AgentStep]:
        """Create a research-focused workflow"""
        steps = [
            AgentStep(
                step_id="research_step_1",
                step_type=AgentStepType.RESEARCH,
                description="Perform semantic search for relevant documents",
                parameters={
                    'query': query,
                    'top_k': 5
                }
            ),
            AgentStep(
                step_id="analysis_step_1",
                step_type=AgentStepType.ANALYSIS,
                description="Analyze the research results",
                parameters={
                    'prompt': 'Analyze the research results and identify key points'
                },
                dependencies=["research_step_1"]
            ),
            AgentStep(
                step_id="synthesis_step_1",
                step_type=AgentStepType.SYNTHESIS,
                description="Synthesize the analyzed information",
                parameters={
                    'prompt': 'Synthesize the analyzed information into a coherent response'
                },
                dependencies=["analysis_step_1"]
            )
        ]
        return steps
    
    async def _create_analysis_workflow(self, query: str) -> List[AgentStep]:
        """Create an analysis-focused workflow"""
        steps = [
            AgentStep(
                step_id="data_collection_step_1",
                step_type=AgentStepType.RESEARCH,
                description="Gather relevant data for analysis",
                parameters={
                    'query': query,
                    'top_k': 7
                }
            ),
            AgentStep(
                step_id="analysis_step_1",
                step_type=AgentStepType.ANALYSIS,
                description="Perform detailed analysis of the collected data",
                parameters={
                    'prompt': f'Perform a detailed analysis of the following data in the context of: {query}'
                },
                dependencies=["data_collection_step_1"]
            ),
            AgentStep(
                step_id="validation_step_1",
                step_type=AgentStepType.VALIDATION,
                description="Validate the analysis results",
                parameters={
                    'criteria': 'Check for logical consistency and accuracy'
                },
                dependencies=["analysis_step_1"]
            ),
            AgentStep(
                step_id="decision_step_1",
                step_type=AgentStepType.DECISION_MAKING,
                description="Make decisions based on the analysis",
                parameters={
                    'criteria': 'Make informed decisions based on the validated analysis'
                },
                dependencies=["validation_step_1"]
            )
        ]
        return steps
    
    async def _create_summarization_workflow(self, query: str) -> List[AgentStep]:
        """Create a summarization-focused workflow"""
        steps = [
            AgentStep(
                step_id="content_retrieval_step_1",
                step_type=AgentStepType.RESEARCH,
                description="Retrieve relevant content for summarization",
                parameters={
                    'query': query,
                    'top_k': 10
                }
            ),
            AgentStep(
                step_id="extraction_step_1",
                step_type=AgentStepType.INFORMATION_EXTRACTION,
                description="Extract key information from the content",
                parameters={
                    'type': 'key_points',
                    'prompt': 'Extract the key points from the following content'
                },
                dependencies=["content_retrieval_step_1"]
            ),
            AgentStep(
                step_id="summarization_step_1",
                step_type=AgentStepType.SUMMARIZATION,
                description="Create a summary of the extracted information",
                parameters={
                    'length': 'concise'
                },
                dependencies=["extraction_step_1"]
            )
        ]
        return steps
    
    async def _create_general_workflow(self, query: str) -> List[AgentStep]:
        """Create a general-purpose workflow"""
        steps = [
            AgentStep(
                step_id="understanding_step_1",
                step_type=AgentStepType.ANALYSIS,
                description="Understand the query and requirements",
                parameters={
                    'prompt': f'Analyze the following query and determine what information is needed: {query}'
                }
            ),
            AgentStep(
                step_id="research_step_1",
                step_type=AgentStepType.RESEARCH,
                description="Research relevant information",
                parameters={
                    'query': query,
                    'top_k': 5
                },
                dependencies=["understanding_step_1"]
            ),
            AgentStep(
                step_id="synthesis_step_1",
                step_type=AgentStepType.SYNTHESIS,
                description="Synthesize the research results",
                parameters={
                    'prompt': 'Synthesize the research results into a comprehensive response'
                },
                dependencies=["research_step_1"]
            )
        ]
        return steps
    
    async def _execute_workflow(self, steps: List[AgentStep], context: Dict[str, Any]) -> Any:
        """Execute a workflow of steps"""
        from .agent_orchestrator import agent_orchestrator
        
        # Register the workflow temporarily
        workflow_id = f"temp_workflow_{datetime.utcnow().timestamp()}"
        await agent_orchestrator.register_workflow(workflow_id, steps)
        
        try:
            # Execute the workflow
            result = await agent_orchestrator.execute_workflow(workflow_id, context)
            return result
        finally:
            # Clean up the temporary workflow
            if workflow_id in agent_orchestrator.workflows:
                del agent_orchestrator.workflows[workflow_id]
    
    async def add_to_queue(self, task: Dict[str, Any]):
        """Add a task to the agent's queue"""
        self.task_queue.append(task)
        if not self.is_running:
            await self.process_queue()
    
    async def process_queue(self):
        """Process tasks in the queue"""
        self.is_running = True
        while self.task_queue:
            task = self.task_queue.pop(0)
            result = await self.execute_task(task)
            # In a real implementation, you might want to handle the result
            # (e.g., send to a callback URL, store in database, etc.)
            logger.info(f"Completed task: {result['task_id']}")
        
        self.is_running = False