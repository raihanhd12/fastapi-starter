import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.config.env as env
from src.routes.api.v1 import router as api_router
from src.routes.api.auth import router as auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
app.include_router(auth_router, prefix="/api/v1")


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


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 FastAPI Starter Template is starting up...")
    logger.info(
        f"📝 Documentation available at: http://{env.API_HOST}:{env.API_PORT}/docs"
    )
    logger.info(f"🔗 API Base URL: http://{env.API_HOST}:{env.API_PORT}/api/v1")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 FastAPI Starter Template is shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=env.API_HOST,
        port=env.API_PORT,
        reload=True,  # Enable auto-reload for development
        access_log=True,
        log_level="info",
    )
