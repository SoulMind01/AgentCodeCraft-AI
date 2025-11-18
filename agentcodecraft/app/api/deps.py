"""
Shared FastAPI dependencies.
"""
from sqlalchemy.orm import Session

from app.db import get_db_session
from app.services.gemini_adapter import GeminiAdapter
from app.services.orchestrator import AgentCodeCraftApp
from app.services.policy_engine import PolicyEngine
from app.services.static_analysis import StaticAnalysisService

_adapter = GeminiAdapter()
_policy_engine = PolicyEngine()
_static_analysis = StaticAnalysisService()
_agent_app = AgentCodeCraftApp(
    adapter=_adapter,
    policy_engine=_policy_engine,
    static_analysis=_static_analysis,
)


def get_db() -> Session:
    """Dependency wrapper for DB session."""
    yield from get_db_session()


def get_agent_app() -> AgentCodeCraftApp:
    """Return the orchestrator singleton."""
    return _agent_app



