"""
Simple example: Using Microsoft Agent Framework for research tasks

This example demonstrates how to use the migrated Deep Research Agent
powered by Microsoft Agent Framework.
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


async def simple_research_example():
    """
    Simple example of using the Deep Research Agent
    """
    print("="*60)
    print("Microsoft Agent Framework - Simple Research Example")
    print("="*60)
    print()
    
    # Import the agent
    from agents.deep_research.agent import DeepResearchAgent
    
    # Create the agent
    print("1. Creating Deep Research Agent...")
    agent = DeepResearchAgent()
    print(f"   ✓ Agent created: {type(agent).__name__}")
    print()
    
    # Define research task
    task = """
    Pythonプログラミング言語について以下の観点から調査してください：
    1. 主な特徴と強み
    2. 一般的な使用用途
    3. 他の言語と比較した利点
    
    簡潔にまとめてください。
    """
    
    print("2. Executing research task...")
    print(f"   Task: {task.strip()[:80]}...")
    print()
    
    # Run the research
    result = await agent.run(task)
    
    print("3. Research completed!")
    print()
    print("="*60)
    print("RESEARCH REPORT")
    print("="*60)
    print()
    print(result["report"])
    print()
    
    # Display metadata
    print("="*60)
    print("METADATA")
    print("="*60)
    print(f"Status: {result['status']}")
    print(f"Framework: {result.get('framework', 'Legacy')}")
    if 'result' in result:
        print(f"Confidence Score: {result['result'].confidence_score:.2f}")
    if 'reflection' in result:
        print(f"Quality Score: {result['reflection']['quality_score']:.2f}")
    print()


async def multi_step_research_example():
    """
    Example showing the research process step by step
    """
    print("="*60)
    print("Multi-Step Research Process Example")
    print("="*60)
    print()
    
    from agents.deep_research.agent import DeepResearchAgent
    
    agent = DeepResearchAgent()
    
    task = "Microsoft Agent Framework の主な機能について説明してください。"
    
    # Step 1: Planning
    print("Step 1: Planning")
    plan = await agent.plan(task)
    print(f"  Task: {plan.task}")
    print(f"  Steps: {len(plan.steps)}")
    for step in plan.steps:
        print(f"    - {step['description']}")
    print()
    
    # Step 2: Execution
    print("Step 2: Execution")
    result = await agent.execute(plan)
    print(f"  Summary length: {len(result.summary)} characters")
    print(f"  Findings: {len(result.findings)}")
    print()
    
    # Step 3: Reflection
    print("Step 3: Reflection")
    reflection = await agent.reflect(result)
    print(f"  Quality Score: {reflection['quality_score']:.2f}")
    print(f"  Citation Coverage: {reflection['citation_coverage']:.2f}")
    if reflection.get('issues'):
        print(f"  Issues: {', '.join(reflection['issues'])}")
    print()
    
    # Step 4: Report Generation
    print("Step 4: Report Generation")
    report = await agent.report(result, reflection)
    print(f"  Report length: {len(report)} characters")
    print()
    
    print("="*60)
    print("FINAL REPORT")
    print("="*60)
    print()
    print(report)
    print()


async def main():
    """Run all examples"""
    # Check environment
    use_agent_framework = os.getenv("USE_AGENT_FRAMEWORK", "true").lower() in ("true", "1", "yes")
    
    print(f"\nImplementation Mode: {'Agent Framework' if use_agent_framework else 'Legacy'}")
    print(f"Azure Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not configured')}")
    print()
    
    if not use_agent_framework:
        print("Note: Running in legacy mode. Set USE_AGENT_FRAMEWORK=true to use Agent Framework.")
        print()
    
    try:
        # Run simple example
        await simple_research_example()
        
        print("\n" + "="*60 + "\n")
        
        # Run multi-step example
        await multi_step_research_example()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
