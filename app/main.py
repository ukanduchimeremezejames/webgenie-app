"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import datasets, jobs, results
from app.core import get_logger, settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="Production-ready FastAPI backend for Beeline GRN inference",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Root endpoint
@app.get("/")
async def root():
    """Health check and API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
    }


# Include routers
app.include_router(datasets.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(results.router, prefix="/api")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
