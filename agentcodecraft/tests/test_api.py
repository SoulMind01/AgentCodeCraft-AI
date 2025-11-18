from fastapi.testclient import TestClient

from app.main import app
from app.db import init_db


client = TestClient(app)
init_db()


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "AgentCodeCraft backend is running"


def test_refactor_flow():
    policy_doc = """
profile:
  name: Demo Policy
  domain: python
  version: 1.0.0
rules:
  - rule_key: no-tabs
    description: Tabs are not allowed
    category: style
    expression: "\\t"
    severity: medium
    auto_fixable: true
"""
    policy_resp = client.post(
        "/policies/import",
        json={"document": policy_doc, "name": "Demo Policy", "domain": "python", "version": "1.0.0"},
    )
    assert policy_resp.status_code == 201
    policy_id = policy_resp.json()["policy_profile_id"]

    refactor_resp = client.post(
        "/refactor",
        json={
            "user_id": "tester",
            "user_name": "Tester",
            "code": "def foo():\n    return 42\n",
            "language": "python",
            "policy_profile_id": policy_id,
            "file_path": "foo.py",
        },
    )
    assert refactor_resp.status_code == 201, refactor_resp.text
    payload = refactor_resp.json()
    assert payload["compliance"]["policy_score"] >= 0
    assert payload["session"]["status"] == "completed"
    assert payload["original_code"] == "def foo():\n    return 42\n"
    assert isinstance(payload["refactored_code"], str)


