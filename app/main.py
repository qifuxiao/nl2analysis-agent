"""
Chat Service Main Application.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import chat, knowledge, llm, routes

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Chat Service starting...")
    logger.info(f"Model: {settings.default_model}")
    logger.info(f"Base URL: {settings.openai_base_url}")
    
    yield
    
    # Shutdown
    logger.info("Chat Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Chat Service",
    description="Multi-mode chat service with LLM support",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(llm.router)
app.include_router(routes.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Chat Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": settings.default_model,
        "base_url": settings.openai_base_url
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
