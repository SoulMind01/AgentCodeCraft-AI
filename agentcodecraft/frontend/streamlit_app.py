"""
Streamlit UI for AgentCodeCraft AI.
"""
from __future__ import annotations

import os
from typing import Any, Dict

import requests
import streamlit as st

API_BASE = os.getenv("AGENTCODECRAFT_API", "http://localhost:8000")


def fetch_policies() -> list[dict[str, Any]]:
    response = requests.get(f"{API_BASE}/policies", timeout=10)
    response.raise_for_status()
    return response.json()


def submit_refactor(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_BASE}/refactor", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def upload_policy(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_BASE}/policies/import", json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def render_refactor_workspace():
    st.header("Refactor Workspace")
    policies = fetch_policies()
    if not policies:
        st.warning("No policy profiles are available. Please import one first.")
        return

    policy_names = {f"{p['name']} ({p['domain']})": p for p in policies}
    selected_policy = st.selectbox("Policy Profile", list(policy_names.keys()))
    code = st.text_area("Code Snippet", height=300, placeholder="Paste Python or Terraform code here...")
    repo = st.text_input("Repository (optional)")
    branch = st.text_input("Branch (optional)")
    file_path = st.text_input("File Path", value="submission.py")
    user_id = st.text_input("User ID", value="developer-1")
    user_name = st.text_input("User Name", value="Demo Developer")
    language = st.selectbox("Language", ["python", "terraform"])

    if st.button("Run Policy-Aware Refactor", type="primary"):
        if not code.strip():
            st.warning("Please provide code to analyze.")
            return
        try:
            payload = {
                "user_id": user_id,
                "user_name": user_name,
                "code": code,
                "language": language,
                "policy_profile_id": policy_names[selected_policy]["policy_profile_id"],
                "repo": repo or None,
                "branch": branch or None,
                "file_path": file_path or None,
            }
            result = submit_refactor(payload)
            st.success("Refactor completed.")
            st.subheader("Compliance Summary")
            st.json(result["compliance"])

            st.subheader("Code Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Original")
                st.code(result["original_code"], language=language)
            with col2:
                st.caption("Refactored")
                st.code(result["refactored_code"], language=language)

            for suggestion in result["suggestions"]:
                st.subheader(f"Suggestion {suggestion['suggestion_id']}")
                st.code(suggestion["rationale"])
                st.write("Original:")
                st.code(suggestion["original_code"])
                st.write("Proposed:")
                st.code(suggestion["proposed_code"])
            if result["violations"]:
                st.error("Remaining Policy Violations:")
                st.json(result["violations"])
            else:
                st.info("No policy violations detected.")
        except requests.HTTPError as exc:
            st.error(f"Refactor request failed: {exc.response.text}")


def import_policy(name: str, domain: str, version: str, document: str):
    try:
        payload = {"name": name or None, "domain": domain or None, "version": version or None, "document": document}
        response = upload_policy(payload)
        st.success(f"Imported policy {response['name']} ({response['policy_profile_id']})")
    except requests.HTTPError as exc:
        st.error(f"Failed to import policy: {exc.response.text}")


def render_policy_studio():
    st.header("Policy Studio")
    name = st.text_input("Policy Name")
    domain = st.text_input("Domain", value="python")
    version = st.text_input("Version", value="1.0.0")
    document = st.text_area("Policy Document (YAML/JSON)", height=250)

    if st.button("Import Policy Profile"):
        if not bool(document):
            st.warning("Please provide a policy document.")
        else:
            import_policy(name, domain, version, document)

    st.subheader("Available Profiles")
    try:
        policies = fetch_policies()
        for profile in policies:
            st.write(f"**{profile['name']}** — {profile['domain']} (v{profile['version']})")
            with st.expander("Rules"):
                st.json(profile["rules"])
    except requests.HTTPError:
        st.info("Unable to load policy profiles.")


def main():
    st.set_page_config(page_title="AgentCodeCraft AI", layout="wide")
    view = st.sidebar.radio("View", ["Refactor Workspace", "Policy Studio"])
    if view == "Refactor Workspace":
        render_refactor_workspace()
    else:
        render_policy_studio()


if __name__ == "__main__":
    main()


