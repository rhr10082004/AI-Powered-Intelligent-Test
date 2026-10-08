"""
Main FastAPI application factory.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.api.config import get_settings
from services.api.database import close_db, init_db
from services.api.routes.auth import router as auth_router
from services.api.schemas import HealthResponse
from datetime import datetime


# Lifespan context
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    # Startup
    print("Starting up application...")
    await init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    await close_db()
    print("Database closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Intelligent Test Preparation Platform",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health", response_model=HealthResponse)
    @app.get("/api/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            environment=settings.environment,
        )
    
    # Root endpoint
    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "message": "Welcome to Intelligent Test Prep Platform API",
            "version": settings.app_version,
            "docs": "/docs",
        }
    
    # Include routers
    from services.api.routes.users import router as users_router
    from services.api.routes.exams import router as exams_router
    from services.api.routes.learning import router as learning_router
    from services.api.routes.tutor import router as tutor_router
    from services.api.routes.writing import router as writing_router
    from services.api.routes.speaking import router as speaking_router
    from services.api.routes.mock_tests import router as mock_tests_router
    from services.api.routes.activity import router as activity_router

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(users_router, prefix=settings.api_prefix)
    app.include_router(exams_router, prefix=settings.api_prefix)
    app.include_router(learning_router, prefix=settings.api_prefix)
    app.include_router(tutor_router, prefix=settings.api_prefix)
    app.include_router(writing_router, prefix=settings.api_prefix)
    app.include_router(speaking_router, prefix=settings.api_prefix)
    app.include_router(mock_tests_router, prefix=settings.api_prefix)
    app.include_router(activity_router, prefix=settings.api_prefix)

    
    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.api_host if hasattr(settings, "api_host") else "0.0.0.0",
        port=settings.api_port if hasattr(settings, "api_port") else 8000,
        reload=settings.debug,
    )
