import logging
import sys
from typing import Optional

def setup_logger(name: str = "aio_cc", level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Sets up a logger with console and optional file output.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Default logger instance
logger = setup_logger()
