"""
Stubbed Gemini adapter that simulates refactoring suggestions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence
from uuid import uuid4
import os

from app.models.orm import PolicyRule
from app.config import get_settings
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
        prompt = f"""You are a code refactoring assistant. Refactor the following Python code to comply with the policy rules.

IMPORTANT: 
- Preserve all code formatting, indentation, and newlines exactly as they should appear in Python code
- Use proper Python indentation (4 spaces per level)
- Include all necessary imports
- Maintain code structure and readability
- The output must be valid, properly formatted Python code

Original code:
```python
{normalized_code}
```

Policy violations and fix instructions:
{policy_fix_prompt}

Refactor the code to fix all policy violations while maintaining functionality. Return the complete refactored code with proper formatting, indentation, and newlines."""

        # Get API key from config or environment
        settings = get_settings()
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        # Ensure API key is available to genai library
        # The library looks for GOOGLE_API_KEY in environment, so set it if we have GEMINI_API_KEY
        if api_key and api_key != "GEMINI_API_KEY_PLACEHOLDER":
            # Set as environment variable for genai library compatibility
            if not os.getenv("GOOGLE_API_KEY"):
                os.environ["GOOGLE_API_KEY"] = api_key
            # Create client with explicit API key
            client = genai.Client(api_key=api_key)
        else:
            # Fallback: try without explicit key (will use environment)
            client = genai.Client()
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Using Flash for cost efficiency and speed
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
        
        # Parse JSON response
        try:
            response_data = json.loads(response.text)
            fixed_code = response_data.get("code", "")
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: if JSON parsing fails, try to extract code from raw response
            raise ValueError(f"Failed to parse Gemini response: {e}")
        
        # Normalize code formatting: ensure proper newlines are preserved
        # json.loads() automatically converts \n escape sequences to actual newlines
        # But we need to handle edge cases where Gemini might return improperly formatted code
        if not isinstance(fixed_code, str):
            fixed_code = str(fixed_code)
        
        # Check if code appears to be all on one line (indicates formatting issue)
        # This should not happen with the improved prompt, but we'll handle it as a safety net
        # Only do this check if code is suspiciously long without newlines (performance optimization)
        if "\n" not in fixed_code and len(fixed_code) > 50:
            # This indicates Gemini returned code without newlines despite our prompt
            # We'll try a simple heuristic: look for Python keywords that typically start new lines
            import re
            # Add newlines before class/def/if/for/while/try/except/else/elif
            # This is a last-resort fallback - the prompt should prevent this
            fixed_code = re.sub(r'\b(class|def|if|for|while|try|except|finally|else|elif|async def)\b', r'\n\1', fixed_code)
            # Add newlines after colons that start blocks (simplified pattern for performance)
            fixed_code = re.sub(r':\s*([a-zA-Z_])', r':\n    \1', fixed_code)
            # Clean up any double newlines (single pass)
            fixed_code = re.sub(r'\n{3,}', r'\n\n', fixed_code)
            # Remove leading newline if added
            fixed_code = fixed_code.lstrip('\n')
        
        # Normalize line endings: ensure consistent \n newlines
        # splitlines() handles \r\n, \r, and \n correctly
        lines = fixed_code.splitlines()
        if not lines:
            # Empty code - return minimal valid code
            fixed_code = "\n"
        else:
            # Reconstruct with proper newlines (splitlines() removes trailing newline, so we add it back)
            fixed_code = "\n".join(lines)
            # Ensure code ends with a single newline
            if fixed_code and not fixed_code.endswith("\n"):
                fixed_code += "\n"


        # Calculate end line for proposal (use original code line count)
        original_line_count = len(normalized_lines) or 1
        
        proposal = RefactorProposal(
            suggestion_id=str(uuid4()),
            file_path=file_path or "submitted_code.py",
            start_line=1,
            end_line=original_line_count,
            original_code=code,
            proposed_code=fixed_code,
            rationale="; ".join(rationale_parts),
            confidence_score=0.65,
        )

        return RefactorResult(suggestions=[proposal], refactored_code=fixed_code)


