from app.services.policy_engine import PolicyEngine, PolicyViolation
from app.models import orm
from app.db import SessionLocal, init_db


def test_policy_engine_detects_violation():
    engine = PolicyEngine()
    profile = orm.PolicyProfile(
        policy_profile_id="policy-1",
        name="Style",
        domain="python",
        version="1.0",
    )
    rule = orm.PolicyRule(
        rule_id="rule-1",
        policy_profile_id="policy-1",
        rule_key="no-tabs",
        description="Tabs are not allowed",
        category="style",
        expression=r"\t",
        severity="high",
        auto_fixable=True,
    )
    profile.rules.append(rule)

    violations = engine.evaluate("def foo():\n\tprint('tab')\n", profile)
    assert len(violations) == 1
    assert isinstance(violations[0], PolicyViolation)
    assert engine.score_compliance(violations=violations, total_rules=1) == 0.0


def test_policy_engine_scores_full_compliance():
    engine = PolicyEngine()
    profile = orm.PolicyProfile(
        policy_profile_id="policy-2",
        name="Style",
        domain="python",
        version="1.0",
    )
    rule = orm.PolicyRule(
        rule_id="rule-2",
        policy_profile_id="policy-2",
        rule_key="no-tabs",
        description="Tabs are not allowed",
        category="style",
        expression=r"\t",
        severity="high",
        auto_fixable=True,
    )
    profile.rules.append(rule)

    violations = engine.evaluate("def foo():\n    print('spaces')\n", profile)
    assert len(violations) == 0
    assert engine.score_compliance(violations=violations, total_rules=1) == 100.0


def test_import_policy_profile_accepts_key_field():
    init_db()
    db = SessionLocal()
    engine = PolicyEngine()
    document = """
profile:
  name: Example
  domain: python
  version: "1.0"
rules:
  - key: no_eval
    description: Avoid eval
    category: security
    expression: 'eval\\('
"""
    profile = None
    try:
        profile = engine.import_policy_profile(db, document=document)
        assert any(rule.rule_key == "no_eval" for rule in profile.rules)
    finally:
        if profile is not None:
            db.delete(profile)
            db.commit()
        db.close()


