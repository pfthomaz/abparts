"""
User service for AI Assistant.

This module provides functionality to retrieve user information
from the ABParts system, including language preferences.
"""

import logging
from typing import Optional, Dict, Any, List
from .abparts_integration import abparts_integration

logger = logging.getLogger(__name__)


class UserService:
    """Service for retrieving user information from ABParts."""
    
    def __init__(self):
        self.abparts_integration = abparts_integration
        
    async def get_user_language(self, user_id: str, auth_token: str = None) -> str:
        """
        Get user's preferred language from ABParts.
        
        Args:
            user_id: User ID from ABParts
            auth_token: JWT token for authentication (not used in direct DB access)
            
        Returns:
            Language code (defaults to 'en' if not found or error)
        """
        try:
            user_preferences = await self.abparts_integration.get_user_preferences(user_id)
            
            if user_preferences:
                preferred_language = user_preferences.get("preferred_language", "en")
                
                # Validate language code
                supported_languages = ["en", "el", "ar", "es", "tr", "no"]
                if preferred_language in supported_languages:
                    logger.info(f"Retrieved user language: {preferred_language} for user {user_id}")
                    return preferred_language
                else:
                    logger.warning(f"Unsupported language {preferred_language} for user {user_id}, defaulting to 'en'")
                    return "en"
            else:
                logger.warning(f"User preferences not found for user {user_id}, defaulting to 'en'")
                return "en"
                    
        except Exception as e:
            logger.error(f"Error retrieving user language for user {user_id}: {e}")
            return "en"
    
    async def get_user_profile(self, user_id: str, auth_token: str = None) -> Optional[Dict[str, Any]]:
        """
        Get complete user profile from ABParts.
        
        Args:
            user_id: User ID from ABParts
            auth_token: JWT token for authentication (not used in direct DB access)
            
        Returns:
            User profile data or None if error
        """
        try:
            user_preferences = await self.abparts_integration.get_user_preferences(user_id)
            
            if user_preferences:
                logger.info(f"Retrieved user profile for user {user_id}")
                return user_preferences
            else:
                logger.warning(f"User profile not found for user {user_id}")
                return None
                    
        except Exception as e:
            logger.error(f"Error retrieving user profile for user {user_id}: {e}")
            return None
    
    async def get_machine_context(self, machine_id: str, auth_token: str = None) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive machine context information from ABParts.
        
        Args:
            machine_id: Machine ID from ABParts
            auth_token: JWT token for authentication (not used in direct DB access)
            
        Returns:
            Machine context data including details, maintenance history, and usage patterns
        """
        try:
            # Get machine details
            machine_details = await self.abparts_integration.get_machine_details(machine_id)
            if not machine_details:
                logger.warning(f"Machine details not found for machine {machine_id}")
                return None
            
            # Get maintenance history
            maintenance_history = await self.abparts_integration.get_maintenance_history(machine_id, limit=5)
            
            # Get parts usage data
            parts_usage = await self.abparts_integration.get_parts_usage_data(machine_id, days=30)
            
            # Get machine hours history
            hours_history = await self.abparts_integration.get_machine_hours_history(machine_id, limit=10)
            
            # Get preventive maintenance suggestions
            maintenance_suggestions = await self.abparts_integration.get_preventive_maintenance_suggestions(machine_id)
            
            # Build comprehensive context for AI
            context = {
                "machine_details": {
                    "id": machine_details.get("id"),
                    "name": machine_details.get("name"),
                    "model_type": machine_details.get("model_type"),
                    "serial_number": machine_details.get("serial_number"),
                    "current_hours": machine_details.get("latest_hours", 0),
                    "total_hours_records": machine_details.get("total_hours_records", 0),
                    "organization": machine_details.get("customer_organization", {}).get("name", "Unknown"),
                    "country": machine_details.get("customer_organization", {}).get("country", "Unknown")
                },
                "recent_maintenance": [
                    {
                        "date": record.get("maintenance_date"),
                        "type": record.get("maintenance_type"),
                        "description": record.get("description"),
                        "hours_spent": record.get("hours_spent"),
                        "parts_used": len(record.get("parts_used", [])),
                        "performed_by": record.get("performed_by", {}).get("name", "Unknown")
                    }
                    for record in maintenance_history[:3]  # Last 3 maintenance records
                ],
                "recent_parts_usage": [
                    {
                        "date": usage.get("usage_date"),
                        "part_name": usage.get("part", {}).get("name"),
                        "part_number": usage.get("part", {}).get("part_number"),
                        "quantity": usage.get("quantity"),
                        "is_proprietary": usage.get("part", {}).get("is_proprietary", False)
                    }
                    for usage in parts_usage[:5]  # Last 5 parts usage records
                ],
                "hours_trend": [
                    {
                        "date": record.get("recorded_date"),
                        "hours": record.get("hours_value"),
                        "recorded_by": record.get("recorded_by", {}).get("name", "Unknown")
                    }
                    for record in hours_history[:5]  # Last 5 hours records
                ],
                "maintenance_suggestions": [
                    {
                        "type": suggestion.get("type"),
                        "description": suggestion.get("description"),
                        "priority": suggestion.get("priority"),
                        "overdue_hours": suggestion.get("overdue_hours", 0)
                    }
                    for suggestion in maintenance_suggestions[:3]  # Top 3 suggestions
                ]
            }
            
            logger.info(f"Retrieved comprehensive machine context for machine {machine_id}")
            return context
                    
        except Exception as e:
            logger.error(f"Error retrieving machine context for machine {machine_id}: {e}")
            return None
    
    async def get_user_machines(self, user_id: str, auth_token: str = None) -> List[Dict[str, Any]]:
        """
        Get all machines accessible to a user.
        
        Args:
            user_id: User ID from ABParts
            auth_token: JWT token for authentication (not used in direct DB access)
            
        Returns:
            List of machines accessible to the user
        """
        try:
            machines = await self.abparts_integration.get_user_machines(user_id)
            logger.info(f"Retrieved {len(machines)} machines for user {user_id}")
            return machines
                    
        except Exception as e:
            logger.error(f"Error retrieving machines for user {user_id}: {e}")
            return []