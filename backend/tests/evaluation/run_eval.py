"""
Automated Test Runner for CareConnect Evaluation
Runs test suite and generates evaluation report
"""
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.router import AgentRouter
from app.core.db import async_session_maker, init_db
from app.models import User
from sqlalchemy import select

from test_suite import BASELINE_METRICS, PERFORMANCE_TARGETS, TEST_SUITE


class EvaluationRunner:
    """Run automated evaluation tests."""

    def __init__(self):
        """Initialize evaluation runner."""
        self.results = []
        self.test_user_id = None

    async def setup(self):
        """Set up test environment."""
        await init_db()
        
        # Get or create test user
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == "test@evaluation.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                from app.core.security import get_password_hash
                from app.models.user import UserRole
                
                user = User(
                    email="test@evaluation.com",
                    name="Test User",
                    role=UserRole.PATIENT,
                    hashed_password=get_password_hash("test123")
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            self.test_user_id = user.id

    async def run_test(self, test_case: dict) -> dict[str, Any]:
        """Run a single test case."""
        print(f"  Running {test_case['test_id']}: {test_case['description']}")
        
        start_time = time.time()
        
        try:
            # Execute agent with test conversation
            messages = test_case["conversation"]
            
            # Convert to ChatMessage objects
            from app.schemas.agent import ChatMessage
            chat_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in messages]
            
            # Get database session
            async with async_session_maker() as session:
                agent = AgentRouter(session)
                final_message, tool_calls, tool_results, usage = await agent.chat_turn(
                    messages=chat_messages,
                    user_id=self.test_user_id
                )
            
            result = {
                "response": final_message.content,
                "tools_used": [tc.name for tc in tool_calls],
                "success": True,
            }
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Validate against expected outcome
            expected = test_case["expected_outcome"]
            validation_results = self.validate_outcome(result, expected)
            
            return {
                "test_id": test_case["test_id"],
                "category": test_case["category"],
                "description": test_case["description"],
                "passed": validation_results["passed"],
                "latency_ms": latency_ms,
                "validation": validation_results,
                "agent_response": result.get("response", ""),
                "tools_called": result.get("tools_used", []),
                "error": None
            }
            
        except Exception as e:
            return {
                "test_id": test_case["test_id"],
                "category": test_case["category"],
                "description": test_case["description"],
                "passed": False,
                "latency_ms": (time.time() - start_time) * 1000,
                "validation": {"passed": False, "errors": [str(e)]},
                "agent_response": "",
                "tools_called": [],
                "error": str(e)
            }

    def validate_outcome(self, result: dict, expected: dict) -> dict[str, Any]:
        """Validate test result against expected outcome."""
        errors = []
        checks = {}
        
        # Check tools called
        if "tools_called" in expected:
            actual_tools = result.get("tools_used", [])
            expected_tools = expected["tools_called"]
            
            for tool in expected_tools:
                if tool not in actual_tools:
                    errors.append(f"Expected tool '{tool}' was not called")
            
            checks["tools_correct"] = len(errors) == 0
        
        # Check success
        if "success" in expected:
            checks["success"] = result.get("success", False) == expected["success"]
            if not checks["success"]:
                errors.append("Success status does not match expected")
        
        # Check keywords in response
        if "contains_keywords" in expected:
            response = result.get("response", "").lower()
            missing_keywords = []
            
            for keyword in expected["contains_keywords"]:
                if keyword.lower() not in response:
                    missing_keywords.append(keyword)
            
            checks["keywords_present"] = len(missing_keywords) == 0
            if missing_keywords:
                errors.append(f"Missing keywords: {', '.join(missing_keywords)}")
        
        # Check emergency detection
        if expected.get("emergency_detected"):
            response = result.get("response", "").lower()
            checks["emergency_detected"] = any(
                word in response for word in ["911", "emergency", "immediate"]
            )
            if not checks["emergency_detected"]:
                errors.append("Emergency not properly detected")
        
        # Check medical advice rejection
        if expected.get("medical_advice_rejected"):
            response = result.get("response", "").lower()
            checks["medical_advice_rejected"] = any(
                phrase in response for phrase in [
                    "cannot provide medical advice",
                    "not qualified",
                    "consult",
                    "healthcare provider"
                ]
            )
            if not checks["medical_advice_rejected"]:
                errors.append("Medical advice not properly rejected")
        
        # Overall pass/fail
        passed = len(errors) == 0 and all(checks.values())
        
        return {
            "passed": passed,
            "checks": checks,
            "errors": errors
        }

    async def run_all_tests(self):
        """Run all tests in the suite."""
        print(f"\n🧪 Starting Evaluation - {len(TEST_SUITE)} tests")
        print("=" * 70)
        
        await self.setup()
        
        # Group tests by category
        categories = {}
        for test in TEST_SUITE:
            cat = test["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test)
        
        # Run tests by category
        for category, tests in categories.items():
            print(f"\n📁 Category: {category.upper()} ({len(tests)} tests)")
            print("-" * 70)
            
            for test in tests:
                result = await self.run_test(test)
                self.results.append(result)
                
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} - {result['test_id']}: {result['latency_ms']:.0f}ms")
        
        # Generate report
        return self.generate_report()

    def generate_report(self) -> dict[str, Any]:
        """Generate evaluation report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        # Calculate metrics
        latencies = [r["latency_ms"] for r in self.results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        p50_latency = sorted(latencies)[len(latencies) // 2] if latencies else 0
        p90_latency = sorted(latencies)[int(len(latencies) * 0.9)] if latencies else 0
        
        # Success by category
        category_stats = {}
        for result in self.results:
            cat = result["category"]
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0}
            category_stats[cat]["total"] += 1
            if result["passed"]:
                category_stats[cat]["passed"] += 1
        
        for cat in category_stats:
            stats = category_stats[cat]
            stats["success_rate"] = stats["passed"] / stats["total"]
        
        # Compare to baseline and targets
        success_rate = passed_tests / total_tests
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate,
                "avg_latency_ms": avg_latency,
                "p50_latency_ms": p50_latency,
                "p90_latency_ms": p90_latency
            },
            "category_breakdown": category_stats,
            "performance_vs_targets": {
                "task_completion": {
                    "actual": success_rate,
                    "target": PERFORMANCE_TARGETS["task_completion_rate"],
                    "meets_target": success_rate >= PERFORMANCE_TARGETS["task_completion_rate"]
                },
                "response_time_p50": {
                    "actual_ms": p50_latency,
                    "target_ms": PERFORMANCE_TARGETS["avg_response_time_p50"] * 1000,
                    "meets_target": p50_latency <= PERFORMANCE_TARGETS["avg_response_time_p50"] * 1000
                },
                "response_time_p90": {
                    "actual_ms": p90_latency,
                    "target_ms": PERFORMANCE_TARGETS["avg_response_time_p90"] * 1000,
                    "meets_target": p90_latency <= PERFORMANCE_TARGETS["avg_response_time_p90"] * 1000
                }
            },
            "baseline_comparison": {
                "agent_success_rate": success_rate,
                "manual_success_rate": BASELINE_METRICS["success_rate"],
                "improvement": success_rate - BASELINE_METRICS["success_rate"],
                "agent_avg_time_sec": avg_latency / 1000,
                "manual_avg_time_sec": BASELINE_METRICS["avg_call_duration_seconds"],
                "time_savings_sec": BASELINE_METRICS["avg_call_duration_seconds"] - (avg_latency / 1000)
            },
            "detailed_results": self.results
        }
        
        return report

    def save_report(self, report: dict, output_path: str = "/app/data/evaluation_report.json"):
        """Save evaluation report to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {output_path}")


