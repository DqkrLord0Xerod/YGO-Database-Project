"""Command-line interface utilities for the Yu-Gi-Oh! Card Database Generator."""

import os
import sys
import time
import logging
from typing import List, Optional
import tqdm

from yugioh_db_generator import __version__


logger = logging.getLogger(__name__)


def show_welcome_message():
    """Show a welcome message when the program starts."""
    print(f"\n{'-'*60}")
    print(f"  Yu-Gi-Oh! Card Database Generator v{__version__}")
    print(f"  A tool to generate comprehensive card information databases")
    print(f"{'-'*60}\n")


def show_version():
    """Display version information and exit."""
    print(f"Yu-Gi-Oh! Card Database Generator v{__version__}")
    sys.exit(0)


def create_progress_bar(total: int, desc: str = "Processing") -> tqdm.tqdm:
    """Create a progress bar for command-line display.
    
    Args:
        total: Total number of items to process
        desc: Description text for the progress bar
        
    Returns:
        tqdm progress bar instance
    """
    return tqdm.tqdm(
        total=total, 
        desc=desc,
        bar_format="{desc}: {percentage:3.0f}% |{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    )


def update_progress(progress_bar: tqdm.tqdm, advance: int = 1):
    """Update a progress bar.
    
    Args:
        progress_bar: The progress bar to update
        advance: Number of steps to advance
    """
    progress_bar.update(advance)


def show_results_summary(
    output_file: str, 
    processed: int, 
    found: int, 
    corrected: int, 
    not_found: int,
    corrections_file: Optional[str] = None
):
    """Show a summary of the database generation results.
    
    Args:
        output_file: Path to the generated database file
        processed: Number of cards processed
        found: Number of cards found (exact matches)
        corrected: Number of cards with corrected names
        not_found: Number of cards not found
        corrections_file: Path to the corrections file, if generated
    """
    print(f"\n{'-'*60}")
    print(f"  Database Generation Summary")
    print(f"{'-'*60}")
    print(f"  Total cards processed: {processed}")
    print(f"  Exact matches: {found}")
    print(f"  Corrected matches: {corrected}")
    print(f"  Not found: {not_found}")
    print(f"{'-'*60}")
    print(f"  Output saved to: {os.path.abspath(output_file)}")
    
    if corrections_file:
        print(f"  Name corrections saved to: {os.path.abspath(corrections_file)}")
        
    print(f"{'-'*60}\n")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """Ask for user confirmation before performing an action.
    
    Args:
        prompt: Prompt text to display
        default: Default action if user presses Enter
        
    Returns:
        True if confirmed, False otherwise
    """
    default_text = " [Y/n]" if default else " [y/N]"
    response = input(f"{prompt}{default_text}: ").strip().lower()
    
    if not response:
        return default
    
    return response.startswith('y')


def show_spinner(seconds: int, message: str = "Processing"):
    """Show a spinner animation for a specified number of seconds.
    
    Args:
        seconds: Number of seconds to show the spinner
        message: Message to display with the spinner
    """
    spinner_chars = ['|', '/', '-', '\\']
    
    start_time = time.time()
    i = 0
    
    try:
        while time.time() - start_time < seconds:
            sys.stdout.write(f"\r{message} {spinner_chars[i % len(spinner_chars)]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
            
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
        sys.stdout.flush()
        raise
