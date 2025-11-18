"""
Policy ingestion and evaluation service.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Sequence
from uuid import uuid4

import yaml
from sqlalchemy.orm import Session

from app.models import orm


@dataclass
class PolicyViolation:
    rule_id: str
    rule_key: str
    message: str
    severity: str


class PolicyEngine:
    """Loads policy profiles and evaluates code compliance."""

    def load_profile(self, db: Session, profile_id: str) -> orm.PolicyProfile | None:
        """Return a PolicyProfile by ID."""
        return db.query(orm.PolicyProfile).filter(orm.PolicyProfile.policy_profile_id == profile_id).one_or_none()

    def parse_policy_document(self, document: str) -> Dict:
        """Parse YAML/JSON content into a dictionary."""
        try:
            return yaml.safe_load(document) if not document.strip().startswith("{") else json.loads(document)
        except (yaml.YAMLError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid policy document: {exc}") from exc

    def import_policy_profile(
        self,
        db: Session,
        *,
        document: str,
        overrides: Dict | None = None,
    ) -> orm.PolicyProfile:
        """Create a PolicyProfile and associated rules from a document."""
        overrides = overrides or {}
        payload = self.parse_policy_document(document)
        profile_data = payload.get("profile", {})
        rules_data = payload.get("rules", [])
        policy_profile_id = profile_data.get("policy_profile_id") or str(uuid4())

        profile = orm.PolicyProfile(
            policy_profile_id=policy_profile_id,
            name=overrides.get("name") or profile_data.get("name") or "Unnamed Policy",
            domain=overrides.get("domain") or profile_data.get("domain") or "general",
            version=overrides.get("version") or profile_data.get("version") or "1.0.0",
            created_at=datetime.utcnow(),
        )

        for rule in rules_data:
            rule_key = rule.get("rule_key") or rule.get("key")
            if not rule_key:
                raise ValueError("Each policy rule must include 'rule_key' or 'key'.")
            rule_obj = orm.PolicyRule(
                rule_id=rule.get("rule_id") or str(uuid4()),
                policy_profile_id=policy_profile_id,
                rule_key=rule_key,
                description=rule.get("description", "No description provided"),
                category=rule.get("category", "style"),
                expression=str(rule.get("expression", "")),
                severity=rule.get("severity", "medium"),
                auto_fixable=bool(rule.get("auto_fixable", False)),
            )
            profile.rules.append(rule_obj)

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    def evaluate(self, code_snapshot: str, policy_profile: orm.PolicyProfile) -> List[PolicyViolation]:
        """
        Check the given code against each policy rule.

        The current heuristic treats each rule expression as a regex that should NOT match.
        If a match is found, the rule is considered violated.
        """
        violations: List[PolicyViolation] = []
        for rule in policy_profile.rules:
            pattern = rule.expression
            if not pattern:
                continue
            try:
                if re.search(pattern, code_snapshot, re.MULTILINE):
                    violations.append(
                        PolicyViolation(
                            rule_id=rule.rule_id,
                            rule_key=rule.rule_key,
                            message=rule.description,
                            severity=rule.severity,
                        )
                    )
            except re.error:
                violations.append(
                    PolicyViolation(
                        rule_id=rule.rule_id,
                        rule_key=rule.rule_key,
                        message=f"Invalid regex: {pattern}",
                        severity="high",
                    )
                )
        return violations

    def score_compliance(self, *, violations: Sequence[PolicyViolation], total_rules: int) -> float:
        """Return a compliance score between 0 and 100."""
        if total_rules <= 0:
            return 100.0
        score = max(0.0, 100.0 - (len(list(violations)) / total_rules) * 100.0)
        return round(score, 2)


