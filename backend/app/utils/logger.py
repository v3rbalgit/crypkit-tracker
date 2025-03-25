"""Logging configuration for the application."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

# Constants for logging configuration
LOGS_DIR = Path("logs")
LOG_FILENAME = "app.log"
ERROR_LOG_FILENAME = "error.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True, parents=True)

# Format string for logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: The name of the module (typically __name__)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)

    # Set base log level
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

    # Console handler - INFO level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File handler - DEBUG level
    file_handler = RotatingFileHandler(LOGS_DIR / LOG_FILENAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Error file handler - ERROR level
    error_file_handler = RotatingFileHandler(
        LOGS_DIR / ERROR_LOG_FILENAME, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)

    return logger
