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
from app.api import export
from app.services.scheduler import start_scheduler
from logging_config import get_logger

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting Games Industry Jobs Dashboard API...")
    init_db()
    start_scheduler()
    logger.info("API started successfully")
    yield
    logger.info("Shutting down API...")
    close_db()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Games Industry Jobs Dashboard API",
    description="API for tracking UK games industry job market trends",
    version="1.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(export.router, prefix="/api/export", tags=["Export"])


@app.get("/api/welcome")
async def api_welcome():
    return {
        "message": "Games Industry Jobs Dashboard API",
        "version": "1.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"context": {"path": request.url.path, "method": request.method}}
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ------------------------------------------------------------------------------
# Frontend Static File Serving (for Single-Container Deployment)
# ------------------------------------------------------------------------------
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check if static directory exists (it will in Docker production build)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount static files
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    # Explicit root handler for index.html
    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(static_dir, "index.html"))

    # Catch-all route for SPA (React Router)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API routes to pass through (already handled above due to order)
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
             return JSONResponse(status_code=404, content={"detail": "Not found"})
             
        # Serve index.html for everything else
        return FileResponse(os.path.join(static_dir, "index.html"))

from fastapi.responses import FileResponse
