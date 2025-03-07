"""Logging utilities for the Yu-Gi-Oh! Card Database Generator."""

import os
import logging
import sys
from typing import Optional

import colorama
from colorama import Fore, Style


# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored log messages."""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }
    
    def format(self, record):
        """Format the log record with colors."""
        levelname = record.levelname
        message = super().format(record)
        
        # Add color based on log level
        if levelname in self.COLORS:
            message = f"{self.COLORS[levelname]}{message}{Style.RESET_ALL}"
            
        return message


def setup_logging(log_file: Optional[str] = "yugioh_db_generator.log", verbose: int = 0) -> logging.Logger:
    """Set up logging for the application.
    
    Args:
        log_file: Path to the log file (None for no file logging)
        verbose: Verbosity level (0=INFO, 1=DEBUG)
        
    Returns:
        The configured logger instance
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)
    
    # Use colored formatter for console
    console_format = "%(levelname)s: %(message)s"
    console_handler.setFormatter(ColoredFormatter(console_format))
    logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        
        # Use standard formatter for file
        file_format = "%(asctime)s - %(levelname)s - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)
    
    return logger
