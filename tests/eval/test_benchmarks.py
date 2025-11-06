"""
Evaluation Suite for Agent Performance
Tests task success rate, citation quality, and cost efficiency
"""
import pytest
import asyncio
from typing import List, Dict, Any
from datetime import datetime


class AgentEvaluator:
    """Evaluates agent performance on benchmark tasks"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    def evaluate_task_success(self, result: Dict[str, Any]) -> float:
        """
        Evaluate if task was successfully completed
        Returns: 0.0 to 1.0
        """
        if result.get("status") != "completed":
            return 0.0
        
        # Check if result has required components
        has_summary = bool(result.get("result", {}).get("summary"))
        has_findings = len(result.get("result", {}).get("findings", [])) > 0
        
        score = 0.0
        if has_summary:
            score += 0.5
        if has_findings:
            score += 0.5
        
        return score
    
    def evaluate_citation_quality(self, result: Dict[str, Any]) -> float:
        """
        Evaluate quality and coverage of citations
        Returns: 0.0 to 1.0
        """
        citations = result.get("result", {}).get("citations", [])
        
        if not citations:
            return 0.0
        
        # Citation count score (up to 5 citations)
        count_score = min(len(citations) / 5.0, 1.0) * 0.5
        
        # Citation completeness score
        complete_citations = sum(
            1 for c in citations
            if c.get("url") and c.get("title")
        )
        completeness_score = (complete_citations / len(citations)) * 0.5
        
        return count_score + completeness_score
    
    def evaluate_cost_efficiency(self, result: Dict[str, Any], 
                                 budget: int = 100000) -> float:
        """
        Evaluate cost efficiency (token usage vs budget)
        Returns: 0.0 to 1.0 (higher is better)
        """
        tokens_used = result.get("result", {}).get("metadata", {}).get("tokens_used", 0)
        
        if tokens_used == 0:
            return 1.0  # No tokens used
        
        if tokens_used > budget:
            return 0.0  # Over budget
        
        # Score based on efficiency (using less is better)
        efficiency = 1.0 - (tokens_used / budget)
        return efficiency
    
    def evaluate_consistency(self, results: List[Dict[str, Any]]) -> float:
        """
        Evaluate consistency across multiple runs of same task
        Returns: 0.0 to 1.0
        """
        if len(results) < 2:
            return 1.0
        
        # Compare key metrics across runs
        success_rates = [self.evaluate_task_success(r) for r in results]
        citation_counts = [len(r.get("result", {}).get("citations", [])) for r in results]
        
        # Calculate variance (lower is better)
        success_variance = max(success_rates) - min(success_rates)
        citation_variance = max(citation_counts) - min(citation_counts) if citation_counts else 0
        
        # Normalize and invert (higher consistency = lower variance)
        consistency_score = 1.0 - (success_variance * 0.5 + 
                                   min(citation_variance / 10.0, 1.0) * 0.5)
        
        return max(0.0, consistency_score)
    
    async def run_benchmark(self, tasks: List[str]) -> Dict[str, Any]:
        """
        Run benchmark evaluation on a set of tasks
        """
        print(f"Running benchmark on {len(tasks)} tasks...")
        
        results = []
        
        for i, task in enumerate(tasks, 1):
            print(f"Task {i}/{len(tasks)}: {task[:50]}...")
            
            # Mock result for demonstration
            result = {
                "task": task,
                "status": "completed",
                "result": {
                    "summary": f"Mock summary for {task}",
                    "findings": [{"data": "mock finding"}],
                    "citations": [
                        {"url": "http://example.com", "title": "Example"}
                    ],
                    "metadata": {"tokens_used": 10000}
                }
            }
            
            # Evaluate
            eval_result = {
                "task": task,
                "success_score": self.evaluate_task_success(result),
                "citation_score": self.evaluate_citation_quality(result),
                "cost_score": self.evaluate_cost_efficiency(result),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            results.append(eval_result)
            self.results.append(eval_result)
        
        # Calculate aggregate scores
        avg_success = sum(r["success_score"] for r in results) / len(results)
        avg_citation = sum(r["citation_score"] for r in results) / len(results)
        avg_cost = sum(r["cost_score"] for r in results) / len(results)
        
        benchmark_result = {
            "total_tasks": len(tasks),
            "avg_success_score": avg_success,
            "avg_citation_score": avg_citation,
            "avg_cost_score": avg_cost,
            "overall_score": (avg_success + avg_citation + avg_cost) / 3,
            "individual_results": results
        }
        
        return benchmark_result


# Benchmark task sets
BENCHMARK_TASKS = {
    "basic": [
        "Find information about Python programming language",
        "Research climate change effects",
        "Analyze stock market trends"
    ],
    "complex": [
        "市場規模を調査し5年間のCAGRを算出",
        "法令改正の影響を分析",
        "競合他社の戦略を比較分析"
    ]
}


@pytest.mark.asyncio
async def test_benchmark_basic():
    """Run basic benchmark evaluation"""
    evaluator = AgentEvaluator()
    result = await evaluator.run_benchmark(BENCHMARK_TASKS["basic"])
    
    assert result["total_tasks"] == len(BENCHMARK_TASKS["basic"])
    assert 0.0 <= result["overall_score"] <= 1.0
    
    print("\n=== Basic Benchmark Results ===")
    print(f"Overall Score: {result['overall_score']:.2f}")
    print(f"Success Score: {result['avg_success_score']:.2f}")
    print(f"Citation Score: {result['avg_citation_score']:.2f}")
    print(f"Cost Score: {result['avg_cost_score']:.2f}")


@pytest.mark.asyncio
async def test_benchmark_complex():
    """Run complex benchmark evaluation"""
    evaluator = AgentEvaluator()
    result = await evaluator.run_benchmark(BENCHMARK_TASKS["complex"])
    
    assert result["total_tasks"] == len(BENCHMARK_TASKS["complex"])
    
    print("\n=== Complex Benchmark Results ===")
    print(f"Overall Score: {result['overall_score']:.2f}")


if __name__ == "__main__":
    # Run benchmarks directly
    async def main():
        evaluator = AgentEvaluator()
        
        print("Running Agent Performance Benchmarks\n")
        
        basic_result = await evaluator.run_benchmark(BENCHMARK_TASKS["basic"])
        print("\n=== Basic Tasks Benchmark ===")
        print(f"Overall Score: {basic_result['overall_score']:.2%}")
        print(f"Average Success: {basic_result['avg_success_score']:.2%}")
        print(f"Average Citation Quality: {basic_result['avg_citation_score']:.2%}")
        print(f"Average Cost Efficiency: {basic_result['avg_cost_score']:.2%}")
        
        complex_result = await evaluator.run_benchmark(BENCHMARK_TASKS["complex"])
        print("\n=== Complex Tasks Benchmark ===")
        print(f"Overall Score: {complex_result['overall_score']:.2%}")
        print(f"Average Success: {complex_result['avg_success_score']:.2%}")
        print(f"Average Citation Quality: {complex_result['avg_citation_score']:.2%}")
        print(f"Average Cost Efficiency: {complex_result['avg_cost_score']:.2%}")
    
    asyncio.run(main())
