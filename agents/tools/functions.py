"""
Agent Framework Function Tools
Implements tools as decorated functions compatible with Microsoft Agent Framework
"""
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
import logging

logger = logging.getLogger(__name__)


@ai_function(
    name="web_search",
    description="Search the web using Bing Search API to find relevant information"
)
def web_search(
    query: Annotated[str, Field(description="The search query to execute")],
) -> str:
    """Search the web for information"""
    logger.info(f"Executing web search: {query}")
    
    # Mock implementation - in production, call actual Bing API
    result = f"Web search results for '{query}':\n"
    result += f"1. Example result 1 about {query}\n"
    result += f"   Source: https://example.com/result1\n"
    result += f"2. Example result 2 about {query}\n"
    result += f"   Source: https://example.com/result2\n"
    
    return result


@ai_function(
    name="rag_search",
    description="Search internal knowledge base using RAG (Retrieval Augmented Generation)"
)
def rag_search(
    query: Annotated[str, Field(description="The search query for internal knowledge base")],
) -> str:
    """Search internal knowledge base using RAG"""
    logger.info(f"Executing RAG search: {query}")
    
    # Mock implementation - in production, call Azure AI Search
    result = f"Knowledge base results for '{query}':\n"
    result += f"- Internal documentation: {query} is covered in section 3.2\n"
    result += f"- Best practices: Follow the guidelines for {query}\n"
    result += f"Source: Internal KB Document ID: KB-{hash(query) % 10000}\n"
    
    return result


@ai_function(
    name="browse_url",
    description="Browse a specific URL safely to extract content"
)
def browse_url(
    url: Annotated[str, Field(description="The URL to browse")],
) -> str:
    """Browse a URL safely to extract content"""
    logger.info(f"Browsing URL: {url}")
    
    # Check if URL is allowed (simplified check)
    allowed_domains = [".gov", ".ac.jp", ".co.jp", ".microsoft.com", ".edu"]
    if not any(domain in url for domain in allowed_domains):
        return f"Error: Domain not in allowlist. URL: {url}"
    
    # Mock implementation - in production, use actual browser automation
    result = f"Content from {url}:\n"
    result += f"Title: Example Page\n"
    result += f"Summary: This page contains information relevant to your query.\n"
    result += f"Key points:\n- Point 1\n- Point 2\n- Point 3\n"
    
    return result


@ai_function(
    name="analyze_data",
    description="Analyze data and provide insights"
)
def analyze_data(
    data_description: Annotated[str, Field(description="Description of the data to analyze")],
) -> str:
    """Analyze data and provide insights"""
    logger.info(f"Analyzing data: {data_description}")
    
    result = f"Analysis of '{data_description}':\n"
    result += f"- Pattern identified: Trending upward\n"
    result += f"- Key insight: Significant growth in the last quarter\n"
    result += f"- Recommendation: Continue current strategy\n"
    
    return result


@ai_function(
    name="verify_facts",
    description="Verify and fact-check information from multiple sources"
)
def verify_facts(
    claim: Annotated[str, Field(description="The claim or fact to verify")],
) -> str:
    """Verify and fact-check information"""
    logger.info(f"Verifying facts: {claim}")
    
    result = f"Fact-checking result for: '{claim}'\n"
    result += f"- Confidence: High\n"
    result += f"- Supporting sources: 3 reliable sources found\n"
    result += f"- Verification status: Confirmed\n"
    result += f"- Notes: Cross-referenced with authoritative sources\n"
    
    return result


# Tool registry for backward compatibility
AGENT_TOOLS = [
    web_search,
    rag_search,
    browse_url,
    analyze_data,
    verify_facts,
]


def get_all_tools():
    """Get all available tools for agent"""
    return AGENT_TOOLS
