"""
Tool Base Classes and Implementations
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Standard tool result structure"""
    success: bool
    data: Any
    citations: List[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.citations is None:
            self.citations = []
        if self.metadata is None:
            self.metadata = {}


class BaseTool(ABC):
    """Base class for all agent tools"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given context"""
        pass
    
    def validate_input(self, context: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        return True


class WebSearchTool(BaseTool):
    """Web search tool using Bing Search API"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("web_search_bing", config)
        self.api_key = self.config.get("api_key")
        self.endpoint = self.config.get("endpoint", "https://api.bing.microsoft.com/v7.0/search")
    
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute web search"""
        query = context.get("query", "")
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                error="Query is required"
            )
        
        logger.info(f"Executing web search: {query}")
        
        # Mock implementation - in production, call actual Bing API
        results = [
            {
                "title": f"Result for {query}",
                "url": "https://example.com/result1",
                "snippet": f"This is a search result for {query}...",
                "relevance_score": 0.95
            }
        ]
        
        citations = [
            {
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"],
                "accessed_at": "2024-01-01T00:00:00Z"
            }
            for result in results
        ]
        
        return ToolResult(
            success=True,
            data=results,
            citations=citations,
            metadata={"query": query, "result_count": len(results)}
        )


class RAGTool(BaseTool):
    """RAG (Retrieval Augmented Generation) tool using Azure AI Search"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("rag_corpus", config)
        self.search_endpoint = self.config.get("search_endpoint")
        self.index_name = self.config.get("index_name", "knowledge-base")
    
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute RAG search"""
        query = context.get("query", "")
        
        if not query:
            return ToolResult(
                success=False,
                data=None,
                error="Query is required"
            )
        
        logger.info(f"Executing RAG search: {query}")
        
        # Mock implementation - in production, call Azure AI Search
        results = [
            {
                "content": f"Knowledge base content related to {query}",
                "source": "internal_docs",
                "relevance_score": 0.88,
                "metadata": {"doc_id": "doc_123"}
            }
        ]
        
        citations = [
            {
                "title": "Internal Documentation",
                "source": result["source"],
                "content_snippet": result["content"][:200],
                "relevance_score": result["relevance_score"]
            }
            for result in results
        ]
        
        return ToolResult(
            success=True,
            data=results,
            citations=citations,
            metadata={"query": query, "index": self.index_name}
        )


class BrowserTool(BaseTool):
    """Safe browser tool for web scraping"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("browser_safe", config)
        self.allowed_domains = self.config.get("allowed_domains", [])
    
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute safe browsing"""
        url = context.get("url", "")
        
        if not url:
            return ToolResult(
                success=False,
                data=None,
                error="URL is required"
            )
        
        # Check domain allowlist
        if self.allowed_domains:
            import re
            # Extract domain from URL
            domain_match = re.search(r'https?://([^/]+)', url)
            if not domain_match:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Invalid URL format: {url}"
                )
            
            domain = domain_match.group(1)
            
            # Check against allowlist patterns
            allowed = False
            for pattern in self.allowed_domains:
                # Convert wildcard pattern to regex
                # *.example.com should match www.example.com, api.example.com, etc.
                regex_pattern = '^' + pattern.replace('.', r'\.').replace('*', '.*') + '$'
                if re.match(regex_pattern, domain):
                    allowed = True
                    break
            
            if not allowed:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Domain not in allowlist: {url}"
                )
        
        logger.info(f"Browsing URL: {url}")
        
        # Mock implementation - in production, use actual browser automation
        content = f"Page content from {url}"
        
        return ToolResult(
            success=True,
            data={"content": content, "url": url},
            citations=[{
                "url": url,
                "title": "Web Page",
                "accessed_at": "2024-01-01T00:00:00Z"
            }],
            metadata={"url": url, "content_length": len(content)}
        )


class MCPTool(BaseTool):
    """MCP (Model Context Protocol) tool for internal API access"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("mcp_api", config)
        self.api_endpoint = self.config.get("api_endpoint")
        self.auth_token = self.config.get("auth_token")
    
    async def execute(self, context: Dict[str, Any]) -> ToolResult:
        """Execute MCP API call"""
        action = context.get("action", "")
        params = context.get("params", {})
        
        if not action:
            return ToolResult(
                success=False,
                data=None,
                error="Action is required"
            )
        
        logger.info(f"Executing MCP action: {action}")
        
        # Mock implementation - in production, call actual MCP API
        result = {
            "action": action,
            "status": "success",
            "data": params
        }
        
        return ToolResult(
            success=True,
            data=result,
            metadata={"action": action}
        )


class ToolRegistry:
    """Registry for managing agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tools"""
        return list(self.tools.keys())
    
    @classmethod
    def create_default_registry(cls, config: Optional[Dict[str, Any]] = None) -> 'ToolRegistry':
        """Create registry with default tools"""
        registry = cls()
        
        config = config or {}
        
        # Register default tools
        registry.register(WebSearchTool(config.get("web_search", {})))
        registry.register(RAGTool(config.get("rag", {})))
        registry.register(BrowserTool(config.get("browser", {})))
        registry.register(MCPTool(config.get("mcp", {})))
        
        return registry
