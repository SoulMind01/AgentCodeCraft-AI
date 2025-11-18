"""
FastAPI application entry point.
"""
from fastapi import FastAPI

from app.db import init_db
from app.api.routes_refactor import router as refactor_router
from app.api.routes_policies import router as policies_router
from app.api.routes_sessions import router as sessions_router


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    application = FastAPI(title="AgentCodeCraft AI", version="0.1.0")
    application.include_router(refactor_router)
    application.include_router(policies_router)
    application.include_router(sessions_router)

    @application.get("/")
    def root():
        return {"message": "AgentCodeCraft backend is running"}

    @application.get("/health")
    def health_check():
        return {"status": "ok"}

    return application


app = create_app()


@app.on_event("startup")
def on_startup():
    """Ensure database schema exists."""
    init_db()


