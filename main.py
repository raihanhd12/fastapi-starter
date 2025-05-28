import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.config.env as env
from src.routes.api.v1 import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events
    """
    # Startup
    logger.info("🚀 FastAPI Starter Template is starting up...")
    logger.info("📝 Documentation available at: http://0.0.0.0:8001/docs")
    logger.info("🔗 API Base URL: http://0.0.0.0:8001/api/v1")

    yield  # Server is running

    # Shutdown
    logger.info("⚡️ FastAPI Starter Template is shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Starter Template",
    description="A production-ready FastAPI starter with authentication, database integration, and clean architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FastAPI Starter Template",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "api_v1": "/api/v1",
            "auth": "/api/v1/auth",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "FastAPI Starter", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=env.API_HOST,
        port=env.API_PORT,
        reload=True,  # Enable auto-reload for development
        access_log=True,
        log_level="info",
    )
