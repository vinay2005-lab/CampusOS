"""Main FastAPI application entry point.

Configures routes, middleware, exception handlers, and startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time

from app.config import get_settings
from app.database import init_db
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.error_handler import ErrorHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_period}s"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production-ready campus management system with AI-powered features",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=429,
    content={"detail": "Rate limit exceeded. Please try again later."}
))

# Add middleware
# 1. Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly in production
)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)

# 3. Logging Middleware
app.add_middleware(LoggingMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Service status and version
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information.

    Returns:
        dict: API information and available endpoints
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "documents": "/api/v1/documents",
            "queries": "/api/v1/queries",
            "admissions": "/api/v1/admissions",
            "notices": "/api/v1/notices",
            "analytics": "/api/v1/analytics"
        }
    }


# Import and include routers
from app.routers import auth, users, documents, queries, admissions, notices, analytics, admin

api_v1 = FastAPI(title="CampusOS API v1")
api_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1.include_router(users.router, prefix="/users", tags=["Users"])
api_v1.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_v1.include_router(queries.router, prefix="/queries", tags=["AI Queries"])
api_v1.include_router(admissions.router, prefix="/admissions", tags=["Admissions"])
api_v1.include_router(notices.router, prefix="/notices", tags=["Notices"])
api_v1.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_v1.include_router(admin.router, prefix="/admin", tags=["Admin"])

app.include_router(api_v1, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
