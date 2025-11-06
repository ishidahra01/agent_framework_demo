"""
Deep Research Agent - Microsoft Agent Framework Implementation
Migrated to use Microsoft Agent Framework (successor to AutoGen and Semantic Kernel)
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import yaml
import logging
import os

from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential, DefaultAzureCredential
from agents.tools.functions import get_all_tools

logger = logging.getLogger(__name__)


@dataclass
class ResearchPlan:
    """Research plan structure"""
    task: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    
@dataclass
class ResearchResult:
    """Research result with citations"""
    summary: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentFrameworkResearchAgent:
    """
    Deep Research Agent using Microsoft Agent Framework
    
    This implementation uses:
    - ChatAgent with AzureOpenAIChatClient for LLM interactions
    - Function tools for research capabilities
    - Thread-based conversation management
    - Compatible with Azure OpenAI and other AI services
    """
    
    def __init__(self, config_path: str = "agents/deep_research/config.yaml"):
        """Initialize agent with configuration"""
        self.config = self._load_config(config_path)
        self.agent = None
        self._chat_client = None
        self._initialize_agent()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "name": "deep-research",
            "roles": ["researcher", "fact_checker", "writer"],
            "memory": {
                "short_term": "inproc_cache",
                "long_term": {"type": "azure_ai_search"}
            },
            "tools": ["web_search", "rag_search", "browse_url", "analyze_data", "verify_facts"],
            "policies": {
                "domain_allowlist": ["*.gov", "*.ac.jp", "*.co.jp", "*.microsoft.com"],
                "require_citations": True
            }
        }
    
    def _get_credentials(self):
        """Get Azure credentials for authentication"""
        # Try environment variable first for API key
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            return None  # Will use API key directly
        
        # Try Azure CLI credential
        try:
            return AzureCliCredential()
        except Exception as e:
            logger.warning(f"Azure CLI credential failed: {e}, trying DefaultAzureCredential")
            return DefaultAzureCredential()
    
    def _initialize_agent(self):
        """Initialize the Agent Framework ChatAgent"""
        try:
            # Get configuration from environment or config
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            # Create chat client
            if api_key:
                # Use API key authentication
                self._chat_client = AzureOpenAIChatClient(
                    endpoint=endpoint,
                    api_key=api_key,
                    deployment_name=deployment
                )
            else:
                # Use credential-based authentication
                credential = self._get_credentials()
                self._chat_client = AzureOpenAIChatClient(
                    credential=credential,
                    endpoint=endpoint,
                    deployment_name=deployment
                )
            
            # Create instructions based on roles
            instructions = self._build_instructions()
            
            # Get available tools
            tools = get_all_tools()
            
            # Create the agent
            self.agent = self._chat_client.create_agent(
                name=self.config.get("name", "deep-research"),
                instructions=instructions,
                tools=tools
            )
            
            logger.info(f"Agent Framework agent initialized: {self.config.get('name')}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Framework agent: {str(e)}")
            # Create a fallback mock agent for development/testing
            self.agent = None
            logger.warning("Running in mock mode - agent will return simulated responses")
    
    def _build_instructions(self) -> str:
        """Build agent instructions from config"""
        roles = self.config.get("roles", ["researcher"])
        policies = self.config.get("policies", {})
        
        instructions = f"""You are a Deep Research Agent with the following roles: {', '.join(roles)}.

Your primary objectives:
1. Conduct thorough research on given topics using available tools
2. Gather information from multiple reliable sources
3. Verify facts and cross-reference information
4. Provide well-structured reports with proper citations
5. Maintain high standards of accuracy and objectivity

Research Guidelines:
- Always use the web_search tool to find current information
- Use rag_search to check internal knowledge bases
- Verify important facts using the verify_facts tool
- Browse specific URLs when needed for detailed information
- Analyze data systematically

"""
        
        if policies.get("require_citations"):
            instructions += "- ALWAYS provide citations and sources for all claims\n"
        
        instructions += """
When generating reports:
- Start with an executive summary
- Present findings in a structured manner
- Include all relevant citations
- Indicate confidence levels for key findings
- Highlight any limitations or uncertainties

