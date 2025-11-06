"""
Unit tests for Policy Manager
"""
import pytest
from agents.policies.manager import (
    PolicyManager, DomainPolicy, CitationPolicy, RateLimitPolicy
)


def test_domain_policy_allowed():
    """Test domain policy allows valid domains"""
    policy = DomainPolicy(["*.example.com", "*.test.org"])
    
    violation = policy.check("https://www.example.com/page")
    
    assert violation is None


def test_domain_policy_blocked():
    """Test domain policy blocks invalid domains"""
    policy = DomainPolicy(["*.example.com"])
    
    violation = policy.check("https://blocked.com/page")
    
    assert violation is not None
    assert violation.severity == "high"


def test_citation_policy_sufficient():
    """Test citation policy with sufficient citations"""
    policy = CitationPolicy(require_citations=True, min_citations=2)
    
    result = {
        "citations": [
            {"url": "http://example.com/1"},
            {"url": "http://example.com/2"}
        ]
    }
    
    violation = policy.check(result)
    
    assert violation is None


def test_citation_policy_insufficient():
    """Test citation policy with insufficient citations"""
    policy = CitationPolicy(require_citations=True, min_citations=3)
    
    result = {"citations": [{"url": "http://example.com/1"}]}
    
    violation = policy.check(result)
    
    assert violation is not None
    assert "citation" in violation.message.lower()


def test_rate_limit_policy():
    """Test rate limit policy"""
    policy = RateLimitPolicy(requests_per_minute=5)
    
    # First 5 requests should succeed
    for _ in range(5):
        violation = policy.check_request_rate()
        assert violation is None
    
    # 6th request should be rate limited
    violation = policy.check_request_rate()
    assert violation is not None
    assert "rate limit" in violation.message.lower()


@pytest.mark.asyncio
async def test_policy_manager():
    """Test policy manager integration"""
    config = {
        "domain_allowlist": ["*.example.com"],
        "require_citations": True,
        "rate_limit_requests_per_minute": 10
    }
    
    manager = PolicyManager(config)
    
    # Test URL checking
    allowed = await manager.check_url("https://www.example.com/page")
    assert allowed is True
    
    blocked = await manager.check_url("https://blocked.com/page")
    assert blocked is False
    
    # Check violations were recorded
    violations = manager.get_violations()
    assert len(violations) > 0
