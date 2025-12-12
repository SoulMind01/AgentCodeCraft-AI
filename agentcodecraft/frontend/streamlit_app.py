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
    # Increased timeout to 120 seconds for complex refactoring operations
    # Gemini API calls can take 30-60 seconds for large code files
    response = requests.post(f"{API_BASE}/refactor", json=payload, timeout=120)
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
            with st.spinner("🔄 Running policy-aware refactoring... This may take 30-60 seconds for complex code."):
                result = submit_refactor(payload)
            
            st.success("✅ Refactoring completed!")
            
            # ====================================================================
            # Workflow Status
            # ====================================================================
            st.subheader("Workflow Status")
            status = result.get("session", {}).get("status", "unknown")
            if status == "completed":
                st.success("✅ Workflow completed successfully")
                st.progress(1.0)
                st.caption("All workflow steps completed")
            elif status == "running":
                st.info("⏳ Workflow in progress...")
                st.progress(0.5)
            elif status == "failed":
                st.error("❌ Workflow failed")
                st.progress(0.0)
            else:
                st.warning(f"Status: {status}")
            
            st.divider()
            
            # ====================================================================
            # Compliance Summary - Visual Metrics Cards
            # ====================================================================
            st.subheader("Compliance Summary")
            compliance = result["compliance"]
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                score = compliance["policy_score"]
                color = "normal" if score >= 80 else "inverse" if score >= 50 else "off"
                st.metric("Policy Score", f"{score:.1f}%", delta_color=color)
            with col2:
                delta = compliance["complexity_delta"]
                delta_color = "inverse" if delta < 0 else "normal" if delta == 0 else "off"
                st.metric("Complexity Δ", f"{delta:+.2f}", delta_color=delta_color)
            with col3:
                rate = compliance["test_pass_rate"]
                rate_color = "normal" if rate >= 0.8 else "inverse" if rate >= 0.5 else "off"
                st.metric("Test Pass Rate", f"{rate:.0%}", delta_color=rate_color)
            with col4:
                st.metric("Latency", f"{compliance['latency_ms']}ms")
            with col5:
                st.metric("Tokens", f"{compliance['token_usage']}")
            
            # ====================================================================
            # Performance Metrics
            # ====================================================================
            with st.expander("📊 Performance Metrics", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Latency", f"{compliance['latency_ms']}ms")
                    st.caption("End-to-end execution time")
                with col2:
                    st.metric("Token Usage", f"{compliance['token_usage']}")
                    st.caption("LLM tokens consumed")
                with col3:
                    # Approximate cost (Flash pricing: $0.075 per 1M input, $0.30 per 1M output)
                    # Using average of input/output pricing
                    estimated_cost = (compliance['token_usage'] / 1_000_000) * 0.1875
                    st.metric("Est. Cost", f"${estimated_cost:.6f}")
                    st.caption("Using gemini-2.5-flash")
            
            st.divider()
            
            # ====================================================================
            # Code Comparison
            # ====================================================================
            st.subheader("Code Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Original")
                st.code(result["original_code"], language=language)
            with col2:
                st.caption("Refactored")
                st.code(result["refactored_code"], language=language)
            
            st.divider()
            
            # ====================================================================
            # Suggestions with Confidence Scores
            # ====================================================================
            if result["suggestions"]:
                st.subheader(f"Refactoring Suggestions ({len(result['suggestions'])})")
                for idx, suggestion in enumerate(result["suggestions"]):
                    confidence = suggestion.get("confidence_score", 0.5)
                    with st.expander(f"💡 Suggestion {idx + 1} (Confidence: {confidence:.0%})"):
                        # Confidence visualization
                        st.progress(confidence, text=f"Confidence: {confidence:.0%}")
                        
                        st.write("**Rationale:**")
                        st.write(suggestion["rationale"])
                        
                        # Code comparison for suggestion
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption("Original")
                            st.code(suggestion["original_code"], language=language)
                        with col2:
                            st.caption("Proposed")
                            st.code(suggestion["proposed_code"], language=language)
            else:
                st.info("No refactoring suggestions generated.")
            
            st.divider()
            
            # ====================================================================
            # Enhanced Violations Display
            # ====================================================================
            if result["violations"]:
                # Count by severity
                high_violations = [v for v in result["violations"] if v.get("severity", "").lower() == "high"]
                medium_violations = [v for v in result["violations"] if v.get("severity", "").lower() == "medium"]
                low_violations = [v for v in result["violations"] if v.get("severity", "").lower() == "low"]
                unknown_violations = [v for v in result["violations"] 
                                    if v.get("severity", "").lower() not in ["high", "medium", "low"]]
                
                st.error(f"⚠️ {len(result['violations'])} Policy Violation(s) Detected")
                
                # Severity summary
                cols = st.columns(4)
                if high_violations:
                    cols[0].error(f"🔴 High: {len(high_violations)}")
                if medium_violations:
                    cols[1].warning(f"🟡 Medium: {len(medium_violations)}")
                if low_violations:
                    cols[2].info(f"🟢 Low: {len(low_violations)}")
                if unknown_violations:
                    cols[3].info(f"⚪ Unknown: {len(unknown_violations)}")
                
                # Detailed view in expander
                with st.expander("View All Violations", expanded=False):
                    for v in result["violations"]:
                        severity = v.get("severity", "medium").lower()
                        severity_icon = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(severity, "⚪")
                        
                        st.write(f"{severity_icon} **{v.get('rule_key', 'Unknown Rule')}** ({severity.upper()})")
                        st.caption(v.get('message', 'No description available'))
                        if v.get('fix_prompt'):
                            st.info(f"💡 Fix suggestion: {v.get('fix_prompt')}")
                        st.divider()
            else:
                st.success("✅ No policy violations detected")
        except requests.Timeout as exc:
            st.error("⏱️ Request Timeout")
            st.warning("The refactoring operation took too long (>120 seconds). This can happen with:")
            st.markdown("""
            - **Very large code files** (>500 lines)
            - **Many policy violations** (>20 violations)
            - **Slow network connection**
            - **Gemini API delays**
            
            **Suggestions:**
            - Try with smaller code snippets
            - Check your internet connection
            - Wait a moment and try again
            - Consider breaking large files into smaller chunks
            """)
            with st.expander("Technical Details"):
                st.code(str(exc))
        except requests.HTTPError as exc:
            status = exc.response.status_code
            if status == 400:
                st.error("❌ Validation Error")
                st.warning("Please check your code syntax and ensure the policy profile is valid.")
            elif status == 404:
                st.error("❌ Policy Profile Not Found")
                st.info("The selected policy profile may have been deleted or doesn't exist.")
            elif status == 429:
                st.error("⏱️ Rate Limit Exceeded")
                st.warning("Please wait a moment and try again. Free tier: 5 requests/minute.")
            elif status == 500:
                st.error("❌ Server Error")
                st.warning("An internal error occurred. Please try again later.")
            else:
                st.error(f"❌ Request Failed (Status: {status})")
            
            with st.expander("Technical Details"):
                try:
                    error_detail = exc.response.json()
                    st.json(error_detail)
                except:
                    st.code(exc.response.text)
        except requests.RequestException as exc:
            st.error("❌ Network Error")
            st.warning(f"Failed to connect to the backend API: {str(exc)}")
            st.info("Please ensure the backend server is running on http://localhost:8000")
            with st.expander("Technical Details"):
                st.code(str(exc))


def render_policy_studio():
    st.header("Policy Studio")
    name = st.text_input("Policy Name")
    domain = st.text_input("Domain", value="python")
    version = st.text_input("Version", value="1.0.0")
    document = st.text_area("Policy Document (YAML/JSON)", height=250)

    if st.button("Import Policy Profile"):
        try:
            payload = {"name": name or None, "domain": domain or None, "version": version or None, "document": document}
            response = upload_policy(payload)
            st.success(f"Imported policy {response['name']} ({response['policy_profile_id']})")
        except requests.HTTPError as exc:
            st.error(f"Failed to import policy: {exc.response.text}")

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


