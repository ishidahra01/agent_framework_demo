"""
Test script for Agent Framework implementation
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set environment to use Agent Framework
os.environ["USE_AGENT_FRAMEWORK"] = "true"

async def test_agent_framework_basic():
    """Test basic Agent Framework functionality"""
    print("Testing Agent Framework implementation...\n")
    
    try:
        from agents.deep_research.agent import DeepResearchAgent
        
        # Create agent
        print("1. Creating agent...")
        agent = DeepResearchAgent()
        print(f"   ✓ Agent created: {type(agent).__name__}")
        
        # Test planning
        print("\n2. Testing planning...")
        task = "Research the benefits of Python programming"
        plan = await agent.plan(task)
        print(f"   ✓ Plan created with {len(plan.steps)} steps")
        print(f"   Task: {plan.task}")
        print(f"   Status: {plan.status}")
        
        # Test execution (this will be in mock mode without Azure credentials)
        print("\n3. Testing execution...")
        result = await agent.execute(plan)
        print(f"   ✓ Execution completed")
        print(f"   Summary length: {len(result.summary)} characters")
        print(f"   Confidence: {result.confidence_score}")
        
        # Test reflection
        print("\n4. Testing reflection...")
        reflection = await agent.reflect(result)
        print(f"   ✓ Reflection completed")
        print(f"   Quality score: {reflection['quality_score']:.2f}")
        
        # Test report generation
        print("\n5. Testing report generation...")
        report = await agent.report(result, reflection)
        print(f"   ✓ Report generated ({len(report)} characters)")
        
        # Test full cycle
        print("\n6. Testing full research cycle...")
        full_result = await agent.run("What is Microsoft Agent Framework?")
        print(f"   ✓ Full cycle completed")
        print(f"   Status: {full_result['status']}")
        print(f"   Framework: {full_result.get('framework', 'Unknown')}")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_function_tools():
    """Test function tools"""
    print("\n\nTesting Function Tools...\n")
    
    try:
        from agents.tools.functions import get_all_tools
        
        tools = get_all_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            if hasattr(tool, '__name__'):
                print(f"  - {tool.__name__}")
        
        # Test a tool directly
        from agents.tools.functions import web_search
        result = web_search("Python programming")
        print(f"\n✓ web_search tool executed:")
        print(f"  Result length: {len(result)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Tool test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test configuration loading"""
    print("\n\nTesting Configuration Loading...\n")
    
    try:
        import yaml
        config_path = "agents/deep_research/config.yaml"
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"✓ Configuration loaded from {config_path}")
        print(f"  Name: {config.get('name')}")
        print(f"  Roles: {', '.join(config.get('roles', []))}")
        print(f"  Tools: {len(config.get('tools', []))} configured")
        print(f"  Require citations: {config.get('policies', {}).get('require_citations')}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Config test failed: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("="*60)
    print("Agent Framework Implementation Test Suite")
    print("="*60)
    
    results = []
    
    # Test 1: Configuration
    results.append(test_config_loading())
    
    # Test 2: Function tools
    results.append(await test_function_tools())
    
    # Test 3: Agent Framework
    results.append(await test_agent_framework_basic())
    
    # Summary
    print("\n" + "="*60)
    print(f"Test Summary: {sum(results)}/{len(results)} passed")
    print("="*60)
    
    if all(results):
        print("\n✓ All tests passed successfully!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
