import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import os
from .config import get_settings

settings = get_settings()

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logger():
    logger = logging.getLogger("bare_metals")
    
    # Set log level based on debug setting
    level = logging.DEBUG if settings.debug else logging.INFO
    logger.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Daily Rotation, keep for 3 days)
    file_handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="D",
        interval=1,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
