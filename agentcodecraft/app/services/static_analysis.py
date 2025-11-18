"""
Static analysis helpers for computing heuristics.
"""
from __future__ import annotations

import math
from typing import Iterable

from app.models.orm import RefactorSession


class StaticAnalysisService:
    """Compute lightweight metrics for refactor sessions."""

    control_keywords = ("if ", "for ", "while ", "def ", "class ", "try:", "with ")

    def compute_complexity(self, code: str) -> float:
        """Return a naive complexity estimate based on lines and control flow keywords."""
        lines = [line for line in code.splitlines() if line.strip()]
        control_statements = sum(1 for line in lines for keyword in self.control_keywords if keyword in line)
        return round(len(lines) + math.log2(control_statements + 1), 2)

    def run_tests(self, session: RefactorSession | None = None) -> float:
        """
        Placeholder test runner that returns a deterministic score.

        TODO: Integrate with actual test execution pipeline.
        """
        _ = session
        return 1.0

    def summarize_complexity(self, original: str, refactored: str) -> float:
        """Compute delta between original and refactored code complexity."""
        return round(self.compute_complexity(refactored) - self.compute_complexity(original), 2)