Remember: Accuracy and thoroughness are more important than speed.
"""
        
        return instructions
    
    async def plan(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> ResearchPlan:
        """
        Planning phase: Break down the research task into steps
        """
        logger.info(f"Planning research task: {task}")
        
        # Create initial plan
        plan = ResearchPlan(task=task)
        
        # In Agent Framework, planning is done by the LLM itself
        # We just structure the task for the agent
        steps = [
            {
                "id": 1,
                "action": "research",
                "description": f"Research the topic: {task}",
                "status": "pending"
            },
            {
                "id": 2,
                "action": "verify",
                "description": "Verify and cross-reference findings",
                "status": "pending"
            },
            {
                "id": 3,
                "action": "synthesize",
                "description": "Synthesize findings into a coherent report",
                "status": "pending"
            }
        ]
        
        plan.steps = steps
        plan.status = "planned"
        plan.updated_at = datetime.now(timezone.utc)
        
        return plan
    
    async def execute(self, plan: ResearchPlan) -> ResearchResult:
        """
        Execution phase: Execute the research plan using Agent Framework
        """
        logger.info(f"Executing research plan for task: {plan.task}")
        
        plan.status = "in_progress"
        plan.updated_at = datetime.now(timezone.utc)
        
        # Use Agent Framework to execute the research
        if self.agent:
            try:
                # Run the agent with the task
                result = await self.agent.run(plan.task)
                
                # Extract the response text
                response_text = result.text if hasattr(result, 'text') else str(result)
                
                # Create research result
                research_result = ResearchResult(
                    summary=response_text,
                    findings=[{
                        "step_id": 1,
                        "action": "agent_execution",
                        "status": "completed",
                        "data": {"response": response_text}
                    }],
                    citations=[],  # Would extract from response in production
                    confidence_score=0.8,
                    metadata={
                        "plan_id": id(plan),
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "agent_framework_version": "1.0"
                    }
                )
                
                plan.status = "completed"
                plan.updated_at = datetime.now(timezone.utc)
                
                return research_result
                
            except Exception as e:
                logger.error(f"Error executing agent: {str(e)}")
                plan.status = "failed"
                return self._create_error_result(str(e), plan)
        else:
            # Mock execution for development
            logger.warning("Running in mock mode")
            return self._create_mock_result(plan)
    
    def _create_error_result(self, error: str, plan: ResearchPlan) -> ResearchResult:
        """Create error result"""
        return ResearchResult(
            summary=f"Error during execution: {error}",
            findings=[],
            citations=[],
            confidence_score=0.0,
            metadata={
                "error": error,
                "plan_id": id(plan),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _create_mock_result(self, plan: ResearchPlan) -> ResearchResult:
        """Create mock result for development"""
        return ResearchResult(
            summary=f"Mock research completed for: {plan.task}\n\nThis is a simulated response in development mode.",
            findings=[{
                "step_id": 1,
                "action": "mock_research",
                "status": "completed",
                "data": {"mock": True}
            }],
            citations=[],
            confidence_score=0.5,
            metadata={
                "mock": True,
                "plan_id": id(plan),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def reflect(self, result: ResearchResult) -> Dict[str, Any]:
        """
        Reflection phase: Verify and validate the research results
        """
        logger.info("Reflecting on research results")
        
        reflection = {
            "quality_score": 0.0,
            "completeness": 0.0,
            "citation_coverage": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        # Check citation coverage
        if self.config.get("policies", {}).get("require_citations", True):
            if len(result.citations) == 0:
                reflection["issues"].append("No explicit citations found")
                reflection["citation_coverage"] = 0.0
            else:
                reflection["citation_coverage"] = min(len(result.citations) / 3, 1.0)
        else:
            reflection["citation_coverage"] = 1.0
        
        # Calculate quality score
        reflection["quality_score"] = (
            result.confidence_score * 0.5 +
            reflection["citation_coverage"] * 0.3 +
            (1.0 if result.summary else 0.0) * 0.2
        )
        
        # Check completeness
        reflection["completeness"] = 1.0 if result.summary and result.findings else 0.5
        
        return reflection
    
    async def report(self, result: ResearchResult, reflection: Dict[str, Any]) -> str:
        """
        Reporting phase: Generate final report
        """
        logger.info("Generating research report")
        
        report = []
        report.append("# Research Report")
        report.append(f"\n## Summary\n{result.summary}")
        
        if result.findings:
            report.append("\n## Findings")
            for i, finding in enumerate(result.findings, 1):
                report.append(f"\n### Finding {i}")
                report.append(f"- Action: {finding.get('action', 'N/A')}")
                report.append(f"- Status: {finding.get('status', 'N/A')}")
        
        if result.citations:
            report.append("\n## Citations")
            for i, citation in enumerate(result.citations, 1):
                url = citation.get('url', 'N/A')
                title = citation.get('title', 'N/A')
                report.append(f"{i}. [{title}]({url})")
        
        report.append(f"\n## Quality Metrics")
        report.append(f"- Confidence Score: {result.confidence_score:.2f}")
        report.append(f"- Quality Score: {reflection['quality_score']:.2f}")
        report.append(f"- Citation Coverage: {reflection['citation_coverage']:.2f}")
        
        if reflection.get("issues"):
            report.append(f"\n## Notes")
            for issue in reflection["issues"]:
                report.append(f"- {issue}")
        
        return "\n".join(report)
    
    async def run(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Full research cycle: Plan -> Execute -> Reflect -> Report
        Uses Microsoft Agent Framework for intelligent execution
        """
        logger.info(f"Starting research cycle for task: {task}")
        
        # Planning
        plan = await self.plan(task, constraints)
        
        # Execution (using Agent Framework)
        result = await self.execute(plan)
        
        # Reflection
        reflection = await self.reflect(result)
        
        # Reporting
        report = await self.report(result, reflection)
        
        return {
            "task": task,
            "plan": plan,
            "result": result,
            "reflection": reflection,
            "report": report,
            "status": "completed",
            "framework": "Microsoft Agent Framework"
        }


# Backward compatibility: Keep the old class name as alias
DeepResearchAgent = AgentFrameworkResearchAgent
