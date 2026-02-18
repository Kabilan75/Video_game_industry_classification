"""
Centralized logging configuration for the application.
Supports structured JSON logging with rotation and multiple log categories.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom context if present
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        return json.dumps(log_data)


def setup_logger(
    name: str,
    log_file: str,
    level: int = logging.INFO,
    rotation_days: int = 30,
    use_json: bool = True
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        rotation_days: Number of days to keep logs
        use_json: Whether to use JSON formatting
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=rotation_days,
        encoding="utf-8"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Set formatters
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Initialize loggers for different categories
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))

# Scraper logs
scraper_logger = setup_logger(
    "scraper",
    f"{LOG_DIR}/scraper/scraper_run_{datetime.now().strftime('%Y%m%d')}.log",
    level=LOG_LEVEL,
    rotation_days=90
)

# API logs
api_logger = setup_logger(
    "api",
    f"{LOG_DIR}/api/api_{datetime.now().strftime('%Y%m%d')}.log",
    level=LOG_LEVEL,
    rotation_days=30
)

# NLP processing logs
nlp_logger = setup_logger(
    "nlp",
    f"{LOG_DIR}/nlp/nlp_processing_{datetime.now().strftime('%Y%m%d')}.log",
    level=LOG_LEVEL,
    rotation_days=30
)

# Database logs
db_logger = setup_logger(
    "database",
    f"{LOG_DIR}/database/db_operations_{datetime.now().strftime('%Y%m%d')}.log",
    level=LOG_LEVEL,
    rotation_days=30
)

# System logs
system_logger = setup_logger(
    "system",
    f"{LOG_DIR}/system/system_{datetime.now().strftime('%Y%m%d')}.log",
    level=LOG_LEVEL,
    rotation_days=90
)


def get_logger(category: str) -> logging.Logger:
    """
    Get logger by category.
    
    Args:
        category: Logger category (scraper, api, nlp, database, system)
    
    Returns:
        Logger instance
    """
    loggers = {
        "scraper": scraper_logger,
        "api": api_logger,
        "nlp": nlp_logger,
        "database": db_logger,
        "system": system_logger,
    }
    
    return loggers.get(category, system_logger)