async def run_evaluation():
    """Main evaluation entry point."""
    runner = EvaluationRunner()
    report = await runner.run_all_tests()
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']} ✅")
    print(f"Failed: {report['summary']['failed']} ❌")
    print(f"Success Rate: {report['summary']['success_rate']:.1%}")
    print(f"Avg Latency: {report['summary']['avg_latency_ms']:.0f}ms")
    print(f"P50 Latency: {report['summary']['p50_latency_ms']:.0f}ms")
    print(f"P90 Latency: {report['summary']['p90_latency_ms']:.0f}ms")
    
    print("\n📈 Performance vs Targets:")
    for metric, data in report['performance_vs_targets'].items():
        status = "✅" if data["meets_target"] else "❌"
        print(f"  {status} {metric}: {data}")
    
    print("\n📊 Baseline Comparison:")
    baseline = report['baseline_comparison']
    print(f"  Agent Success Rate: {baseline['agent_success_rate']:.1%}")
    print(f"  Manual Success Rate: {baseline['manual_success_rate']:.1%}")
    print(f"  Improvement: {baseline['improvement']:+.1%}")
    print(f"  Time Savings: {baseline['time_savings_sec']:.1f}s per task")
    
    # Save report
    runner.save_report(report)
    
    return report


if __name__ == "__main__":
    asyncio.run(run_evaluation())
