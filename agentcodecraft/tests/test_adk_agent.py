"""
Unit tests for ADK Agent (Phase 3, Step 3.2).

Tests the AgentCodeCraftAgent workflow implementation.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import orm
from app.services.adk_agent import AgentCodeCraftAgent
from app.services.agent_framework import WorkflowStep


class TestAgentCodeCraftAgent:
    """Test suite for AgentCodeCraftAgent."""

    @pytest.fixture
    def agent(self):
        """Create an AgentCodeCraftAgent instance."""
        return AgentCodeCraftAgent()

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        db = Mock(spec=Session)
        db.commit = Mock()
        db.rollback = Mock()
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
        return session

    @pytest.fixture
    def sample_code(self):
        """Sample Python code for testing."""
        return """
def hello(name):
    return f"Hello, {name}!"
"""

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent is not None
        assert hasattr(agent, 'llm_agent')
        assert hasattr(agent, 'policy_engine')
        assert hasattr(agent, 'static_analysis')

    def test_preflight_checks_valid_input(self, agent, mock_db_session, mock_session, sample_code):
        """Test pre-flight checks with valid inputs."""
        # Mock policy profile exists
        mock_profile = Mock()
        mock_profile.policy_profile_id = "test_profile_id"
        
        mock_rule = Mock()
        mock_rule.policy_profile_id = "test_profile_id"
        
        mock_db_session.query.return_value.filter.return_value.one_or_none.return_value = mock_profile
        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_rule]
        
        agent.policy_engine.load_profile = Mock(return_value=mock_profile)
        
        context = Mock()
        context.language = "python"
        context.file_path = "test.py"
        
        is_valid, error = agent._preflight_checks(
            sample_code, "test.py", "test_profile_id", mock_db_session, context
        )
        
        assert is_valid is True
        assert error is None

    def test_preflight_checks_empty_code(self, agent, mock_db_session, mock_session):
        """Test pre-flight checks with empty code."""
        context = Mock()
        context.language = "python"
        
        is_valid, error = agent._preflight_checks(
            "", "test.py", "test_profile_id", mock_db_session, context
        )
        
        assert is_valid is False
        assert "empty" in error.lower()

    def test_preflight_checks_missing_policy_profile(self, agent, mock_db_session, mock_session, sample_code):
        """Test pre-flight checks with missing policy profile."""
        agent.policy_engine.load_profile = Mock(return_value=None)
        
        context = Mock()
        context.language = "python"
        
        is_valid, error = agent._preflight_checks(
            sample_code, "test.py", "test_profile_id", mock_db_session, context
        )
        
        assert is_valid is False
        assert "not found" in error.lower()

    @patch('app.services.adk_agent.StaticAnalysisTool')
    def test_analyze_code_success(self, mock_tool, agent, sample_code):
        """Test code analysis step."""
        mock_result = {
            "complexity": 1.0,
            "line_count": 3,
            "function_count": 1,
            "functions": ["hello"],
            "classes": []
        }
        mock_tool.func.return_value = mock_result
        
        state = Mock()
        context = Mock()
        
        result = agent._analyze_code(sample_code, state, context)
        
        assert result == mock_result
        state.record_step_completion.assert_called_once()
        context.update_analysis.assert_called_once_with(mock_result)

    @patch('app.services.adk_agent.StaticAnalysisTool')
    def test_analyze_code_failure(self, mock_tool, agent, sample_code):
        """Test code analysis step with failure (fallback)."""
        mock_tool.func.side_effect = Exception("Analysis failed")
        
        state = Mock()
        context = Mock()
        
        result = agent._analyze_code(sample_code, state, context)
        
        assert result["complexity"] == 0.0
        assert result["line_count"] == 0
        state.record_error.assert_called_once()
        state.record_warning.assert_called_once()

    def test_evaluate_policies_success(self, agent, mock_db_session, sample_code):
        """Test policy evaluation step."""
        mock_profile = Mock()
        mock_profile.rules = [Mock(), Mock()]  # 2 rules
        
        mock_violation = Mock()
        mock_violation.rule_id = "rule1"
        mock_violation.rule_key = "test_rule"
        mock_violation.message = "Test violation"
        mock_violation.severity = "high"
        mock_violation.fix_prompt = "Fix this"
        
        agent.policy_engine.load_profile = Mock(return_value=mock_profile)
        agent.policy_engine.evaluate = Mock(return_value=[mock_violation])
        agent.policy_engine.score_compliance = Mock(return_value=0.5)
        
        state = Mock()
        context = Mock()
        
        result = agent._evaluate_policies(
            sample_code, "test_profile_id", mock_db_session, state, context
        )
        
        assert "violations" in result
        assert len(result["violations"]) == 1
        assert result["compliance_score"] == 0.5
        assert result["total_rules"] == 2
        state.record_step_completion.assert_called_once()
        context.update_policy_evaluation.assert_called_once()

    def test_should_refactor_with_violations(self, agent, mock_db_session, mock_session, sample_code):
        """Test decision point: should refactor when violations found."""
        # Create state with violations
        state = Mock()
        state.tool_results = {
            "policy_evaluation": {
                "violations": [{"rule_id": "rule1", "severity": "high"}]
            }
        }
        state.metrics = {}
        
        # Use the actual should_refactor method from AgentSessionState
        from app.services.agent_framework import AgentSessionState
        
        test_state = AgentSessionState(session_id="test")
        test_state.tool_results = {
            "policy_evaluation": {
                "violations": [{"rule_id": "rule1", "severity": "high"}]
            }
        }
        
        assert test_state.should_refactor() is True

    def test_should_refactor_no_violations(self, agent, mock_db_session, mock_session, sample_code):
        """Test decision point: should not refactor when no violations."""
        from app.services.agent_framework import AgentSessionState
        
        test_state = AgentSessionState(session_id="test")
        test_state.tool_results = {
            "policy_evaluation": {
                "violations": []
            }
        }
        
        assert test_state.should_refactor() is False

    @patch('app.services.adk_agent.GeminiRefactorTool')
    def test_refactor_code_success(self, mock_tool, agent, sample_code):
        """Test refactoring step."""
        mock_result = {
            "suggestions": [
                {
                    "suggestion_id": "sug1",
                    "file_path": "test.py",
                    "start_line": 1,
                    "end_line": 3,
                    "original_code": sample_code,
                    "proposed_code": "def hello(name):\n    return f'Hello, {name}!'",
                    "rationale": "Improved formatting",
                    "confidence_score": 0.9
                }
            ],
            "refactored_code": "def hello(name):\n    return f'Hello, {name}!'"
        }
        mock_tool.func.return_value = mock_result
        
        policy_result = {"violations": [{"rule_id": "rule1"}]}
        state = Mock()
        context = Mock()
        
        result = agent._refactor_code(sample_code, policy_result, "test.py", state, context)
        
        assert result == mock_result
        state.record_step_completion.assert_called_once()
        context.update_refactoring.assert_called_once()

    @patch('app.services.adk_agent.GeminiRefactorTool')
    def test_refactor_code_failure(self, mock_tool, agent, sample_code):
        """Test refactoring step with failure (fallback to original)."""
        mock_tool.func.side_effect = Exception("Refactoring failed")
        
        policy_result = {"violations": [{"rule_id": "rule1"}]}
        state = Mock()
        context = Mock()
        
        result = agent._refactor_code(sample_code, policy_result, "test.py", state, context)
        
        assert result["refactored_code"] == sample_code
        assert result["suggestions"] == []
        state.record_error.assert_called_once()
        state.record_warning.assert_called_once()

    def test_validate_refactored_code(self, agent, mock_db_session, sample_code):
        """Test validation step."""
        refactored_code = "def hello(name):\n    return f'Hello, {name}!'"
        
        mock_profile = Mock()
        agent.policy_engine.load_profile = Mock(return_value=mock_profile)
        agent.policy_engine.evaluate = Mock(return_value=[])
        
        with patch('app.services.adk_agent.TestRunnerTool') as mock_test_tool:
            mock_test_tool.func.return_value = {"test_pass_rate": 1.0}
            
            agent.static_analysis.compute_complexity = Mock(side_effect=[1.0, 0.8])
            
            state = Mock()
            context = Mock()
            context.language = "python"
            
            result = agent._validate_refactored_code(
                sample_code, refactored_code, "test_profile_id", mock_db_session, state, context
            )
            
            assert "refactored_code_valid" in result
            assert "policy_compliance" in result
            assert "test_results" in result
            assert "complexity_validation" in result
            state.record_step_completion.assert_called_once()
            context.update_validation.assert_called_once()

    def test_calculate_metrics(self, agent, sample_code):
        """Test metrics calculation step."""
        context = Mock()
        context.get_refactored_code.return_value = "def hello(name):\n    return f'Hello, {name}!'"
        context.compliance_score = 0.9
        context.test_pass_rate = 1.0
        
        agent.static_analysis.summarize_complexity = Mock(return_value=-0.2)
        
        state = Mock()
        state.metrics = {}
        
        result = agent._calculate_metrics(sample_code, context, state)
        
        assert "complexity_delta" in result
        assert "policy_score" in result
        assert "test_pass_rate" in result
        assert "latency_ms" in result
        assert "token_usage" in result
        assert result["complexity_delta"] == -0.2
        assert result["policy_score"] == 0.9
        assert result["test_pass_rate"] == 1.0

    def test_save_results(self, agent, mock_db_session, mock_session):
        """Test save results step."""
        context = Mock()
        context.get_refactored_code.return_value = "def hello(name):\n    return f'Hello, {name}!'"
        context.refactoring_suggestions = [
            {
                "suggestion_id": "sug1",
                "file_path": "test.py",
                "start_line": 1,
                "end_line": 3,
                "original_code": "def hello(name): pass",
                "proposed_code": "def hello(name):\n    return f'Hello, {name}!'",
                "rationale": "Added return statement",
                "confidence_score": 0.9
            }
        ]
        context.policy_violations = [
            {
                "rule_id": "rule1",
                "rule_key": "test_rule",
                "message": "Test violation",
                "severity": "high",
                "fix_prompt": "Fix this"
            }
        ]
        
        metrics = {
            "complexity_delta": -0.2,
            "policy_score": 0.9,
            "test_pass_rate": 1.0,
            "latency_ms": 100,
            "token_usage": 50
        }
        
        state = Mock()
        
        suggestions, metric, violations, refactored_code = agent._save_results(
            mock_db_session, mock_session, context, metrics, state
        )
        
        assert len(suggestions) == 1
        assert metric is not None
        assert len(violations) == 1
        assert refactored_code == context.get_refactored_code()
        mock_db_session.add.assert_called()
        state.record_step_completion.assert_called_once()

    def test_final_validation(self, agent):
        """Test final validation step."""
        state = Mock()
        state.is_workflow_complete.return_value = True
        
        context = Mock()
        context.refactoring_suggestions = []
        
        metrics = {
            "complexity_delta": -0.2,
            "policy_score": 0.9,
            "test_pass_rate": 1.0,
            "latency_ms": 100,
            "token_usage": 50
        }
        
        agent._final_validation(state, context, metrics)
        
        # Should not record warnings if everything is complete
        state.record_warning.assert_not_called()

    def test_final_validation_missing_metrics(self, agent):
        """Test final validation with missing metrics."""
        state = Mock()
        state.is_workflow_complete.return_value = True
        
        context = Mock()
        context.refactoring_suggestions = []
        
        metrics = {
            "complexity_delta": -0.2,
            # Missing other metrics
        }
        
        agent._final_validation(state, context, metrics)
        
        # Should record warnings for missing metrics
        assert state.record_warning.called

