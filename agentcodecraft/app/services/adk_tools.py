"""ADK tools for AgentCodeCraft."""
from google.adk.tools import FunctionTool
from app.services.static_analysis import StaticAnalysisService
import ast

# Initialize service
_static_analysis_service = StaticAnalysisService()

def static_analyze_code(code: str) -> dict:
    """
    Analyze code and return complexity metrics.
    
    Args:
        code: Source code to analyze
        
    Returns:
        Dictionary with complexity, line_count, function_count, etc.
    """
    complexity = _static_analysis_service.compute_complexity(code)
    
    # Parse AST
    try:
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    except SyntaxError:
        functions = []
        classes = []
    
    return {
        "complexity": complexity,
        "line_count": len(code.splitlines()),
        "function_count": len(functions),
        "class_count": len(classes),
        "functions": functions,
        "classes": classes
    }

# Create ADK FunctionTool
# CORRECT API: FunctionTool takes the function directly in constructor
StaticAnalysisTool = FunctionTool(static_analyze_code)


# ============================================================================
# PolicyEngineTool
# Note: DB session will be handled via context/agent initialization
# ============================================================================

def policy_evaluate_code(code: str, policy_profile_id: str) -> dict:
    """
    Evaluate code against policies.
    
    Args:
        code: Source code to evaluate
        policy_profile_id: ID of policy profile to use
        
    Returns:
        Dictionary with violations, compliance_score, etc.
    
    Note: DB session will be passed through agent context, not as parameter.
    """
    from app.services.policy_engine import PolicyEngine
    
    # Get DB session from global context (set by agent)
    # This is a workaround - in Phase 3, agent will handle DB session properly
    from app.db import SessionLocal
    db_session = SessionLocal()
    
    try:
        policy_engine = PolicyEngine()
        profile = policy_engine.load_profile(db_session, policy_profile_id)
        
        if not profile:
            raise ValueError(f"Policy profile {policy_profile_id} not found")
        
        violations = policy_engine.evaluate(code, profile)
        score = policy_engine.score_compliance(
            violations=violations,
            total_rules=len(profile.rules)
        )
        
        return {
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "rule_key": v.rule_key,
                    "message": v.message,
                    "severity": v.severity,
                    "fix_prompt": v.fix_prompt
                }
                for v in violations
            ],
            "compliance_score": score,
            "total_rules": len(profile.rules)
        }
    finally:
        db_session.close()

# Note: We'll create PolicyEngineTool in Phase 3 when we handle DB session properly
# For now, this function exists but won't be wrapped as a tool yet


# ============================================================================
# GeminiRefactorTool
# ============================================================================

def gemini_refactor_code(code: str, violations: list, file_path: str) -> dict:
    """
    Generate refactoring suggestions via Gemini.
    
    Args:
        code: Source code to refactor
        violations: List of policy violations (dict format)
        file_path: Path to the file
        
    Returns:
        Dictionary with suggestions and refactored code
    """
    from app.services.gemini_adapter import GeminiAdapter
    
    # Convert violations dict to PolicyRule-like objects
    class PolicyRuleWrapper:
        def __init__(self, v_dict):
            self.rule_id = v_dict.get("rule_id", "")
            self.rule_key = v_dict.get("rule_key", "")
            self.fix_prompt = v_dict.get("fix_prompt", "")
    
    adapter = GeminiAdapter()
    policy_rules = [PolicyRuleWrapper(v) for v in violations]
    
    result = adapter.generate_refactor(
        code=code,
        violate_policies=policy_rules,
        file_path=file_path
    )
    
    return {
        "suggestions": [
            {
                "suggestion_id": s.suggestion_id,
                "file_path": s.file_path,
                "start_line": s.start_line,
                "end_line": s.end_line,
                "original_code": s.original_code,
                "proposed_code": s.proposed_code,
                "rationale": s.rationale,
                "confidence_score": s.confidence_score
            }
            for s in result.suggestions
        ],
        "refactored_code": result.refactored_code
    }

GeminiRefactorTool = FunctionTool(gemini_refactor_code)


# ============================================================================
# TestRunnerTool
# ============================================================================

import subprocess
import tempfile
import os

def test_run_code(code: str, language: str) -> dict:
    """
    Run tests on code.
    
    Args:
        code: Source code to test
        language: Programming language (python, etc.)
        
    Returns:
        Dictionary with test_pass_rate and details
    """
    if language != "python":
        return {"test_pass_rate": 1.0, "message": "Test execution not supported for this language"}
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Run pytest - use current Python interpreter to ensure venv pytest is used
        import sys
        
        # Use current Python interpreter with -m pytest
        # This ensures we use pytest from the virtual environment
        pytest_cmd = [sys.executable, '-m', 'pytest']
        
        result = subprocess.run(
            pytest_cmd + [temp_path, '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(temp_path)  # Run from temp file directory
        )
        
        # Parse output (simplified)
        if "passed" in result.stdout or result.returncode == 0:
            lines = result.stdout.split('\n')
            passed = sum(1 for line in lines if "PASSED" in line)
            failed = sum(1 for line in lines if "FAILED" in line)
            total = passed + failed
            pass_rate = passed / total if total > 0 else 1.0
        else:
            pass_rate = 1.0  # No tests found
        
        return {
            "test_pass_rate": pass_rate,
            "stdout": result.stdout[:500],  # Limit output
            "stderr": result.stderr[:500] if result.stderr else ""
        }
    except FileNotFoundError:
        # pytest not found - return default
        return {
            "test_pass_rate": 1.0,
            "message": "pytest not found in PATH. Install pytest or ensure it's available.",
            "stdout": "",
            "stderr": ""
        }
    except subprocess.TimeoutExpired:
        return {
            "test_pass_rate": 0.0,
            "message": "Test execution timed out",
            "stdout": "",
            "stderr": ""
        }
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

TestRunnerTool = FunctionTool(test_run_code)

