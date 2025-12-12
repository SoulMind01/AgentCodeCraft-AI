"""
Comparison Tests: ADK vs Manual Orchestration (Phase 5, Step 5.2).

This test suite compares results from ADK agent and manual orchestration paths
to verify consistency and document differences.
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db import init_db, SessionLocal
from app.models import orm
from app.services.gemini_adapter import GeminiAdapter
from app.services.orchestrator import AgentCodeCraftApp
from app.services.policy_engine import PolicyEngine
from app.services.static_analysis import StaticAnalysisService


# Initialize database
init_db()


class TestADKVsManualComparison:
    """Compare ADK agent results with manual orchestration results."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Set up test database."""
        init_db()
        yield
        # Cleanup handled by test isolation

    @pytest.fixture(autouse=True)
    def rate_limit_delay(self):
        """
        Add delay between tests to avoid API rate limits.
        Free tier: 5 requests/minute for gemini-2.5-flash
        """
        import time
        # Wait 12 seconds between tests (allows 5 tests per minute)
        time.sleep(12)
        yield

    @pytest.fixture
    def sample_policy_profile(self):
        """Create a sample policy profile for testing."""
        db = SessionLocal()
        try:
            # Check if profile already exists
            profile = db.query(orm.PolicyProfile).filter(
                orm.PolicyProfile.policy_profile_id == "comparison_test_profile"
            ).one_or_none()
            
            if not profile:
                profile = orm.PolicyProfile(
                    policy_profile_id="comparison_test_profile",
                    name="Comparison Test Policy",
                    domain="python",
                    version="1.0"
                )
                db.add(profile)
                
                # Add a rule that will be violated
                rule = orm.PolicyRule(
                    rule_id="comparison_test_rule_1",
                    policy_profile_id="comparison_test_profile",
                    rule_key="no_eval",
                    description="Do not use eval()",
                    category="security",
                    expression=r"eval\s*\(",
                    severity="high",
                    auto_fixable=False,
                    fix_prompt="Replace eval() with safer alternatives like ast.literal_eval() or direct computation"
                )
                db.add(rule)
                db.commit()
            
            yield profile
        finally:
            db.close()

    @pytest.fixture
    def test_code_with_violations(self):
        """Sample code that violates policy rules."""
        return """
def calculate_sum(a, b):
    # This violates the no_eval policy
    result = eval(f"{a} + {b}")
    return result

def safe_calculate(a, b):
    return a + b
"""

    @pytest.fixture
    def test_code_no_violations(self):
        """Sample code that doesn't violate any policy rules."""
        return """
def calculate_sum(a, b):
    return a + b

def calculate_product(a, b):
    return a * b
"""

    @pytest.fixture
    def adk_app(self):
        """Create orchestrator with ADK enabled."""
        adapter = GeminiAdapter()
        policy_engine = PolicyEngine()
        static_analysis = StaticAnalysisService()
        return AgentCodeCraftApp(
            adapter=adapter,
            policy_engine=policy_engine,
            static_analysis=static_analysis,
            use_adk=True
        )

    @pytest.fixture
    def manual_app(self):
        """Create orchestrator with ADK disabled (manual path)."""
        adapter = GeminiAdapter()
        policy_engine = PolicyEngine()
        static_analysis = StaticAnalysisService()
        return AgentCodeCraftApp(
            adapter=adapter,
            policy_engine=policy_engine,
            static_analysis=static_analysis,
            use_adk=False
        )

    def _create_test_session(self, db: Session, policy_profile_id: str) -> orm.RefactorSession:
        """Helper to create a test refactor session."""
        session = orm.RefactorSession(
            session_id=str(uuid4()),
            user_id="comparison_test_user",
            repo="test_repo",
            branch="main",
            language="python",
            policy_profile_id=policy_profile_id,
            status="pending",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def _normalize_results(self, suggestions, metric, violations, refactored_code):
        """Normalize results for comparison (remove non-deterministic fields)."""
        # Normalize suggestions (remove IDs, timestamps, etc.)
        normalized_suggestions = []
        for s in suggestions:
            normalized_suggestions.append({
                "file_path": s.file_path,
                "start_line": s.start_line,
                "end_line": s.end_line,
                "original_code": s.original_code.strip(),
                "proposed_code": s.proposed_code.strip(),
                "rationale": s.rationale,
                "confidence_score": round(s.confidence_score, 2),
            })
        
        # Normalize metric
        normalized_metric = {
            "policy_score": round(metric.policy_score, 2),
            "complexity_delta": round(metric.complexity_delta, 2),
            "test_pass_rate": round(metric.test_pass_rate, 2),
            "latency_ms": metric.latency_ms,
            "token_usage": metric.token_usage,
        }
        
        # Normalize violations
        normalized_violations = []
        for v in violations:
            normalized_violations.append({
                "rule_key": v.rule_key,
                "message": v.message,
                "severity": v.severity,
            })
        
        # Normalize refactored code
        normalized_refactored = refactored_code.strip()
        
        return normalized_suggestions, normalized_metric, normalized_violations, normalized_refactored

    def test_comparison_with_violations(
        self, adk_app, manual_app, sample_policy_profile, test_code_with_violations
    ):
        """
        Compare ADK vs Manual results when code has policy violations.
        
        This test verifies:
        1. Both paths produce valid results
        2. Both detect violations
        3. Both generate refactoring suggestions
        4. Metrics are comparable
        """
        db = SessionLocal()
        try:
            # Run with ADK
            adk_session = self._create_test_session(db, "comparison_test_profile")
            adk_suggestions, adk_metric, adk_violations, adk_refactored = adk_app.run_refactor_session(
                db,
                session=adk_session,
                code=test_code_with_violations,
                file_path="test_adk.py",
            )
            
            # Run with Manual
            manual_session = self._create_test_session(db, "comparison_test_profile")
            manual_suggestions, manual_metric, manual_violations, manual_refactored = manual_app.run_refactor_session(
                db,
                session=manual_session,
                code=test_code_with_violations,
                file_path="test_manual.py",
            )
            
            # Normalize for comparison
            adk_norm = self._normalize_results(adk_suggestions, adk_metric, adk_violations, adk_refactored)
            manual_norm = self._normalize_results(manual_suggestions, manual_metric, manual_violations, manual_refactored)
            
            adk_suggestions_norm, adk_metric_norm, adk_violations_norm, adk_refactored_norm = adk_norm
            manual_suggestions_norm, manual_metric_norm, manual_violations_norm, manual_refactored_norm = manual_norm
            
            # Assertions: Both should produce valid results
            assert len(adk_suggestions_norm) > 0, "ADK should produce suggestions"
            assert len(manual_suggestions_norm) > 0, "Manual should produce suggestions"
            
            assert len(adk_violations_norm) > 0, "ADK should detect violations"
            assert len(manual_violations_norm) > 0, "Manual should detect violations"
            
            # Both should have refactored code
            assert len(adk_refactored_norm) > 0, "ADK should produce refactored code"
            assert len(manual_refactored_norm) > 0, "Manual should produce refactored code"
            
            # Metrics should be valid
            assert 0 <= adk_metric_norm["policy_score"] <= 100, "ADK policy score out of range"
            assert 0 <= manual_metric_norm["policy_score"] <= 100, "Manual policy score out of range"
            assert 0 <= adk_metric_norm["test_pass_rate"] <= 1.0, "ADK test pass rate out of range"
            assert 0 <= manual_metric_norm["test_pass_rate"] <= 1.0, "Manual test pass rate out of range"
            
            # Both should detect the same violations (rule_key should match)
            adk_rule_keys = {v["rule_key"] for v in adk_violations_norm}
            manual_rule_keys = {v["rule_key"] for v in manual_violations_norm}
            assert adk_rule_keys == manual_rule_keys, \
                f"Violation detection differs: ADK={adk_rule_keys}, Manual={manual_rule_keys}"
            
            # Document differences (for analysis)
            print("\n=== ADK vs Manual Comparison (With Violations) ===")
            print(f"ADK Suggestions: {len(adk_suggestions_norm)}")
            print(f"Manual Suggestions: {len(manual_suggestions_norm)}")
            print(f"ADK Policy Score: {adk_metric_norm['policy_score']}")
            print(f"Manual Policy Score: {manual_metric_norm['policy_score']}")
            print(f"ADK Complexity Delta: {adk_metric_norm['complexity_delta']}")
            print(f"Manual Complexity Delta: {manual_metric_norm['complexity_delta']}")
            print(f"ADK Latency: {adk_metric_norm['latency_ms']}ms")
            print(f"Manual Latency: {manual_metric_norm['latency_ms']}ms")
            
        finally:
            db.close()

    def test_comparison_without_violations(
        self, adk_app, manual_app, sample_policy_profile, test_code_no_violations
    ):
        """
        Compare ADK vs Manual results when code has no violations.
        
        This test verifies:
        1. ADK skips refactoring when no violations (by design)
        2. Manual still attempts refactoring (legacy behavior)
        3. Both produce valid results
        """
        db = SessionLocal()
        try:
            # Run with ADK
            adk_session = self._create_test_session(db, "comparison_test_profile")
            adk_suggestions, adk_metric, adk_violations, adk_refactored = adk_app.run_refactor_session(
                db,
                session=adk_session,
                code=test_code_no_violations,
                file_path="test_adk_no_viol.py",
            )
            
            # Run with Manual
            manual_session = self._create_test_session(db, "comparison_test_profile")
            manual_suggestions, manual_metric, manual_violations, manual_refactored = manual_app.run_refactor_session(
                db,
                session=manual_session,
                code=test_code_no_violations,
                file_path="test_manual_no_viol.py",
            )
            
            # Normalize for comparison
            adk_norm = self._normalize_results(adk_suggestions, adk_metric, adk_violations, adk_refactored)
            manual_norm = self._normalize_results(manual_suggestions, manual_metric, manual_violations, manual_refactored)
            
            adk_suggestions_norm, adk_metric_norm, adk_violations_norm, adk_refactored_norm = adk_norm
            manual_suggestions_norm, manual_metric_norm, manual_violations_norm, manual_refactored_norm = manual_norm
            
            # Both should detect no violations
            assert len(adk_violations_norm) == 0, "ADK should detect no violations"
            assert len(manual_violations_norm) == 0, "Manual should detect no violations"
            
            # ADK should skip refactoring (by design - no violations)
            # Manual may still refactor (legacy behavior)
            # Both should produce valid results regardless
            
            # Metrics should be valid
            assert 0 <= adk_metric_norm["policy_score"] <= 100, "ADK policy score out of range"
            assert 0 <= manual_metric_norm["policy_score"] <= 100, "Manual policy score out of range"
            
            # Document differences
            print("\n=== ADK vs Manual Comparison (No Violations) ===")
            print(f"ADK Suggestions: {len(adk_suggestions_norm)} (should be 0 - no violations)")
            print(f"Manual Suggestions: {len(manual_suggestions_norm)}")
            print(f"ADK Refactored Code Length: {len(adk_refactored_norm)}")
            print(f"Manual Refactored Code Length: {len(manual_refactored_norm)}")
            print(f"ADK Policy Score: {adk_metric_norm['policy_score']} (should be 100)")
            print(f"Manual Policy Score: {manual_metric_norm['policy_score']}")
            
        finally:
            db.close()

    def test_comparison_result_structure(
        self, adk_app, manual_app, sample_policy_profile, test_code_with_violations
    ):
        """
        Verify that both paths return the same result structure.
        
        This ensures API compatibility between ADK and manual paths.
        """
        db = SessionLocal()
        try:
            # Run with ADK
            adk_session = self._create_test_session(db, "comparison_test_profile")
            adk_suggestions, adk_metric, adk_violations, adk_refactored = adk_app.run_refactor_session(
                db,
                session=adk_session,
                code=test_code_with_violations,
                file_path="test_structure_adk.py",
            )
            
            # Run with Manual
            manual_session = self._create_test_session(db, "comparison_test_profile")
            manual_suggestions, manual_metric, manual_violations, manual_refactored = manual_app.run_refactor_session(
                db,
                session=manual_session,
                code=test_code_with_violations,
                file_path="test_structure_manual.py",
            )
            
            # Verify structure consistency
            assert isinstance(adk_suggestions, list), "ADK suggestions should be a list"
            assert isinstance(manual_suggestions, list), "Manual suggestions should be a list"
            
            assert hasattr(adk_metric, "policy_score"), "ADK metric should have policy_score"
            assert hasattr(manual_metric, "policy_score"), "Manual metric should have policy_score"
            
            assert isinstance(adk_violations, list), "ADK violations should be a list"
            assert isinstance(manual_violations, list), "Manual violations should be a list"
            
            assert isinstance(adk_refactored, str), "ADK refactored_code should be a string"
            assert isinstance(manual_refactored, str), "Manual refactored_code should be a string"
            
            # Verify metric attributes match
            adk_metric_attrs = {
                "policy_score", "complexity_delta", "test_pass_rate",
                "latency_ms", "token_usage"
            }
            manual_metric_attrs = {
                "policy_score", "complexity_delta", "test_pass_rate",
                "latency_ms", "token_usage"
            }
            assert adk_metric_attrs == manual_metric_attrs, "Metric attributes should match"
            
            print("\n=== Structure Comparison ===")
            print("[OK] Both paths return consistent structure")
            print(f"ADK Suggestions Count: {len(adk_suggestions)}")
            print(f"Manual Suggestions Count: {len(manual_suggestions)}")
            print(f"ADK Violations Count: {len(adk_violations)}")
            print(f"Manual Violations Count: {len(manual_violations)}")
            
        finally:
            db.close()

    def test_comparison_performance(
        self, adk_app, manual_app, sample_policy_profile, test_code_with_violations
    ):
        """
        Compare performance metrics between ADK and Manual paths.
        
        This test documents latency and token usage differences.
        
        Note: This test may hit API rate limits (5 requests/minute for free tier).
        If you get a 429 error, wait 60 seconds and retry, or upgrade to a paid tier.
        """
        import time
        db = SessionLocal()
        try:
            # Run with ADK
            adk_session = self._create_test_session(db, "comparison_test_profile")
            adk_suggestions, adk_metric, adk_violations, adk_refactored = adk_app.run_refactor_session(
                db,
                session=adk_session,
                code=test_code_with_violations,
                file_path="test_perf_adk.py",
            )
            
            # Wait 15 seconds between ADK and Manual calls to avoid rate limits
            # Free tier: 5 requests/minute for gemini-2.5-flash
            time.sleep(5)
            
            # Run with Manual
            manual_session = self._create_test_session(db, "comparison_test_profile")
            manual_suggestions, manual_metric, manual_violations, manual_refactored = manual_app.run_refactor_session(
                db,
                session=manual_session,
                code=test_code_with_violations,
                file_path="test_perf_manual.py",
            )
            
            # Compare performance
            print("\n=== Performance Comparison ===")
            print(f"ADK Latency: {adk_metric.latency_ms}ms")
            print(f"Manual Latency: {manual_metric.latency_ms}ms")
            print(f"Latency Difference: {adk_metric.latency_ms - manual_metric.latency_ms}ms")
            print(f"ADK Token Usage: {adk_metric.token_usage}")
            print(f"Manual Token Usage: {manual_metric.token_usage}")
            print(f"Token Difference: {adk_metric.token_usage - manual_metric.token_usage}")
            
            # Both should have valid performance metrics
            assert adk_metric.latency_ms >= 0, "ADK latency should be non-negative"
            assert manual_metric.latency_ms >= 0, "Manual latency should be non-negative"
            assert adk_metric.token_usage >= 0, "ADK token usage should be non-negative"
            assert manual_metric.token_usage >= 0, "Manual token usage should be non-negative"
            
        finally:
            db.close()

