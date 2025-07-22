"""
CORS Configuration Module

Provides environment-aware CORS configuration for the FastAPI application.
Supports both development and production environments with appropriate defaults.
"""

import os
import socket
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def get_network_ip() -> str:
    """
    Get the local network IP address for development environments.
    
    Returns:
        str: The local network IP address, or empty string if not available
    """
    try:
        # Create a socket connection to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
            logger.info(f"Detected network IP: {network_ip}")
            return network_ip
    except Exception as e:
        logger.warning(f"Could not detect network IP: {e}")
        return ""


def get_development_origins() -> List[str]:
    """
    Get default development origins including localhost and network IP.
    
    Returns:
        List[str]: List of allowed origins for development
    """
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ]
    
    # Add network IP origins for mobile/remote testing
    network_ip = get_network_ip()
    if network_ip:
        origins.extend([
            f"http://{network_ip}:3000",
            f"http://{network_ip}:8000",
            f"http://{network_ip}",
        ])
    
    # Add common host network IPs for mobile access
    # These are typical network ranges for home/office networks
    host_ips = ["192.168.1.67"]  # Add your specific host IP
    for host_ip in host_ips:
        origins.extend([
            f"http://{host_ip}:3000",
            f"http://{host_ip}:8000",
            f"http://{host_ip}",
        ])
    
    return origins


def get_cors_origins() -> List[str]:
    """
    Get allowed CORS origins from environment variables or development defaults.
    
    Returns:
        List[str]: List of allowed origins
    """
    # Check for environment variable first
    cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS")
    
    if cors_origins_env:
        # Parse comma-separated origins from environment
        origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
        logger.info(f"Using CORS origins from environment: {origins}")
        return origins
    
    # Fall back to development defaults
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        logger.warning("Production environment detected but no CORS_ALLOWED_ORIGINS set. Using empty list.")
        return []
    
    # Development defaults
    origins = get_development_origins()
    logger.info(f"Using development CORS origins: {origins}")
    return origins


def get_cors_settings() -> Dict[str, Any]:
    """
    Get complete CORS configuration dictionary for FastAPI CORSMiddleware.
    
    Returns:
        Dict[str, Any]: Complete CORS configuration
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()
    allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    
    # Base configuration
    cors_config = {
        "allow_origins": get_cors_origins(),
        "allow_credentials": allow_credentials,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Mx-ReqToken",
            "Keep-Alive",
            "X-Requested-With",
            "If-Modified-Since",
        ],
        "max_age": 86400,  # 24 hours
    }
    
    # Environment-specific adjustments
    if environment == "production":
        # More restrictive settings for production
        cors_config["allow_headers"] = [
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
        ]
        cors_config["max_age"] = 3600  # 1 hour
    
    logger.info(f"CORS configuration for {environment} environment:")
    logger.info(f"  - Origins: {cors_config['allow_origins']}")
    logger.info(f"  - Allow credentials: {cors_config['allow_credentials']}")
    logger.info(f"  - Allow methods: {cors_config['allow_methods']}")
    logger.info(f"  - Max age: {cors_config['max_age']}")
    
    return cors_config