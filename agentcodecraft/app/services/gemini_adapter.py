"""
Stubbed Gemini adapter that simulates refactoring suggestions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence
from uuid import uuid4

from app.models.orm import PolicyRule
from google import genai
from google.genai import types
import json


@dataclass
class RefactorProposal:
    """Represents a single refactoring suggestion."""

    suggestion_id: str
    file_path: str
    start_line: int
    end_line: int
    original_code: str
    proposed_code: str
    rationale: str
    confidence_score: float


@dataclass
class RefactorResult:
    """Container for adapter output."""

    suggestions: List[RefactorProposal]
    refactored_code: str


class GeminiAdapter:
    """
    Adapter layer responsible for interacting with Gemini/ADK.

    NOTE: This implementation is stubbed; all interactions are local and deterministic.
    Replace with real API calls once Gemini Pro 2.5 + ADK integration is available.
    """

    def generate_refactor(
        self, *, code: str, violate_policies: Sequence[PolicyRule], file_path: str
    ) -> RefactorResult:
        """
        Produce refactoring suggestions based on the provided code.

        This stub performs simple whitespace normalization to demonstrate the workflow.
        """
        normalized_lines = [line.rstrip() for line in code.splitlines()]
        normalized_code = "\n".join(normalized_lines).strip("\n") + "\n"
        rationale_parts = ["Normalized trailing whitespace"]
        if violate_policies:
            rationale_parts.append(f"Considered {len(violate_policies)} policy rules")
        
        # Send prompt to Gemini
        policy_fix_prompt = "\n".join([policy.fix_prompt for policy in violate_policies])
        prompt = f"""
        You are a helpful assistant. The following code violates the following policy rules:
        code:
        {normalized_code}
        policy and fix instructions:

        {policy_fix_prompt}

        Please fix the code to comply with the policy rules.
        """

        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "code": {"type": "STRING"},
                    },
                    "required": ["code"],
                },
            ),
        )
        fixed_code = json.loads(response.text)["code"]


        proposal = RefactorProposal(
            suggestion_id=str(uuid4()),
            file_path=file_path or "submitted_code.py",
            start_line=1,
            end_line=len(normalized_lines) or 1,
            original_code=code,
            proposed_code=fixed_code,
            rationale="; ".join(rationale_parts),
            confidence_score=0.65,
        )

        return RefactorResult(suggestions=[proposal], refactored_code=fixed_code)


