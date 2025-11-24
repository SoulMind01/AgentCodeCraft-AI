"""
End-to-End Test for ADK Agent Workflow (Phase 5).

Tests the complete workflow from API endpoint through ADK agent to database.
This demonstrates full system integration.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.main import app
from app.db import init_db, SessionLocal
from app.models import orm
from app.config import get_settings


# Initialize test client
client = TestClient(app)
init_db()


class TestEndToEndADKWorkflow:
    """End-to-end tests for complete ADK agent workflow."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Set up test database."""
        init_db()
        yield
        # Cleanup handled by test isolation

    @pytest.fixture
    def sample_policy_profile(self):
        """Create a sample policy profile for testing."""
        db = SessionLocal()
        try:
            # Check if profile already exists
            profile = db.query(orm.PolicyProfile).filter(
                orm.PolicyProfile.policy_profile_id == "test_e2e_profile"
            ).one_or_none()
            
            if not profile:
                profile = orm.PolicyProfile(
                    policy_profile_id="test_e2e_profile",
                    name="E2E Test Policy",
                    domain="python",
                    version="1.0"
                )
                db.add(profile)
                
                # Add a simple rule
                rule = orm.PolicyRule(
                    rule_id="test_e2e_rule_1",
                    policy_profile_id="test_e2e_profile",
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
    def sample_code(self):
        """Sample code with policy violations."""
        return """
def dangerous_function():
    result = eval("2 + 2")
    return result

def safe_function():
    return 2 + 2
"""

    def test_complete_workflow_with_adk_enabled(self, sample_policy_profile, sample_code):
        """
        Test complete workflow: API -> Orchestrator -> ADK Agent -> Database.
        
        This test verifies:
        1. API endpoint accepts request
        2. Orchestrator routes to ADK agent (if enabled)
        3. ADK agent executes full workflow
        4. Results are saved to database
        5. Response contains all expected fields
        
        Note: This test requires ADK to be enabled via USE_ADK=true in .env file.
        If ADK is not enabled, the test will use the manual orchestrator path.
        """
        # Make API request
        response = client.post(
            "/refactor",
            json={
                "user_id": "e2e_test_user",
                "user_name": "E2E Test User",
                "code": sample_code,
                "language": "python",
                "policy_profile_id": "test_e2e_profile",
                "file_path": "test_e2e.py"
            }
        )
        
        # Verify response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify session
        assert "session" in data
        assert data["session"]["status"] in ["completed", "running"]
        assert data["session"]["session_id"] is not None
        
        # Verify suggestions
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        
        # Verify compliance metrics
        assert "compliance" in data
        assert "policy_score" in data["compliance"]
        assert "complexity_delta" in data["compliance"]
        assert "test_pass_rate" in data["compliance"]
        
        # Verify violations
        assert "violations" in data
        assert isinstance(data["violations"], list)
        
        # Verify code
        assert "original_code" in data
        assert "refactored_code" in data
        assert len(data["refactored_code"]) > 0
        
        # Verify database persistence
        db = SessionLocal()
        try:
            session = db.query(orm.RefactorSession).filter(
                orm.RefactorSession.session_id == data["session"]["session_id"]
            ).one_or_none()
            assert session is not None, "Session not found in database"
            assert session.status in ["completed", "running"]
            
            # Verify suggestions saved
            suggestions = db.query(orm.RefactorSuggestion).filter(
                orm.RefactorSuggestion.session_id == session.session_id
            ).all()
            assert len(suggestions) == len(data["suggestions"])
            
            # Verify metrics saved
            metric = db.query(orm.ComplianceMetric).filter(
                orm.ComplianceMetric.session_id == session.session_id
            ).one_or_none()
            assert metric is not None, "Compliance metric not found in database"
            assert metric.policy_score == data["compliance"]["policy_score"]
            
        finally:
            db.close()

    def test_workflow_handles_invalid_code(self, sample_policy_profile):
        """Test workflow handles invalid code gracefully."""
        invalid_code = """
def broken_function(
    # Missing closing parenthesis
    return 42
"""
        
        response = client.post(
            "/refactor",
            json={
                "user_id": "e2e_test_user",
                "user_name": "E2E Test User",
                "code": invalid_code,
                "language": "python",
                "policy_profile_id": "test_e2e_profile",
                "file_path": "test_invalid.py"
            }
        )
        
        # Should either fail gracefully or handle error
        # (Depends on implementation - could be 400 or 500)
        assert response.status_code in [400, 422, 500]

    def test_workflow_handles_missing_policy(self, sample_code):
        """Test workflow handles missing policy profile."""
        response = client.post(
            "/refactor",
            json={
                "user_id": "e2e_test_user",
                "user_name": "E2E Test User",
                "code": sample_code,
                "language": "python",
                "policy_profile_id": "nonexistent_profile",
                "file_path": "test.py"
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_workflow_metrics_accuracy(self, sample_policy_profile, sample_code):
        """Test that workflow produces accurate metrics."""
        response = client.post(
            "/refactor",
            json={
                "user_id": "e2e_test_user",
                "user_name": "E2E Test User",
                "code": sample_code,
                "language": "python",
                "policy_profile_id": "test_e2e_profile",
                "file_path": "test_metrics.py"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify metric ranges
        compliance = data["compliance"]
        assert 0 <= compliance["policy_score"] <= 100, "Policy score out of range"
        assert -100 <= compliance["complexity_delta"] <= 100, "Complexity delta out of range"
        assert 0 <= compliance["test_pass_rate"] <= 1.0, "Test pass rate out of range"
        assert compliance["latency_ms"] >= 0, "Latency should be non-negative"
        assert compliance["token_usage"] >= 0, "Token usage should be non-negative"

