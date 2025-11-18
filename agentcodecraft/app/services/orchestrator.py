"""
AgentCodeCraft orchestrator handling refactor sessions.
"""
from __future__ import annotations

import time
from typing import List, Tuple
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import orm
from app.services.gemini_adapter import GeminiAdapter, RefactorResult
from app.services.policy_engine import PolicyEngine, PolicyViolation
from app.services.static_analysis import StaticAnalysisService


class AgentCodeCraftApp:
    """Coordinates refactoring, policy checks, and metrics collection."""

    def __init__(
        self,
        *,
        adapter: GeminiAdapter,
        policy_engine: PolicyEngine,
        static_analysis: StaticAnalysisService,
    ):
        self.adapter = adapter
        self.policy_engine = policy_engine
        self.static_analysis = static_analysis

    def run_refactor_session(
        self,
        db: Session,
        *,
        session: orm.RefactorSession,
        code: str,
        ast_summary: str | None = None,
        file_path: str,
    ) -> Tuple[List[orm.RefactorSuggestion], orm.ComplianceMetric, List[PolicyViolation], str]:
        """Execute the end-to-end refactoring flow for a session."""
        session.status = "running"
        db.commit()

        policy_profile = self.policy_engine.load_profile(db, session.policy_profile_id)
        if not policy_profile:
            raise ValueError(f"Policy profile {session.policy_profile_id} not found.")

        start_time = time.perf_counter()
        adapter_result: RefactorResult = self.adapter.generate_refactor(
            code=code, ast_summary=ast_summary, policies=policy_profile.rules, file_path=file_path
        )
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        suggestions: List[orm.RefactorSuggestion] = []
        for proposal in adapter_result.suggestions:
            suggestion = orm.RefactorSuggestion(
                suggestion_id=proposal.suggestion_id,
                session_id=session.session_id,
                file_path=proposal.file_path,
                start_line=proposal.start_line,
                end_line=proposal.end_line,
                original_code=proposal.original_code,
                proposed_code=proposal.proposed_code,
                rationale=proposal.rationale,
                confidence_score=proposal.confidence_score,
            )
            db.add(suggestion)
            suggestions.append(suggestion)

        policy_violations = self.policy_engine.evaluate(adapter_result.refactored_code, policy_profile)

        complexity_delta = self.static_analysis.summarize_complexity(code, adapter_result.refactored_code)
        policy_score = self.policy_engine.score_compliance(
            violations=policy_violations, total_rules=len(policy_profile.rules)
        )
        test_pass_rate = self.static_analysis.run_tests(session)
        token_usage = max(1, len(adapter_result.refactored_code) // 4)

        metric = orm.ComplianceMetric(
            metric_id=str(uuid4()),
            session_id=session.session_id,
            policy_score=policy_score,
            complexity_delta=complexity_delta,
            test_pass_rate=test_pass_rate,
            latency_ms=latency_ms,
            token_usage=token_usage,
        )
        db.add(metric)

        session.status = "completed"
        db.commit()

        for suggestion in suggestions:
            db.refresh(suggestion)
        db.refresh(metric)
        db.refresh(session)

        return suggestions, metric, policy_violations, adapter_result.refactored_code


