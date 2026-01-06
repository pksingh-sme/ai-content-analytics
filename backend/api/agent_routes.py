from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

from ..models.content import AgentRequest, AgentResponse
from ..services.agent_orchestrator import agent_orchestrator
from ..services.agent import Agent

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/agent/execute")
async def execute_agent_task(request: AgentRequest):
    """
    Execute a task using the agent orchestrator
    """
    try:
        # For now, we'll use a default agent for all tasks
        # In a more advanced implementation, you could select an agent based on the workflow_type
        agent_id = f"default_agent_{request.workflow_type}"
        
        # If agent doesn't exist, create it
        if agent_id not in agent_orchestrator.agents:
            await agent_orchestrator.create_agent(
                agent_id=agent_id,
                name=f"Default {request.workflow_type.title()} Agent",
                description=f"Default agent for {request.workflow_type} workflows",
                capabilities=["general", request.workflow_type]
            )
        
        # Create a simple task
        task = {
            'task_id': f"task_{len(agent_orchestrator.results)}",
            'query': request.query,
            'type': request.workflow_type or 'general',
            'context': request.context
        }
        
        # Execute the task using the agent
        agent = agent_orchestrator.agents[agent_id]
        result = await agent.execute_task(task)
        
        return result
    except Exception as e:
        logger.error(f"Error executing agent task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent task execution failed: {str(e)}")

@router.post("/agent/workflow/create")
async def create_workflow(
    workflow_id: str,
    steps: List[Dict[str, Any]],
    name: str = None,
    description: str = None
):
    """
    Create a new multi-step workflow
    """
    try:
        from ..services.agent_orchestrator import AgentStep, AgentStepType
        
        # Convert dict steps to AgentStep objects
        agent_steps = []
        for step_data in steps:
            step = AgentStep(
                step_id=step_data['step_id'],
                step_type=AgentStepType(step_data['step_type']),
                description=step_data['description'],
                parameters=step_data.get('parameters', {}),
                dependencies=step_data.get('dependencies', [])
            )
            agent_steps.append(step)
        
        # Register the workflow
        success = await agent_orchestrator.register_workflow(workflow_id, agent_steps)
        
        if success:
            return {
                'workflow_id': workflow_id,
                'status': 'created',
                'step_count': len(agent_steps),
                'timestamp': 'datetime.utcnow().isoformat()'
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create workflow")
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow creation failed: {str(e)}")

@router.post("/agent/workflow/execute")
async def execute_workflow(
    workflow_id: str,
    context: Dict[str, Any],
    max_steps: int = 10
):
    """
    Execute a registered multi-step workflow
    """
    try:
        result = await agent_orchestrator.execute_workflow(
            workflow_id=workflow_id,
            initial_context=context,
            max_steps=max_steps
        )
        return result
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.get("/agent/list")
async def list_agents():
    """
    List all available agents
    """
    try:
        agents_info = []
        for agent_id, agent in agent_orchestrator.agents.items():
            agents_info.append({
                'agent_id': agent.agent_id,
                'name': agent.name,
                'description': agent.description,
                'capabilities': agent.capabilities,
                'status': agent.status,
                'created_at': agent.created_at.isoformat()
            })
        return {'agents': agents_info}
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")

@router.get("/agent/workflows")
async def list_workflows():
    """
    List all registered workflows
    """
    try:
        workflows_info = []
        for workflow_id, steps in agent_orchestrator.workflows.items():
            workflows_info.append({
                'workflow_id': workflow_id,
                'step_count': len(steps),
                'steps': [step.step_id for step in steps]
            })
        return {'workflows': workflows_info}
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")