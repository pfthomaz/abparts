"""
User service for AI Assistant.

This module provides functionality to retrieve user information
from the ABParts system, including language preferences.
"""

import logging
from typing import Optional, Dict, Any
import httpx
from ..config import settings

logger = logging.getLogger(__name__)


class UserService:
    """Service for retrieving user information from ABParts."""
    
    def __init__(self):
        self.abparts_api_base = settings.ABPARTS_API_BASE_URL
        self.timeout = 10.0
        
    async def get_user_language(self, user_id: str, auth_token: str) -> str:
        """
        Get user's preferred language from ABParts.
        
        Args:
            user_id: User ID from ABParts
            auth_token: JWT token for authentication
            
        Returns:
            Language code (defaults to 'en' if not found or error)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.abparts_api_base}/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    preferred_language = user_data.get("preferred_language", "en")
                    
                    # Validate language code
                    supported_languages = ["en", "el", "ar", "es", "tr", "no"]
                    if preferred_language in supported_languages:
                        logger.info(f"Retrieved user language: {preferred_language} for user {user_id}")
                        return preferred_language
                    else:
                        logger.warning(f"Unsupported language {preferred_language} for user {user_id}, defaulting to 'en'")
                        return "en"
                else:
                    logger.warning(f"Failed to retrieve user data: {response.status_code}")
                    return "en"
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout retrieving user language for user {user_id}")
            return "en"
        except Exception as e:
            logger.error(f"Error retrieving user language for user {user_id}: {e}")
            return "en"
    
    async def get_user_profile(self, user_id: str, auth_token: str) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile from ABParts.
        
        Args:
            user_id: User ID from ABParts
            auth_token: JWT token for authentication
            
        Returns:
            User profile data or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.abparts_api_base}/users/{user_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    logger.info(f"Retrieved user profile for user {user_id}")
                    return user_data
                else:
                    logger.warning(f"Failed to retrieve user profile: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout retrieving user profile for user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user profile for user {user_id}: {e}")
            return None
    
    async def get_machine_context(self, machine_id: str, auth_token: str) -> Optional[Dict[str, Any]]:
        """
        Get machine context information from ABParts.
        
        Args:
            machine_id: Machine ID from ABParts
            auth_token: JWT token for authentication
            
        Returns:
            Machine context data or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.abparts_api_base}/machines/{machine_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    machine_data = response.json()
                    
                    # Format machine context for AI
                    context = {
                        "model": machine_data.get("model", "Unknown"),
                        "serial_number": machine_data.get("serial_number", "Unknown"),
                        "installation_date": machine_data.get("installation_date", "Unknown"),
                        "last_maintenance": machine_data.get("last_maintenance", "Unknown"),
                        "location": machine_data.get("location", "Unknown"),
                        "status": machine_data.get("status", "Unknown")
                    }
                    
                    logger.info(f"Retrieved machine context for machine {machine_id}")
                    return context
                else:
                    logger.warning(f"Failed to retrieve machine data: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout retrieving machine context for machine {machine_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving machine context for machine {machine_id}: {e}")
            return None