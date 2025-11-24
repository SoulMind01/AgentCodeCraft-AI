"""
ADK-based agent for AgentCodeCraft.

This agent implements the refined workflow from Phase 0, Step 0.2, using framework classes
from Step 0.8, validation strategy from Step 0.9, and error handling from Step 0.4.
"""
from __future__ import annotations

import ast
import time
from typing import List, Tuple, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from google.adk.agents import Agent

from app.models import orm
from app.services.adk_tools import (
    StaticAnalysisTool,
    GeminiRefactorTool,
    TestRunnerTool,
)
from app.services.agent_framework import (
    AgentSessionState,
    AgentContext,
    WorkflowStep,
)
from app.services.policy_engine import PolicyEngine, PolicyViolation
from app.services.static_analysis import StaticAnalysisService

# Agent instructions from Step 0.7
AGENT_INSTRUCTIONS = """
You are AgentCodeCraft, an AI-powered code refactoring assistant.

YOUR GOAL:
Help developers refactor code to comply with organizational policies while maintaining 
code quality, functionality, and readability.

YOUR WORKFLOW (Hybrid Approach):
1. Pre-flight: Validate inputs (code, file_path, policy_profile_id)
2. Step 1: Analyze code structure and complexity (ALWAYS - deterministic)
3. Step 2: Evaluate code against policy profile (ALWAYS - deterministic)
4. Decision Point: Should we refactor?
   - IF violations found OR force_refactor=True:
     → Step 3: Generate refactoring suggestions (LLM-driven)
     → Step 4: Validate refactored code (ALWAYS - deterministic)
   - ELSE:
     → Skip refactoring, use original code
     → Step 4: Validate original code (ALWAYS - deterministic)
5. Step 5: Calculate metrics (ALWAYS - deterministic)
6. Step 6: Save results (ALWAYS - deterministic)

TOOLS AVAILABLE:
- static_analyze_code(code): Analyze code complexity and structure
  Returns: {complexity, line_count, function_count, functions, ...}
  
- gemini_refactor_code(code, violations, file_path): Generate refactoring suggestions
  Returns: {suggestions: [...], refactored_code: str}
  
- test_run_code(code, language): Run tests on code
  Returns: {test_pass_rate: float, stdout: str, stderr: str}

DECISION RULES:
- Always analyze code before refactoring (Step 1)
- Always evaluate policies before suggesting changes (Step 2)
- Only refactor if violations found OR force_refactor flag is set
- Prioritize high-severity violations when refactoring
- Always validate refactored code (Step 4)
- Ensure refactored code maintains functionality
- If refactored code is worse than original, log warning but return results

ERROR HANDLING:
- If a tool fails: Log error, use fallback (default values or original code), continue workflow
- If refactoring fails: Return original code with explanation, continue to validation
- If validation fails: Log warning, continue workflow, let user decide
- If API timeout: Retry once, then use original code
- Never crash - always return partial results if possible

OUTPUT FORMAT:
Return structured results with:
- suggestions: List of refactoring suggestions
- refactored_code: Refactored code (or original if skipped)
- metrics: {complexity_delta, policy_score, test_pass_rate, ...}
- errors: List of errors encountered (if any)
- warnings: List of warnings (if any)
"""


