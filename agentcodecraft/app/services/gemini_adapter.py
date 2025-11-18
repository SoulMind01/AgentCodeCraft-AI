"""
Stubbed Gemini adapter that simulates refactoring suggestions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence
from uuid import uuid4

from app.models.orm import PolicyRule


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

    def test_connection(self) -> bool:
        """Simulate adapter health check."""
        return True

    def generate_refactor(
        self, *, code: str, ast_summary: str | None, policies: Sequence[PolicyRule], file_path: str
    ) -> RefactorResult:
        """
        Produce refactoring suggestions based on the provided code.

        This stub performs simple whitespace normalization to demonstrate the workflow.
        """
        normalized_lines = [line.rstrip() for line in code.splitlines()]
        normalized_code = "\n".join(normalized_lines).strip("\n") + "\n"
        rationale_parts = ["Normalized trailing whitespace"]
        if policies:
            rationale_parts.append(f"Considered {len(policies)} policy rules")

        proposal = RefactorProposal(
            suggestion_id=str(uuid4()),
            file_path=file_path or "submitted_code.py",
            start_line=1,
            end_line=len(normalized_lines) or 1,
            original_code=code,
            proposed_code=normalized_code,
            rationale="; ".join(rationale_parts),
            confidence_score=0.65,
        )

        return RefactorResult(suggestions=[proposal], refactored_code=normalized_code)


