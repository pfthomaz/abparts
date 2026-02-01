"""
Logging configuration for AI Assistant service.
Provides structured logging with different handlers for development and production.
"""

import logging
import sys
from typing import Dict, Any
from datetime import datetime
import json
from pathlib import Path

from .config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging in production."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging() -> None:
    """
    Configure logging for the AI Assistant service.
    Uses JSON formatting in production and colored output in development.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if settings.ENVIRONMENT == "production":
        # Production: JSON formatted logs
        console_formatter = JSONFormatter()
    else:
        # Development: Colored, human-readable logs
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_dir / "ai_assistant.log")
    file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    
    if settings.ENVIRONMENT == "production":
        file_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors and above only)
    error_handler = logging.FileHandler(log_dir / "ai_assistant_errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configured - Environment: {settings.ENVIRONMENT}, "
        f"Level: {settings.LOG_LEVEL}"
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Request logging middleware helper
class RequestLogger:
    """Helper class for logging HTTP requests with context."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: str = None,
        session_id: str = None,
        request_id: str = None
    ) -> None:
        """Log an HTTP request with context."""
        extra = {
            "duration_ms": duration_ms,
        }
        
        if user_id:
            extra["user_id"] = user_id
        if session_id:
            extra["session_id"] = session_id
        if request_id:
            extra["request_id"] = request_id
        
        log_level = logging.INFO
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        
        self.logger.log(
            log_level,
            f"{method} {path} - {status_code} - {duration_ms:.2f}ms",
            extra=extra
        )
    
    def log_openai_request(
        self,
        model: str,
        tokens_used: int,
        duration_ms: float,
        success: bool,
        error: str = None
    ) -> None:
        """Log an OpenAI API request."""
        extra = {
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "model": model,
        }
        
        if success:
            self.logger.info(
                f"OpenAI API call successful - Model: {model}, Tokens: {tokens_used}",
                extra=extra
            )
        else:
            extra["error"] = error
            self.logger.error(
                f"OpenAI API call failed - Model: {model}, Error: {error}",
                extra=extra
            )
    
    def log_knowledge_base_search(
        self,
        query: str,
        results_count: int,
        duration_ms: float,
        session_id: str = None
    ) -> None:
        """Log a knowledge base search."""
        extra = {
            "duration_ms": duration_ms,
            "results_count": results_count,
        }
        
        if session_id:
            extra["session_id"] = session_id
        
        self.logger.info(
            f"Knowledge base search - Query: '{query[:50]}...', Results: {results_count}",
            extra=extra
        )
    
    def log_escalation(
        self,
        session_id: str,
        user_id: str,
        reason: str,
        machine_id: str = None
    ) -> None:
        """Log an escalation event."""
        extra = {
            "session_id": session_id,
            "user_id": user_id,
            "reason": reason,
        }
        
        if machine_id:
            extra["machine_id"] = machine_id
        
        self.logger.warning(
            f"Escalation triggered - Reason: {reason}",
            extra=extra
        )
