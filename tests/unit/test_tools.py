"""
Unit tests for Tools
"""
import pytest
from agents.tools.base import (
    WebSearchTool, RAGTool, BrowserTool, MCPTool, ToolRegistry
)


@pytest.mark.asyncio
async def test_web_search_tool():
    """Test web search tool"""
    tool = WebSearchTool()
    
    result = await tool.execute({"query": "test query"})
    
    assert result.success is True
    assert result.data is not None
    assert len(result.citations) > 0


@pytest.mark.asyncio
async def test_rag_tool():
    """Test RAG tool"""
    tool = RAGTool()
    
    result = await tool.execute({"query": "test query"})
    
    assert result.success is True
    assert result.data is not None


@pytest.mark.asyncio
async def test_browser_tool():
    """Test browser tool"""
    tool = BrowserTool({"allowed_domains": ["*.example.com"]})
    
    result = await tool.execute({"url": "https://www.example.com/page"})
    
    assert result.success is True
    assert result.data is not None


@pytest.mark.asyncio
async def test_browser_tool_domain_restriction():
    """Test browser tool enforces domain restrictions"""
    tool = BrowserTool({"allowed_domains": ["*.example.com"]})
    
    result = await tool.execute({"url": "https://blocked.com/page"})
    
    assert result.success is False
    assert "not in allowlist" in result.error


@pytest.mark.asyncio
async def test_mcp_tool():
    """Test MCP tool"""
    tool = MCPTool()
    
    result = await tool.execute({"action": "test_action", "params": {}})
    
    assert result.success is True


def test_tool_registry():
    """Test tool registry"""
    registry = ToolRegistry.create_default_registry()
    
    assert len(registry.list_tools()) > 0
    assert registry.get("web_search_bing") is not None
    assert registry.get("rag_corpus") is not None
