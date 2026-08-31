from loguru import logger
import sys
from .config import get_settings

settings = get_settings()

def setup_logging():
    logger.remove()
    logger.add(sys.stdout, level=settings.LOG_LEVEL)
    logger.add("logs/qcc_{time}.log", rotation="500 MB", retention="10 days", level="DEBUG")
    logger.info("Logging initialized")

setup_logging()
