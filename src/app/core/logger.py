import os
import logging
import sys
from .config import settings
from logging.handlers import RotatingFileHandler

# Use current working directory for logs
LOG_DIR = os.path.join(os.getcwd(), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=5),
    ],
)


def get_logger(name: str):
    logger = logging.getLogger(name)

    if settings.ENVIRONMENT == "PRODUCTION":
        logger.setLevel(logging.WARNING)
    elif settings.ENVIRONMENT == "STAGING":
        logger.setLevel(logging.INFO)
    else:  # Development and other environments
        logger.setLevel(logging.DEBUG)

    return logger
