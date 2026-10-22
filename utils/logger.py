import logging
import sys
from pathlib import Path
from config.config import Config


def get_logger(name: str = "automation") -> logging.Logger:
    """
    Returns a configured thread-safe logger writing to both console and file.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if already configured
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Ensure log directory exists
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = Config.LOGS_DIR / "automation.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
