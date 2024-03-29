import os
import logging
import sys
from config import settings
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

# Define a basic configuration for the logger
logging.basicConfig(
    level=logging.INFO,  # Default log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    datefmt='%Y-%m-%d %H:%M:%S',  # Date format
    handlers=[
        logging.StreamHandler(sys.stdout),  # Print to stdout
        RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=5)
    ]
)

def get_logger(name: str):
    """
    Returns a logger instance with the given name.
    Adjusts log level based on the application environment.
    """
    logger = logging.getLogger(name)

    # Example: Adjust log level based on the environment
    if settings.ENVIRONMENT == 'PRODUCTION':
        logger.setLevel(logging.WARNING)
    elif settings.ENVIRONMENT == 'STAGING':
        logger.setLevel(logging.INFO)
    else:  # Development and other environments
        logger.setLevel(logging.DEBUG)

    return logger
