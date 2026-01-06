"""
Test script to verify multi-step agent orchestrator functionality
"""
import asyncio
from backend.services.agent_orchestrator import agent_orchestrator
from backend.services.agent import Agent

async def test_agent_orchestrator():
    """Test the multi-step agent orchestrator"""
    print("Testing Multi-Step Agent Orchestrator...")
    
    try:
        # Create an agent
        agent = await agent_orchestrator.create_agent(
            agent_id="test_research_agent",
            name="Test Research Agent",
            description="Agent for testing research workflows",
            capabilities=["research", "analysis", "summarization"]
        )
        print("✓ Created test agent")
        
        # Define a simple workflow for research task
        from backend.services.agent_orchestrator import AgentStep, AgentStepType
        
        research_workflow = [
            AgentStep(
                step_id="step_1_research",
                step_type=AgentStepType.RESEARCH,
                description="Search for information about AI trends",
                parameters={
                    'query': 'current trends in artificial intelligence',
                    'top_k': 3
                }
            ),
            AgentStep(
                step_id="step_2_analysis",
                step_type=AgentStepType.ANALYSIS,
                description="Analyze the research results",
                parameters={
                    'prompt': 'Analyze the research results and identify key trends'
                },
                dependencies=["step_1_research"]
            ),
            AgentStep(
                step_id="step_3_synthesis",
                step_type=AgentStepType.SYNTHESIS,
                description="Synthesize findings into summary",
                parameters={
                    'prompt': 'Create a concise summary of the key AI trends'
                },
                dependencies=["step_2_analysis"]
            )
        ]
        
        # Register the workflow
        await agent_orchestrator.register_workflow("research_workflow", research_workflow)
        print("✓ Registered research workflow")
        
        # Execute the workflow
        context = {
            'query': 'What are the current trends in artificial intelligence?'
        }
        
        result = await agent_orchestrator.execute_workflow(
            workflow_id="research_workflow",
            initial_context=context,
            max_steps=5
        )
        
        print(f"✓ Workflow executed successfully")
        print(f"  Status: {result['status']}")
        print(f"  Results count: {len(result['results'])}")
        
        # Test the agent task execution
        task = {
            'task_id': 'test_task_1',
            'query': 'Analyze the impact of AI on healthcare',
            'type': 'analysis',
            'context': {}
        }
        
        agent = agent_orchestrator.agents["test_research_agent"]
        task_result = await agent.execute_task(task)
        print(f"✓ Agent task executed: {task_result['status']}")
        
        # List agents
        agents = agent_orchestrator.agents
        print(f"✓ Total agents: {len(agents)}")
        
        # List workflows
        workflows = agent_orchestrator.workflows
        print(f"✓ Total workflows: {len(workflows)}")
        
        print("\n✓ Multi-Step Agent Orchestrator tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_orchestrator())