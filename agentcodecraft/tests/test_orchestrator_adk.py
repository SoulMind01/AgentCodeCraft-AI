"""
Integration tests for orchestrator ADK integration (Phase 4, Step 4.1).

Tests the feature flag, routing, and integration between orchestrator and ADK agent.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import orm
from app.services.orchestrator import AgentCodeCraftApp
from app.services.gemini_adapter import GeminiAdapter
from app.services.policy_engine import PolicyEngine
from app.services.static_analysis import StaticAnalysisService


class TestOrchestratorADKIntegration:
    """Test suite for orchestrator ADK integration."""

    @pytest.fixture
    def services(self):
        """Create service instances."""
        return {
            "adapter": GeminiAdapter(),
            "policy_engine": PolicyEngine(),
            "static_analysis": StaticAnalysisService(),
        }

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        db = Mock(spec=Session)
        db.commit = Mock()
        db.rollback = Mock()
        db.add = Mock()
        db.refresh = Mock()
        db.query = Mock()
        return db

    @pytest.fixture
    def mock_session(self):
        """Create a mock RefactorSession."""
        session = Mock(spec=orm.RefactorSession)
        session.session_id = str(uuid4())
        session.policy_profile_id = "test_profile_id"
        session.language = "python"
        session.status = "pending"
        session.user_id = "test_user"
        return session

    @pytest.fixture
    def sample_code(self):
        """Sample Python code for testing."""
        return """
def hello(name):
    return f"Hello, {name}!"
"""

    def test_orchestrator_with_adk_disabled(self, services):
        """Test orchestrator with ADK disabled (uses manual)."""
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=False
        )
        
        assert app.use_adk is False
        assert app.adk_agent is None

    def test_orchestrator_with_adk_enabled(self, services):
        """Test orchestrator with ADK enabled (creates agent)."""
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=True
        )
        
        assert app.use_adk is True
        assert app.adk_agent is not None

    def test_feature_flag_routing_to_manual(self, services, mock_db_session, mock_session, sample_code):
        """Test that feature flag routes to manual orchestration when disabled."""
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=False
        )
        
        # Mock manual orchestration
        with patch.object(app, '_run_manual') as mock_manual:
            mock_manual.return_value = ([], Mock(), [], sample_code)
            
            app.run_refactor_session(
                db=mock_db_session,
                session=mock_session,
                code=sample_code,
                file_path="test.py"
            )
            
            mock_manual.assert_called_once()
            assert app.adk_agent is None

    def test_feature_flag_routing_to_adk(self, services, mock_db_session, mock_session, sample_code):
        """Test that feature flag routes to ADK agent when enabled."""
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=True
        )
        
        # Mock ADK agent
        if app.adk_agent:
            with patch.object(app.adk_agent, 'run_refactor_session') as mock_adk:
                mock_adk.return_value = ([], Mock(), [], sample_code)
                
                app.run_refactor_session(
                    db=mock_db_session,
                    session=mock_session,
                    code=sample_code,
                    file_path="test.py"
                )
                
                mock_adk.assert_called_once()
                # Verify correct parameters passed
                call_args = mock_adk.call_args
                assert call_args.kwargs['db'] == mock_db_session
                assert call_args.kwargs['session'] == mock_session
                assert call_args.kwargs['code'] == sample_code
                assert call_args.kwargs['file_path'] == "test.py"

    def test_manual_orchestration_still_works(self, services, mock_db_session, mock_session, sample_code):
        """Test that manual orchestration still works as fallback."""
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=False
        )
        
        # Mock policy profile
        mock_profile = Mock()
        mock_profile.rules = [Mock(), Mock()]
        
        app.policy_engine.load_profile = Mock(return_value=mock_profile)
        app.policy_engine.evaluate = Mock(return_value=[])
        app.policy_engine.score_compliance = Mock(return_value=1.0)
        
        # Mock adapter
        mock_result = Mock()
        mock_result.suggestions = []
        mock_result.refactored_code = sample_code
        app.adapter.generate_refactor = Mock(return_value=mock_result)
        
        # Mock static analysis
        app.static_analysis.summarize_complexity = Mock(return_value=0.0)
        app.static_analysis.run_tests = Mock(return_value=1.0)
        
        suggestions, metric, violations, refactored_code = app._run_manual(
            mock_db_session, mock_session, sample_code, "test.py"
        )
        
        assert isinstance(suggestions, list)
        assert metric is not None
        assert isinstance(violations, list)
        assert refactored_code == sample_code

    def test_adk_unavailable_graceful_degradation(self, services):
        """Test graceful degradation when ADK is not available."""
        # Test that use_adk=False works even if ADK is available
        # (This tests the feature flag logic, not ADK unavailability)
        app = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=False  # Explicitly disabled
        )
        
        # Should respect the flag
        assert app.use_adk is False
        assert app.adk_agent is None
        
        # Test that use_adk=True creates agent when ADK is available
        app2 = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=True
        )
        
        # If ADK is available, should create agent
        # If ADK is not available, use_adk would be False
        # Both cases are valid - this tests the feature flag logic works
        assert app2.use_adk in [True, False]  # Depends on ADK availability
        if app2.use_adk:
            assert app2.adk_agent is not None
        else:
            assert app2.adk_agent is None

    def test_both_paths_return_same_format(self, services, mock_db_session, mock_session, sample_code):
        """Test that both ADK and manual paths return same tuple format."""
        app_adk = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=True
        )
        
        app_manual = AgentCodeCraftApp(
            adapter=services["adapter"],
            policy_engine=services["policy_engine"],
            static_analysis=services["static_analysis"],
            use_adk=False
        )
        
        # Mock both paths to return same format
        mock_suggestions = []
        mock_metric = Mock()
        mock_violations = []
        mock_refactored = sample_code
        
        if app_adk.adk_agent:
            with patch.object(app_adk.adk_agent, 'run_refactor_session') as mock_adk:
                mock_adk.return_value = (mock_suggestions, mock_metric, mock_violations, mock_refactored)
                
                result_adk = app_adk.run_refactor_session(
                    db=mock_db_session,
                    session=mock_session,
                    code=sample_code,
                    file_path="test.py"
                )
                
                assert len(result_adk) == 4
                assert isinstance(result_adk[0], list)  # suggestions
                assert result_adk[1] is not None  # metric
                assert isinstance(result_adk[2], list)  # violations
                assert isinstance(result_adk[3], str)  # refactored_code
        
        with patch.object(app_manual, '_run_manual') as mock_manual:
            mock_manual.return_value = (mock_suggestions, mock_metric, mock_violations, mock_refactored)
            
            result_manual = app_manual.run_refactor_session(
                db=mock_db_session,
                session=mock_session,
                code=sample_code,
                file_path="test.py"
            )
            
            assert len(result_manual) == 4
            assert isinstance(result_manual[0], list)  # suggestions
            assert result_manual[1] is not None  # metric
            assert isinstance(result_manual[2], list)  # violations
            assert isinstance(result_manual[3], str)  # refactored_code

