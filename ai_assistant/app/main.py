"""
AutoBoss AI Assistant FastAPI Application

This is the main entry point for the AI Assistant microservice.
It provides intelligent troubleshooting support for AutoBoss machines.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict, Any

from .config import settings
from .llm_client import LLMClient
from .session_manager import session_manager
from .database import init_database, close_database
from .routers import health, chat, sessions, knowledge_base, troubleshooting, machines

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global LLM client instance
llm_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global llm_client
    
    # Startup
    logger.info("Starting AI Assistant service...")
    try:
        # Initialize database
        await init_database()
        
        # Initialize session manager
        await session_manager.initialize()
        
        # Initialize LLM client
        llm_client = LLMClient()
        await llm_client.initialize()
        app.state.llm_client = llm_client
        
        logger.info("AI Assistant service started successfully")
    except Exception as e:
        logger.error(f"Failed to start AI Assistant service: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Assistant service...")
    if llm_client:
        await llm_client.cleanup()
    await session_manager.cleanup()
    await close_database()
    logger.info("AI Assistant service shut down")


# Create FastAPI application
app = FastAPI(
    title="AutoBoss AI Assistant",
    description="Intelligent troubleshooting assistant for AutoBoss machines",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api/ai", tags=["chat"])
app.include_router(sessions.router, prefix="/api/ai", tags=["sessions"])
app.include_router(knowledge_base.router, prefix="/api/ai", tags=["knowledge"])
app.include_router(troubleshooting.router, prefix="/api/ai", tags=["troubleshooting"])
app.include_router(machines.router, tags=["machines"])

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/admin")
async def admin_interface():
    """Serve the knowledge base admin interface."""
    return FileResponse("app/static/admin.html")


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint providing service information."""
    return {
        "service": "AutoBoss AI Assistant",
        "version": "1.0.0",
        "status": "running",
        "description": "Intelligent troubleshooting assistant for AutoBoss machines"
    }


@app.get("/info")
async def info() -> Dict[str, Any]:
    """Service information endpoint."""
    return {
        "service": "AutoBoss AI Assistant",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "supported_languages": [
            {"code": "en", "name": "English"},
            {"code": "el", "name": "Greek (Ελληνικά)"},
            {"code": "ar", "name": "Arabic (العربية)"},
            {"code": "es", "name": "Spanish (Español)"},
            {"code": "tr", "name": "Turkish (Türkçe)"},
            {"code": "no", "name": "Norwegian (Norsk)"}
        ],
        "features": {
            "multilingual_support": True,
            "auto_language_detection": True,
            "voice_input": False,  # Will be implemented in later tasks
            "machine_context": True,  # Implemented in Task 8
            "knowledge_base": True  # Implemented in Task 5
        }
    }