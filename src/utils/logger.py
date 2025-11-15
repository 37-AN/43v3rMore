"""Logging configuration using Loguru."""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger

# Remove default handler
logger.remove()


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "30 days",
    compression: str = "zip",
) -> None:
    """
    Configure application logger with file and console outputs.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default path
        rotation: When to rotate log files
        retention: How long to keep old logs
        compression: Compression format for old logs

    Example:
        >>> setup_logger(log_level="DEBUG")
        >>> logger.info("Application started")
    """
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # File handler
    if log_file is None:
        log_path = Path("data/logs")
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = str(log_path / "quantum_trading.log")

    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression=compression,
        enqueue=True,  # Thread-safe
    )

    logger.info(f"Logger initialized with level: {log_level}")


def get_logger(name: Optional[str] = None):
    """
    Get logger instance for a specific module.

    Args:
        name: Module name for context. If None, uses caller's module

    Returns:
        Logger instance with context

    Example:
        >>> log = get_logger(__name__)
        >>> log.info("Processing started")
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize with default settings on import
setup_logger()
