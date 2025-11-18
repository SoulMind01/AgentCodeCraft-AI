"""
Refactor-related API routes.
"""
from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_agent_app, get_db
from app.models.domain import RefactorRequest, RefactorResponse, RefactorSessionModel, RefactorSuggestionModel, ComplianceMetricModel
from app.models import orm
from app.services.orchestrator import AgentCodeCraftApp

router = APIRouter(prefix="/refactor", tags=["refactor"])


def _ensure_user(db: Session, payload: RefactorRequest) -> orm.User:
    user = db.query(orm.User).filter(orm.User.user_id == payload.user_id).one_or_none()
    if user:
        if payload.user_name:
            user.name = payload.user_name
        if payload.role:
            user.role = payload.role
        if payload.organization:
            user.organization = payload.organization
        db.commit()
        db.refresh(user)
        return user

    user = orm.User(
        user_id=payload.user_id,
        name=payload.user_name,
        role=payload.role,
        organization=payload.organization,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _policy_exists(db: Session, policy_profile_id: str) -> bool:
    return (
        db.query(orm.PolicyProfile)
        .filter(orm.PolicyProfile.policy_profile_id == policy_profile_id)
        .one_or_none()
        is not None
    )


@router.post("", response_model=RefactorResponse, status_code=status.HTTP_201_CREATED)
def run_refactor(
    payload: RefactorRequest,
    db: Session = Depends(get_db),
    agent_app: AgentCodeCraftApp = Depends(get_agent_app),
):
    """Trigger a policy-aware refactoring session."""
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    _ensure_user(db, payload)
    if not _policy_exists(db, payload.policy_profile_id):
        raise HTTPException(status_code=404, detail="Policy profile not found.")

    session = orm.RefactorSession(
        session_id=str(uuid4()),
        user_id=payload.user_id,
        repo=payload.repo,
        branch=payload.branch,
        language=payload.language,
        policy_profile_id=payload.policy_profile_id,
        status="pending",
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    suggestions, metric, violations, refactored_code = agent_app.run_refactor_session(
        db,
        session=session,
        code=payload.code,
        ast_summary=None,
        file_path=payload.file_path or f"submission.{payload.language}",
    )

    response = RefactorResponse(
        session=RefactorSessionModel(
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
                for s in suggestions
            ],
        ),
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
            for s in suggestions
        ],
        compliance=ComplianceMetricModel(
            metric_id=metric.metric_id,
            session_id=metric.session_id,
            policy_score=metric.policy_score,
            complexity_delta=metric.complexity_delta,
            test_pass_rate=metric.test_pass_rate,
            latency_ms=metric.latency_ms,
            token_usage=metric.token_usage,
        ),
        violations=[violation.__dict__ for violation in violations],
        original_code=payload.code,
        refactored_code=refactored_code,
    )
    response.session.metrics = response.compliance
    return response


