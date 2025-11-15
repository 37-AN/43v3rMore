"""FastAPI application main entry point."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from loguru import logger

from .routes import router
from .models import HealthResponse, ErrorResponse
from ..utils.config import get_settings

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Quantum Trading AI API",
    description="Autonomous AI trading system using quantum computing",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = datetime.utcnow()

    response = await call_next(request)

    duration = (datetime.utcnow() - start_time).total_seconds()

    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
        },
    )

    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
        ).model_dump(),
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint.

    Returns:
        API information
    """
    return {
        "name": "Quantum Trading AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.debug else "disabled in production",
    }


# Include routers
app.include_router(router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("=" * 50)
    logger.info("Quantum Trading AI API Starting...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info("=" * 50)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Quantum Trading AI API Shutting Down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
