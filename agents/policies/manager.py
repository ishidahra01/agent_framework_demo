"""
Policy and Governance Management
Handles security policies, approval workflows, and rate limiting
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    """Policy violation record"""
    policy_name: str
    severity: str  # low, medium, high, critical
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class DomainPolicy:
    """Domain allowlist policy"""
    
    def __init__(self, allowed_domains: List[str]):
        self.allowed_domains = allowed_domains
    
    def check(self, url: str) -> Optional[PolicyViolation]:
        """Check if URL is in allowed domains"""
        if not self.allowed_domains:
            return None  # No restrictions
        
        # Extract domain from URL
        domain_pattern = r'https?://([^/]+)'
        match = re.search(domain_pattern, url)
        
        if not match:
            return PolicyViolation(
                policy_name="domain_allowlist",
                severity="high",
                message=f"Invalid URL format: {url}"
            )
        
        domain = match.group(1)
        
        # Check against allowlist
        for allowed in self.allowed_domains:
            pattern = allowed.replace("*", ".*")
            if re.match(pattern, domain):
                return None  # Allowed
        
        return PolicyViolation(
            policy_name="domain_allowlist",
            severity="high",
            message=f"Domain not in allowlist: {domain}",
            context={"url": url, "domain": domain}
        )


class CitationPolicy:
    """Policy requiring citations for research"""
    
    def __init__(self, require_citations: bool = True, min_citations: int = 1):
        self.require_citations = require_citations
        self.min_citations = min_citations
    
    def check(self, result: Any) -> Optional[PolicyViolation]:
        """Check if result has required citations"""
        if not self.require_citations:
            return None
        
        citations = []
        if hasattr(result, 'citations'):
            citations = result.citations or []
        elif isinstance(result, dict):
            citations = result.get('citations', [])
        
        if len(citations) < self.min_citations:
            return PolicyViolation(
                policy_name="citation_requirement",
                severity="medium",
                message=f"Insufficient citations: {len(citations)} < {self.min_citations}",
                context={"citation_count": len(citations)}
            )
        
        return None


class RateLimitPolicy:
    """Rate limiting policy"""
    
    def __init__(self, requests_per_minute: int = 60, tokens_per_minute: int = 150000):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_history: List[datetime] = []
        self.token_history: List[tuple[datetime, int]] = []
    
    def check_request_rate(self) -> Optional[PolicyViolation]:
        """Check if request rate limit is exceeded"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        
        # Clean old entries
        self.request_history = [ts for ts in self.request_history if ts > cutoff]
        
        if len(self.request_history) >= self.requests_per_minute:
            return PolicyViolation(
                policy_name="rate_limit_requests",
                severity="medium",
                message=f"Request rate limit exceeded: {len(self.request_history)}/{self.requests_per_minute} per minute"
            )
        
        # Record this request
        self.request_history.append(now)
        return None
    
    def check_token_rate(self, tokens: int) -> Optional[PolicyViolation]:
        """Check if token rate limit is exceeded"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        
        # Clean old entries
        self.token_history = [(ts, t) for ts, t in self.token_history if ts > cutoff]
        
        total_tokens = sum(t for _, t in self.token_history) + tokens
        
        if total_tokens > self.tokens_per_minute:
            return PolicyViolation(
                policy_name="rate_limit_tokens",
                severity="high",
                message=f"Token rate limit exceeded: {total_tokens}/{self.tokens_per_minute} per minute"
            )
        
        # Record this usage
        self.token_history.append((now, tokens))
        return None


class ApprovalPolicy:
    """Human-in-the-loop approval policy"""
    
    def __init__(self, approval_required_steps: List[str]):
        self.approval_required_steps = approval_required_steps
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
    
    def requires_approval(self, step: Dict[str, Any]) -> bool:
        """Check if step requires approval"""
        action = step.get("action", "")
        return action in self.approval_required_steps
    
    def request_approval(self, step_id: str, context: Dict[str, Any]) -> str:
        """Request approval for a step"""
        approval_id = f"approval_{step_id}_{datetime.now(timezone.utc).timestamp()}"
        
        self.pending_approvals[approval_id] = {
            "step_id": step_id,
            "context": context,
            "status": "pending",
            "requested_at": datetime.now(timezone.utc)
        }
        
        logger.info(f"Approval requested: {approval_id}")
        return approval_id
    
    def approve(self, approval_id: str, approver: str) -> bool:
        """Approve a pending request"""
        if approval_id not in self.pending_approvals:
            return False
        
        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["approver"] = approver
        self.pending_approvals[approval_id]["approved_at"] = datetime.now(timezone.utc)
        
        logger.info(f"Approval granted: {approval_id} by {approver}")
        return True
    
    def reject(self, approval_id: str, approver: str, reason: str) -> bool:
        """Reject a pending request"""
        if approval_id not in self.pending_approvals:
            return False
        
        self.pending_approvals[approval_id]["status"] = "rejected"
        self.pending_approvals[approval_id]["approver"] = approver
        self.pending_approvals[approval_id]["rejected_at"] = datetime.now(timezone.utc)
        self.pending_approvals[approval_id]["reason"] = reason
        
        logger.info(f"Approval rejected: {approval_id} by {approver}")
        return True
    
    def is_approved(self, approval_id: str) -> bool:
        """Check if request is approved"""
        approval = self.pending_approvals.get(approval_id)
        return approval and approval.get("status") == "approved"


class PolicyManager:
    """
    Central policy manager coordinating all policies
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Initialize policies
        self.domain_policy = DomainPolicy(
            allowed_domains=config.get("domain_allowlist", [])
        )
        
        self.citation_policy = CitationPolicy(
            require_citations=config.get("require_citations", True),
            min_citations=config.get("min_citations", 1)
        )
        
        self.rate_limit_policy = RateLimitPolicy(
            requests_per_minute=config.get("rate_limit_requests_per_minute", 60),
            tokens_per_minute=config.get("rate_limit_tokens_per_minute", 150000)
        )
        
        self.approval_policy = ApprovalPolicy(
            approval_required_steps=config.get("human_approval_steps", [])
        )
        
        self.violations: List[PolicyViolation] = []
    
    async def check_permission(self, step: Dict[str, Any]) -> bool:
        """Check if step is allowed by policies"""
        violations = []
        
        # Check rate limits
        rate_violation = self.rate_limit_policy.check_request_rate()
        if rate_violation:
            violations.append(rate_violation)
        
        # Check if approval is required
        if self.approval_policy.requires_approval(step):
            approval_id = self.approval_policy.request_approval(
                step_id=step.get("id", "unknown"),
                context=step
            )
            
            # In a real implementation, this would wait for actual approval
            logger.warning(f"Step requires approval: {approval_id}")
            
            # For now, auto-approve in development
            self.approval_policy.approve(approval_id, "system")
        
        # Record violations
        self.violations.extend(violations)
        
        # Block if there are high/critical severity violations
        critical_violations = [v for v in violations if v.severity in ["high", "critical"]]
        
        if critical_violations:
            for v in critical_violations:
                logger.error(f"Policy violation: {v.message}")
            return False
        
        return True
    
    async def check_url(self, url: str) -> bool:
        """Check if URL is allowed"""
        violation = self.domain_policy.check(url)
        
        if violation:
            self.violations.append(violation)
            logger.warning(f"URL policy violation: {violation.message}")
            return False
        
        return True
    
    async def check_result(self, result: Any) -> bool:
        """Check if result meets policy requirements"""
        violation = self.citation_policy.check(result)
        
        if violation:
            self.violations.append(violation)
            logger.warning(f"Result policy violation: {violation.message}")
            
            # Warning level - don't block
            if violation.severity in ["low", "medium"]:
                return True
            
            return False
        
        return True
    
    def get_violations(self, severity: Optional[str] = None) -> List[PolicyViolation]:
        """Get recorded violations"""
        if severity:
            return [v for v in self.violations if v.severity == severity]
        return self.violations.copy()
    
    def clear_violations(self):
        """Clear violation history"""
        self.violations.clear()
