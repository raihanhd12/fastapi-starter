import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.config.env as env
from src.routes.api.v1 import router

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Embedding API",
    description="API for text embedding and vector search",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Embedding API",
        "documentation": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host=env.API_HOST, port=env.API_PORT)
