"""
Agent framework classes for state and context management.

This module provides the core framework classes for tracking agent execution state
and maintaining context across workflow steps.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class WorkflowStep(Enum):
    """Workflow step enumeration."""
    INITIALIZED = "initialized"
    PREFLIGHT = "preflight"
    ANALYSIS = "analysis"
    POLICY_EVALUATION = "policy_evaluation"
    REFACTORING = "refactoring"
    VALIDATION = "validation"
    METRICS = "metrics"
    SAVE_RESULTS = "save_results"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentSessionState:
    """Track agent execution state for a session (refined to match workflow)."""
    session_id: str
    current_step: WorkflowStep = WorkflowStep.INITIALIZED
    
    # Step completion flags (matches refined workflow)
    preflight_complete: bool = False
    analysis_complete: bool = False
    policy_evaluation_complete: bool = False
    refactoring_complete: bool = False
    validation_complete: bool = False
    metrics_complete: bool = False
    save_complete: bool = False
    
    # Tool results (keyed by step name)
    tool_results: Dict[str, dict] = field(default_factory=dict)
    
    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def record_step_completion(self, step: WorkflowStep, result: dict = None):
        """Record step completion."""
        self.current_step = step
        if step == WorkflowStep.PREFLIGHT:
            self.preflight_complete = True
        elif step == WorkflowStep.ANALYSIS:
            self.analysis_complete = True
            self.tool_results["analysis"] = result or {}
        elif step == WorkflowStep.POLICY_EVALUATION:
            self.policy_evaluation_complete = True
            self.tool_results["policy_evaluation"] = result or {}
        elif step == WorkflowStep.REFACTORING:
            self.refactoring_complete = True
            self.tool_results["refactoring"] = result or {}
        elif step == WorkflowStep.VALIDATION:
            self.validation_complete = True
            self.tool_results["validation"] = result or {}
        elif step == WorkflowStep.METRICS:
            self.metrics_complete = True
        elif step == WorkflowStep.SAVE_RESULTS:
            self.save_complete = True
        elif step == WorkflowStep.COMPLETED:
            pass  # Final state
        elif step == WorkflowStep.FAILED:
            pass  # Error state
    
    def record_error(self, error: Exception, step: WorkflowStep = None):
        """Record error with context."""
        error_msg = f"[{step.value if step else self.current_step.value}] {str(error)}"
        self.errors.append(error_msg)
    
    def record_warning(self, warning: str, step: WorkflowStep = None):
        """Record warning with context."""
        warning_msg = f"[{step.value if step else self.current_step.value}] {warning}"
        self.warnings.append(warning_msg)
    
    def is_workflow_complete(self) -> bool:
        """Check if workflow is complete."""
        return (
            self.preflight_complete and
            self.analysis_complete and
            self.policy_evaluation_complete and
            (self.refactoring_complete or not self.should_refactor()) and
            self.validation_complete and
            self.metrics_complete and
            self.save_complete
        )
    
    def should_refactor(self) -> bool:
        """Determine if refactoring should occur (Decision Point 1)."""
        violations = self.tool_results.get("policy_evaluation", {}).get("violations", [])
        force_refactor = self.metrics.get("force_refactor", False)
        return len(violations) > 0 or force_refactor


@dataclass
class AgentContext:
    """Maintain context across tool calls (refined to match workflow)."""
    # Original inputs
    original_code: str
    file_path: str
    policy_profile_id: str
    language: str = "python"
    
    # Step 1: Analysis results
    analysis_result: Optional[dict] = None
    
    # Step 2: Policy evaluation results
    policy_violations: List[dict] = field(default_factory=list)
    compliance_score: float = 0.0
    
    # Step 3: Refactoring results
    refactored_code: str = ""
    refactoring_suggestions: List[dict] = field(default_factory=list)
    
    # Step 4: Validation results
    validation_result: Optional[dict] = None
    new_violations: List[dict] = field(default_factory=list)
    test_pass_rate: float = 0.0
    
    # Step 5: Metrics
    complexity_delta: float = 0.0
    policy_score: float = 0.0
    final_metrics: dict = field(default_factory=dict)
    
    def update_analysis(self, result: dict):
        """Update after Step 1: Analysis."""
        self.analysis_result = result
    
    def update_policy_evaluation(self, violations: List[dict], score: float):
        """Update after Step 2: Policy Evaluation."""
        self.policy_violations = violations
        self.compliance_score = score
    
    def update_refactoring(self, refactored_code: str, suggestions: List[dict]):
        """Update after Step 3: Refactoring."""
        self.refactored_code = refactored_code
        self.refactoring_suggestions = suggestions
    
    def update_validation(self, result: dict):
        """Update after Step 4: Validation."""
        self.validation_result = result
        self.new_violations = result.get("new_violations", [])
        self.test_pass_rate = result.get("test_pass_rate", 0.0)
    
    def update_metrics(self, metrics: dict):
        """Update after Step 5: Metrics."""
        self.final_metrics = metrics
        self.complexity_delta = metrics.get("complexity_delta", 0.0)
        self.policy_score = metrics.get("policy_score", 0.0)
    
    def get_refactored_code(self) -> str:
        """Get refactored code, or original if not refactored."""
        return self.refactored_code if self.refactored_code else self.original_code

