"""Logging utility for Game Danmaku AI."""

import sys
from loguru import logger

def setup_logger(log_file="game_danmaku.log", level="DEBUG"):
    """Configure application logging."""
    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level
    )

    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    return logger

app_logger = setup_logger()
