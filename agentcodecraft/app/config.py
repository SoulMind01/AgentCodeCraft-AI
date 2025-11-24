"""
Application configuration powered by pydantic settings.
"""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration for AgentCodeCraft AI."""

    environment: str = Field(default="local")
    database_url: str = Field(default="sqlite:///./agentcodecraft.db")
    gemini_api_key: str = Field(default="GEMINI_API_KEY_PLACEHOLDER")
    log_level: str = Field(default="INFO")
    use_adk: bool = Field(default=False)  # ADK feature flag

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


