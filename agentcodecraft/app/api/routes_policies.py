"""
Policy management routes.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_agent_app, get_db
from app.models.domain import PolicyImportRequest, PolicyProfileModel, PolicyRuleModel
from app.models import orm
from app.services.orchestrator import AgentCodeCraftApp

router = APIRouter(prefix="/policies", tags=["policies"])


def _to_profile_model(profile: orm.PolicyProfile) -> PolicyProfileModel:
    return PolicyProfileModel(
        policy_profile_id=profile.policy_profile_id,
        name=profile.name,
        domain=profile.domain,
        version=profile.version,
        created_at=profile.created_at,
        rules=[
            PolicyRuleModel(
                rule_id=rule.rule_id,
                policy_profile_id=rule.policy_profile_id,
                rule_key=rule.rule_key,
                description=rule.description,
                category=rule.category,
                expression=rule.expression,
                severity=rule.severity,
                auto_fixable=rule.auto_fixable,
            )
            for rule in profile.rules
        ],
    )


@router.get("", response_model=List[PolicyProfileModel])
def list_policies(db: Session = Depends(get_db)):
    """Return all available policy profiles."""
    profiles = db.query(orm.PolicyProfile).all()
    return [_to_profile_model(profile) for profile in profiles]


@router.post("/import", response_model=PolicyProfileModel, status_code=status.HTTP_201_CREATED)
def import_policy(
    payload: PolicyImportRequest,
    db: Session = Depends(get_db),
    agent_app: AgentCodeCraftApp = Depends(get_agent_app),
):
    """Import a policy profile from YAML/JSON document."""
    try:
        profile = agent_app.policy_engine.import_policy_profile(
            db,
            document=payload.document,
            overrides={
                "name": payload.name,
                "domain": payload.domain,
                "version": payload.version,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _to_profile_model(profile)