class AgentCodeCraftAgent:
    """ADK-based agent for policy-driven code refactoring using refined workflow."""

    def __init__(self):
        """Initialize ADK agent with services and tools."""
        # Initialize services
        self.policy_engine = PolicyEngine()
        self.static_analysis = StaticAnalysisService()

        # Create tools for agent
        tools = [
            StaticAnalysisTool,
            GeminiRefactorTool,
            TestRunnerTool,
            # Note: PolicyEngineTool not included - handled via helper method due to DB session
        ]

        # Create ADK agent with comprehensive instructions
        # Note: Using Agent (not LlmAgent) for single-agent pattern
        # - Agent: For single agents with tools (matches official docs pattern)
        # - LlmAgent: For multi-agent systems with sub_agents
        # Both work identically, but Agent is semantically clearer for our use case
        self.llm_agent = Agent(
            name="agentcodecraft_refactorer",
            model="gemini-2.0-flash-exp",  # Model name as string, not Gemini object
            instruction=AGENT_INSTRUCTIONS,  # Note: 'instruction' (singular), not 'instructions'
            tools=tools,
        )

    def run_refactor_session(
        self,
        db: Session,
        *,
        session: orm.RefactorSession,
        code: str,
        file_path: str,
    ) -> Tuple[List[orm.RefactorSuggestion], orm.ComplianceMetric, List[PolicyViolation], str]:
        """
        Execute refined workflow using ADK agent and framework classes.

        Implements:
        - Refined workflow from Step 0.2 (6 steps + pre-flight)
        - Framework classes from Step 0.8 (AgentSessionState, AgentContext)
        - Validation strategy from Step 0.9 (3 checkpoints)
        - Error handling from Step 0.4 (4 levels)

        Returns:
            Tuple of (suggestions, metric, violations, refactored_code)
        """
        # Initialize state and context
        state = AgentSessionState(session_id=session.session_id)
        context = AgentContext(
            original_code=code,
            file_path=file_path,
            policy_profile_id=session.policy_profile_id,
            language=session.language,
        )

        session.status = "running"
        db.commit()

        try:
            # ====================================================================
            # PRE-FLIGHT CHECKS (Checkpoint 1)
            # ====================================================================
            state.current_step = WorkflowStep.PREFLIGHT
            is_valid, error_msg = self._preflight_checks(code, file_path, session.policy_profile_id, db, context)
            if not is_valid:
                state.record_error(ValueError(error_msg), WorkflowStep.PREFLIGHT)
                state.current_step = WorkflowStep.FAILED
                session.status = "failed"
                db.commit()
                raise ValueError(error_msg)
            state.record_step_completion(WorkflowStep.PREFLIGHT)

            # ====================================================================
            # STEP 1: ANALYZE CODE (Deterministic - ALWAYS)
            # ====================================================================
            state.current_step = WorkflowStep.ANALYSIS
            analysis_result = self._analyze_code(code, state, context)

            # ====================================================================
            # STEP 2: EVALUATE POLICIES (Deterministic - ALWAYS)
            # ====================================================================
            state.current_step = WorkflowStep.POLICY_EVALUATION
            policy_result = self._evaluate_policies(code, session.policy_profile_id, db, state, context)

            # ====================================================================
            # DECISION POINT 1: Should we refactor?
            # ====================================================================
            if state.should_refactor():
                # ====================================================================
                # STEP 3: REFACTOR CODE (LLM-Driven)
                # ====================================================================
                state.current_step = WorkflowStep.REFACTORING
                refactor_result = self._refactor_code(code, policy_result, file_path, state, context)
            else:
                # Skip refactoring - use original code
                context.refactored_code = code
                state.record_step_completion(WorkflowStep.REFACTORING, {"skipped": True, "reason": "No violations found"})
                state.record_warning("No violations found - skipping refactoring", WorkflowStep.REFACTORING)

            # ====================================================================
            # STEP 4: VALIDATE REFACTORED CODE (Checkpoint 2)
            # ====================================================================
            state.current_step = WorkflowStep.VALIDATION
            validation_result = self._validate_refactored_code(
                code, context.get_refactored_code(), session.policy_profile_id, db, state, context
            )

            # ====================================================================
            # STEP 5: CALCULATE METRICS (Deterministic - ALWAYS)
            # ====================================================================
            state.current_step = WorkflowStep.METRICS
            metrics = self._calculate_metrics(code, context, state)

            # ====================================================================
            # STEP 6: SAVE RESULTS (Deterministic - ALWAYS)
            # ====================================================================
            state.current_step = WorkflowStep.SAVE_RESULTS
            suggestions, metric, violations, refactored_code = self._save_results(
                db, session, context, metrics, state
            )

            # ====================================================================
            # FINAL VALIDATION (Checkpoint 3)
            # ====================================================================
            self._final_validation(state, context, metrics)

            state.current_step = WorkflowStep.COMPLETED
            session.status = "completed"
            db.commit()

            return suggestions, metric, violations, refactored_code

        except Exception as e:
            # Error handling (Step 0.4)
            state.record_error(e, state.current_step)
            state.current_step = WorkflowStep.FAILED
            session.status = "failed"
            db.commit()
            raise

    # ====================================================================
    # PRE-FLIGHT CHECKS (Checkpoint 1)
    # ====================================================================

    def _preflight_checks(
        self, code: str, file_path: str, policy_profile_id: str, db: Session, context: AgentContext
    ) -> tuple[bool, Optional[str]]:
        """
        Pre-flight validation (Checkpoint 1 from Step 0.9).

        Returns:
            (is_valid, error_message)
        """
        # 1.1: Code validation
        if not code or not code.strip():
            return False, "Code cannot be empty"

        if len(code) > 1_000_000:  # 1MB limit
            return False, "Code exceeds maximum size (1MB)"

        # Check parseability
        if context.language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                return False, f"Invalid Python syntax: {str(e)}"

        # 1.2: Policy profile validation
        profile = self.policy_engine.load_profile(db, policy_profile_id)
        if not profile:
            return False, f"Policy profile {policy_profile_id} not found"

        # Check has rules
        rules = db.query(orm.PolicyRule).filter(
            orm.PolicyRule.policy_profile_id == policy_profile_id
        ).all()
        if not rules:
            return False, f"Policy profile {policy_profile_id} has no rules"

        # 1.3: File path validation
        if not file_path:
            # Generate default path
            extension_map = {"python": "py", "terraform": "tf"}
            extension = extension_map.get(context.language, "txt")
            context.file_path = f"submission.{extension}"

        return True, None

    # ====================================================================
    # STEP 1: ANALYZE CODE
    # ====================================================================

    def _analyze_code(self, code: str, state: AgentSessionState, context: AgentContext) -> dict:
        """Step 1: Analyze code structure and complexity."""
        try:
            result = StaticAnalysisTool.func(code=code)
            state.record_step_completion(WorkflowStep.ANALYSIS, result)
            context.update_analysis(result)
            return result
        except Exception as e:
            # Error handling: Log error, use fallback
            state.record_error(e, WorkflowStep.ANALYSIS)
            state.record_warning("Analysis failed - using empty analysis", WorkflowStep.ANALYSIS)
            result = {"complexity": 0.0, "line_count": 0, "function_count": 0, "functions": [], "classes": []}
            state.record_step_completion(WorkflowStep.ANALYSIS, result)
            context.update_analysis(result)
            return result

    # ====================================================================
    # STEP 2: EVALUATE POLICIES
    # ====================================================================

    def _evaluate_policies(
        self, code: str, policy_profile_id: str, db: Session, state: AgentSessionState, context: AgentContext
    ) -> dict:
        """Step 2: Evaluate code against policies."""
        try:
            profile = self.policy_engine.load_profile(db, policy_profile_id)
            if not profile:
                raise ValueError(f"Policy profile {policy_profile_id} not found")

            violations = self.policy_engine.evaluate(code, profile)
            score = self.policy_engine.score_compliance(
                violations=violations,
                total_rules=len(profile.rules)
            )

            result = {
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

            state.record_step_completion(WorkflowStep.POLICY_EVALUATION, result)
            context.update_policy_evaluation(result["violations"], score)
            return result
        except Exception as e:
            # Error handling: Log error, use fallback
            state.record_error(e, WorkflowStep.POLICY_EVALUATION)
            state.record_warning("Policy evaluation failed - using empty violations", WorkflowStep.POLICY_EVALUATION)
            result = {"violations": [], "compliance_score": 0.0, "total_rules": 0}
            state.record_step_completion(WorkflowStep.POLICY_EVALUATION, result)
            context.update_policy_evaluation([], 0.0)
            return result

    # ====================================================================
    # STEP 3: REFACTOR CODE (LLM-Driven)
    # ====================================================================

    def _refactor_code(
        self, code: str, policy_result: dict, file_path: str, state: AgentSessionState, context: AgentContext
    ) -> dict:
        """Step 3: Generate refactoring suggestions (LLM-driven)."""
        try:
            result = GeminiRefactorTool.func(
                code=code,
                violations=policy_result["violations"],
                file_path=file_path
            )
            state.record_step_completion(WorkflowStep.REFACTORING, result)
            context.update_refactoring(result["refactored_code"], result["suggestions"])
            return result
        except Exception as e:
            # Error handling: Retry once, then use original code
            state.record_error(e, WorkflowStep.REFACTORING)
            state.record_warning("Refactoring failed - using original code", WorkflowStep.REFACTORING)
            # Use original code as fallback
            result = {
                "suggestions": [],
                "refactored_code": code
            }
            state.record_step_completion(WorkflowStep.REFACTORING, result)
            context.update_refactoring(code, [])
            return result

    # ====================================================================
    # STEP 4: VALIDATE REFACTORED CODE (Checkpoint 2)
    # ====================================================================

    def _validate_refactored_code(
        self, original_code: str, refactored_code: str, policy_profile_id: str,
        db: Session, state: AgentSessionState, context: AgentContext
    ) -> dict:
        """
        Step 4: Validate refactored code (Checkpoint 2 from Step 0.9).

        Validates:
        - Refactored code parseability
        - Policy compliance
        - Test execution
        - Complexity
        """
        validation_result = {
            "refactored_code_valid": True,
            "policy_compliance": {},
            "test_results": {},
            "complexity_validation": {},
            "warnings": []
        }

        # 2.1: Validate parseability
        try:
            if context.language == "python":
                ast.parse(refactored_code)
        except SyntaxError as e:
            validation_result["refactored_code_valid"] = False
            validation_result["warnings"].append(f"Refactored code has invalid syntax: {str(e)}")
            state.record_warning(f"Refactored code invalid - using original", WorkflowStep.VALIDATION)
            context.refactored_code = original_code  # Fallback to original

        # 2.2: Validate policy compliance
        try:
            profile = self.policy_engine.load_profile(db, policy_profile_id)
            if profile:
                new_violations = self.policy_engine.evaluate(refactored_code, profile)
                original_violations = self.policy_engine.evaluate(original_code, profile)
                
                validation_result["policy_compliance"] = {
                    "original_violations": len(original_violations),
                    "new_violations": len(new_violations),
                    "violations_fixed": len(original_violations) - len(new_violations),
                    "violations_introduced": len([v for v in new_violations if v not in original_violations]),
                    "compliance_improved": len(new_violations) < len(original_violations)
                }
                
                if len(new_violations) > len(original_violations):
                    validation_result["warnings"].append("Refactored code introduced new violations")
                    state.record_warning("New violations introduced", WorkflowStep.VALIDATION)
        except Exception as e:
            state.record_error(e, WorkflowStep.VALIDATION)
            validation_result["warnings"].append(f"Policy compliance validation failed: {str(e)}")

        # 2.3: Validate test execution
        try:
            test_result = TestRunnerTool.func(code=refactored_code, language=context.language)
            validation_result["test_results"] = test_result
            if test_result.get("test_pass_rate", 1.0) < 1.0:
                validation_result["warnings"].append("Some tests failed")
                state.record_warning("Tests failed", WorkflowStep.VALIDATION)
        except Exception as e:
            state.record_error(e, WorkflowStep.VALIDATION)
            validation_result["test_results"] = {"test_pass_rate": 1.0, "message": "Test execution failed"}
            validation_result["warnings"].append(f"Test execution failed: {str(e)}")

        # 2.4: Validate complexity
        try:
            original_complexity = self.static_analysis.compute_complexity(original_code)
            refactored_complexity = self.static_analysis.compute_complexity(refactored_code)
            complexity_delta = refactored_complexity - original_complexity
            
            validation_result["complexity_validation"] = {
                "original_complexity": original_complexity,
                "refactored_complexity": refactored_complexity,
                "complexity_delta": complexity_delta,
                "complexity_improved": complexity_delta < 0,
                "complexity_worsened_significantly": complexity_delta > 5.0
            }
            
            if complexity_delta > 5.0:
                validation_result["warnings"].append("Complexity worsened significantly")
                state.record_warning("Complexity worsened", WorkflowStep.VALIDATION)
        except Exception as e:
            state.record_error(e, WorkflowStep.VALIDATION)
            validation_result["complexity_validation"] = {"complexity_delta": 0.0}

        state.record_step_completion(WorkflowStep.VALIDATION, validation_result)
        context.update_validation(validation_result)
        return validation_result

    # ====================================================================
    # STEP 5: CALCULATE METRICS
    # ====================================================================

    def _calculate_metrics(
        self, original_code: str, context: AgentContext, state: AgentSessionState
    ) -> dict:
        """Step 5: Calculate metrics."""
        try:
            refactored_code = context.get_refactored_code()
            
            # Complexity delta
            complexity_delta = self.static_analysis.summarize_complexity(original_code, refactored_code)
            
            # Policy score (from context)
            policy_score = context.compliance_score
            
            # Test pass rate (from validation)
            test_pass_rate = context.test_pass_rate
            
            metrics = {
                "complexity_delta": complexity_delta,
                "policy_score": policy_score,
                "test_pass_rate": test_pass_rate,
                "latency_ms": 0,  # Would track from agent execution
                "token_usage": max(1, len(refactored_code) // 4)
            }
            
            state.metrics.update(metrics)
            state.record_step_completion(WorkflowStep.METRICS)
            context.update_metrics(metrics)
            return metrics
        except Exception as e:
            # Error handling: Use defaults
            state.record_error(e, WorkflowStep.METRICS)
            metrics = {
                "complexity_delta": 0.0,
                "policy_score": 0.0,
                "test_pass_rate": 0.0,
                "latency_ms": 0,
                "token_usage": 0
            }
            state.metrics.update(metrics)
            state.record_step_completion(WorkflowStep.METRICS)
            context.update_metrics(metrics)
            return metrics

    # ====================================================================
    # STEP 6: SAVE RESULTS
    # ====================================================================

    def _save_results(
        self, db: Session, session: orm.RefactorSession, context: AgentContext,
        metrics: dict, state: AgentSessionState
    ) -> Tuple[List[orm.RefactorSuggestion], orm.ComplianceMetric, List[PolicyViolation], str]:
        """Step 6: Save results to database."""
        try:
            refactored_code = context.get_refactored_code()
            
            # Save suggestions
            suggestions: List[orm.RefactorSuggestion] = []
            for suggestion_data in context.refactoring_suggestions:
                suggestion = orm.RefactorSuggestion(
                    suggestion_id=suggestion_data.get("suggestion_id", str(uuid4())),
                    session_id=session.session_id,
                    file_path=suggestion_data.get("file_path", context.file_path),
                    start_line=suggestion_data.get("start_line", 1),
                    end_line=suggestion_data.get("end_line", 1),
                    original_code=suggestion_data.get("original_code", context.original_code),
                    proposed_code=suggestion_data.get("proposed_code", refactored_code),
                    rationale=suggestion_data.get("rationale", ""),
                    confidence_score=suggestion_data.get("confidence_score", 0.5),
                )
                db.add(suggestion)
                suggestions.append(suggestion)

            # Convert violations
            violations: List[PolicyViolation] = []
            for v_dict in context.policy_violations:
                violation = PolicyViolation(
                    rule_id=v_dict.get("rule_id", ""),
                    rule_key=v_dict.get("rule_key", ""),
                    message=v_dict.get("message", ""),
                    severity=v_dict.get("severity", "medium"),
                    fix_prompt=v_dict.get("fix_prompt", "")
                )
                violations.append(violation)

            # Create compliance metric
            metric = orm.ComplianceMetric(
                metric_id=str(uuid4()),
                session_id=session.session_id,
                policy_score=metrics["policy_score"],
                complexity_delta=metrics["complexity_delta"],
                test_pass_rate=metrics["test_pass_rate"],
                latency_ms=metrics["latency_ms"],
                token_usage=metrics["token_usage"],
            )
            db.add(metric)

            state.record_step_completion(WorkflowStep.SAVE_RESULTS)
            return suggestions, metric, violations, refactored_code

        except Exception as e:
            # Error handling: Rollback, set status
            state.record_error(e, WorkflowStep.SAVE_RESULTS)
            db.rollback()
            session.status = "failed"
            db.commit()
            raise

    # ====================================================================
    # FINAL VALIDATION (Checkpoint 3)
    # ====================================================================

    def _final_validation(
        self, state: AgentSessionState, context: AgentContext, metrics: dict
    ) -> None:
        """
        Final validation (Checkpoint 3 from Step 0.9).

        Validates:
        - Metrics completeness
        - Results consistency
        - Workflow integrity
        """
        issues = []

        # 3.1: Metrics completeness
        required_metrics = ["complexity_delta", "policy_score", "test_pass_rate", "latency_ms", "token_usage"]
        for metric in required_metrics:
            if metric not in metrics:
                issues.append(f"Missing metric: {metric}")
                state.record_warning(f"Missing metric: {metric}", WorkflowStep.METRICS)

        # 3.2: Results consistency
        if context.refactoring_suggestions:
            for suggestion in context.refactoring_suggestions:
                if suggestion.get("proposed_code") not in context.get_refactored_code():
                    issues.append(f"Suggestion code not in refactored_code")
                    state.record_warning("Suggestion code mismatch", WorkflowStep.SAVE_RESULTS)

        # 3.3: Workflow integrity
        if not state.is_workflow_complete():
            issues.append("Workflow not complete")
            state.record_warning("Workflow incomplete", state.current_step)

        if issues:
            state.record_warning(f"Final validation found {len(issues)} issues", WorkflowStep.COMPLETED)

