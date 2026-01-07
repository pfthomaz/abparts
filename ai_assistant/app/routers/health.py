"""
Health check endpoints for the AI Assistant service.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import time
import logging

from ..config import settings
from ..llm_client import LLMClient, ConversationMessage

logger = logging.getLogger(__name__)
router = APIRouter()


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client from app state."""
    from ..main import app
    if not hasattr(app.state, 'llm_client') or app.state.llm_client is None:
        raise HTTPException(status_code=503, detail="LLM client not initialized")
    return app.state.llm_client


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "AutoBoss AI Assistant",
        "timestamp": time.time(),
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready")
async def readiness_check(llm_client: LLMClient = Depends(get_llm_client)) -> Dict[str, Any]:
    """Readiness check that verifies all dependencies are available."""
    checks = {
        "llm_client": False,
        "openai_api": False,
        "configuration": False
    }
    
    overall_status = "ready"
    
    try:
        # Check LLM client
        if llm_client and llm_client.client:
            checks["llm_client"] = True
        else:
            overall_status = "not_ready"
        
        # Check OpenAI API (quick test)
        if checks["llm_client"]:
            try:
                test_messages = [
                    ConversationMessage(role="user", content="test")
                ]
                response = await llm_client.generate_response(
                    messages=test_messages,
                    max_tokens=5
                )
                if response.success:
                    checks["openai_api"] = True
                else:
                    overall_status = "not_ready"
                    logger.warning(f"OpenAI API test failed: {response.error_message}")
            except Exception as e:
                overall_status = "not_ready"
                logger.error(f"OpenAI API readiness check failed: {e}")
        
        # Check configuration
        if settings.OPENAI_API_KEY and settings.DATABASE_URL:
            checks["configuration"] = True
        else:
            overall_status = "not_ready"
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        overall_status = "not_ready"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": time.time(),
        "service": "AutoBoss AI Assistant"
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes/Docker health monitoring."""
    return {
        "status": "alive",
        "timestamp": time.time()
    }