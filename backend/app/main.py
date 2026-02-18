"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.database import init_db, close_db
from app.api import jobs, keywords, trends, regional, admin
from logging_config import get_logger

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Games Industry Jobs Dashboard API...")
    init_db()
    logger.info("API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    close_db()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Games Industry Jobs Dashboard API",
    description="API for tracking UK games industry job market trends",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests and response times."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "context": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s"
            }
        }
    )
    
    return response


# Include routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(trends.router, prefix="/api/trends", tags=["Trends"])
app.include_router(regional.router, prefix="/api/regional", tags=["Regional"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Games Industry Jobs Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "context": {
                "path": request.url.path,
                "method": request.method
            }
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
