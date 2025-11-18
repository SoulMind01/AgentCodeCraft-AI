"""
Session retrieval routes.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.domain import (
    ComplianceMetricModel,
    RefactorSessionModel,
    RefactorSuggestionModel,
)
from app.models import orm

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}", response_model=RefactorSessionModel)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Return a session with its suggestions and metrics."""
    session = (
        db.query(orm.RefactorSession)
        .filter(orm.RefactorSession.session_id == session_id)
        .one_or_none()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    return RefactorSessionModel(
        session_id=session.session_id,
        user_id=session.user_id,
        repo=session.repo,
        branch=session.branch,
        language=session.language,
        policy_profile_id=session.policy_profile_id,
        created_at=session.created_at,
        status=session.status,
        suggestions=[
            RefactorSuggestionModel(
                suggestion_id=s.suggestion_id,
                session_id=s.session_id,
                file_path=s.file_path,
                start_line=s.start_line,
                end_line=s.end_line,
                original_code=s.original_code,
                proposed_code=s.proposed_code,
                rationale=s.rationale,
                confidence_score=s.confidence_score,
            )
            for s in session.suggestions
        ],
        metrics=ComplianceMetricModel(
            metric_id=session.metrics.metric_id,
            session_id=session.metrics.session_id,
            policy_score=session.metrics.policy_score,
            complexity_delta=session.metrics.complexity_delta,
            test_pass_rate=session.metrics.test_pass_rate,
            latency_ms=session.metrics.latency_ms,
            token_usage=session.metrics.token_usage,
        )
        if session.metrics
        else None,
    )


