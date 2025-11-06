"""
Unit tests for Deep Research Agent
"""
import pytest
import asyncio
from agents.deep_research.agent import DeepResearchAgent, ResearchPlan


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent can be initialized"""
    agent = DeepResearchAgent()
    assert agent is not None
    assert agent.config is not None


@pytest.mark.asyncio
async def test_agent_planning():
    """Test agent planning phase"""
    agent = DeepResearchAgent()
    
    task = "Test research task"
    plan = await agent.plan(task)
    
    assert isinstance(plan, ResearchPlan)
    assert plan.task == task
    assert len(plan.steps) > 0
    assert plan.status == "planned"


@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent execution phase"""
    agent = DeepResearchAgent()
    
    # Create a simple plan
    plan = ResearchPlan(task="Test task")
    plan.steps = [
        {
            "id": 1,
            "action": "test_action",
            "description": "Test step",
            "tools": [],
            "status": "pending"
        }
    ]
    
    result = await agent.execute(plan)
    
    assert result is not None
    assert result.summary is not None


@pytest.mark.asyncio
async def test_agent_reflection():
    """Test agent reflection phase"""
    agent = DeepResearchAgent()
    
    from agents.deep_research.agent import ResearchResult
    
    result = ResearchResult(
        summary="Test summary",
        findings=[],
        citations=[],
        confidence_score=0.8
    )
    
    reflection = await agent.reflect(result)
    
    assert "quality_score" in reflection
    assert "completeness" in reflection
    assert "citation_coverage" in reflection


@pytest.mark.asyncio
async def test_agent_full_cycle():
    """Test full research cycle"""
    agent = DeepResearchAgent()
    
    task = "Simple test research task"
    result = await agent.run(task)
    
    assert result["status"] == "completed"
    assert "plan" in result
    assert "result" in result
    assert "reflection" in result
    assert "report" in result
