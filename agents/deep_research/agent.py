"""
Deep Research Agent - Main Implementation
Planning, Execution, Reflection, and Reporting cycle
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResearchPlan:
    """Research plan structure"""
    task: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    
@dataclass
class ResearchResult:
    """Research result with citations"""
    summary: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    citations: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeepResearchAgent:
    """
    Main Deep Research Agent implementing:
    - Planning: Break down research tasks
    - Acting: Execute research using tools
    - Reflecting: Verify and validate findings
    - Reporting: Generate reports with citations
    """
    
    def __init__(self, config_path: str = "agents/deep_research/config.yaml"):
        """Initialize agent with configuration"""
        self.config = self._load_config(config_path)
        self.tools = {}
        self.memory = None
        self.policy_manager = None
        
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
            "tools": ["web_search_bing", "rag_corpus"],
            "policies": {
                "domain_allowlist": ["*.gov", "*.ac.jp", "*.co.jp", "*.microsoft.com"],
                "require_citations": True
            }
        }
    
    def register_tool(self, name: str, tool: Any):
        """Register a tool for the agent"""
        self.tools[name] = tool
        logger.info(f"Tool registered: {name}")
    
    def set_memory(self, memory: Any):
        """Set memory provider"""
        self.memory = memory
        
    def set_policy_manager(self, policy_manager: Any):
        """Set policy manager"""
        self.policy_manager = policy_manager
    
    async def plan(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> ResearchPlan:
        """
        Planning phase: Break down the research task into steps
        """
        logger.info(f"Planning research task: {task}")
        
        # Create initial plan
        plan = ResearchPlan(task=task)
        
        # Decompose task into steps
        steps = await self._decompose_task(task, constraints)
        plan.steps = steps
        plan.status = "planned"
        plan.updated_at = datetime.now(timezone.utc)
        
        # Store plan in memory
        if self.memory:
            await self.memory.store_short_term(f"plan_{id(plan)}", plan)
        
        return plan
    
    async def _decompose_task(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Decompose task into actionable steps"""
        # Basic task decomposition logic
        steps = [
            {
                "id": 1,
                "action": "gather_information",
                "description": "Collect relevant information from various sources",
                "tools": ["web_search_bing", "rag_corpus"],
                "status": "pending"
            },
            {
                "id": 2,
                "action": "verify_facts",
                "description": "Cross-reference and verify collected information",
                "tools": ["fact_checker"],
                "status": "pending"
            },
            {
                "id": 3,
                "action": "synthesize",
                "description": "Synthesize findings into coherent results",
                "tools": [],
                "status": "pending"
            },
            {
                "id": 4,
                "action": "generate_report",
                "description": "Generate final report with citations",
                "tools": ["writer"],
                "status": "pending"
            }
        ]
        
        return steps
    
    async def execute(self, plan: ResearchPlan) -> ResearchResult:
        """
        Execution phase: Execute the research plan
        """
        logger.info(f"Executing research plan for task: {plan.task}")
        
        plan.status = "in_progress"
        plan.updated_at = datetime.now(timezone.utc)
        
        findings = []
        citations = []
        
        # Execute each step
        for step in plan.steps:
            logger.info(f"Executing step {step['id']}: {step['action']}")
            
            try:
                # Check policy before execution
                if self.policy_manager:
                    await self.policy_manager.check_permission(step)
                
                # Execute step
                step_result = await self._execute_step(step)
                findings.append(step_result)
                
                # Extract citations
                if "citations" in step_result:
                    citations.extend(step_result["citations"])
                
                step["status"] = "completed"
                
            except Exception as e:
                logger.error(f"Error executing step {step['id']}: {str(e)}")
                step["status"] = "failed"
                step["error"] = str(e)
        
        plan.status = "completed"
        plan.updated_at = datetime.now(timezone.utc)
        
        # Create result
        result = ResearchResult(
            summary=await self._generate_summary(findings),
            findings=findings,
            citations=citations,
            confidence_score=self._calculate_confidence(findings),
            metadata={
                "plan_id": id(plan),
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        return result
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single research step"""
        action = step["action"]
        
        # Simulate step execution
        result = {
            "step_id": step["id"],
            "action": action,
            "status": "completed",
            "data": {},
            "citations": []
        }
        
        # Use tools if available
        for tool_name in step.get("tools", []):
            if tool_name in self.tools:
                tool_result = await self._use_tool(tool_name, step)
                result["data"][tool_name] = tool_result
        
        return result
    
    async def _use_tool(self, tool_name: str, context: Dict[str, Any]) -> Any:
        """Use a registered tool"""
        tool = self.tools.get(tool_name)
        if tool and hasattr(tool, 'execute'):
            return await tool.execute(context)
        return {"status": "tool_not_implemented"}
    
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
        if self.config["policies"].get("require_citations", True):
            if len(result.citations) == 0:
                reflection["issues"].append("No citations found")
                reflection["citation_coverage"] = 0.0
            else:
                reflection["citation_coverage"] = min(len(result.citations) / 3, 1.0)
        
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
        
        return "\n".join(report)
    
    async def _generate_summary(self, findings: List[Dict[str, Any]]) -> str:
        """Generate summary from findings"""
        if not findings:
            return "No findings available"
        
        return f"Research completed with {len(findings)} steps. Results synthesized from multiple sources."
    
    def _calculate_confidence(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for findings"""
        if not findings:
            return 0.0
        
        completed = sum(1 for f in findings if f.get("status") == "completed")
        return completed / len(findings)
    
    async def run(self, task: str, constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Full research cycle: Plan -> Execute -> Reflect -> Report
        """
        logger.info(f"Starting research cycle for task: {task}")
        
        # Planning
        plan = await self.plan(task, constraints)
        
        # Execution
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
            "status": "completed"
        }
