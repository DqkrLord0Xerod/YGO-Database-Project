"""File utilities for the Yu-Gi-Oh! Card Database Generator."""

import os
import re
import logging
from typing import List, Dict, Optional


logger = logging.getLogger(__name__)


def read_deck_list(filename: str) -> List[str]:
    """Read a deck list from a file."""
    if not os.path.exists(filename):
        logger.error(f"File not found: {filename}")
        return []
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Better format detection
        if content.strip().startswith('#main') or content.strip().startswith('#created by'):
            return _parse_ydk_file(filename)  # Only for actual YDK files
        else:
            return _parse_text_file(filename)  # Plain text with possible comments
            
    except Exception as e:
        logger.error(f"Error reading deck list: {e}")
        return []


def _parse_text_file(filename: str) -> List[str]:
    """Parse a plain text deck list file.
    
    Format: One card per line, comments start with '#'
    
    Args:
        filename: Path to the deck list file
        
    Returns:
        List of card names
    """
    cards = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                # Remove comments and whitespace
                line = line.split('#')[0].strip()
                if line:
                    cards.append(line)
        return cards
    except Exception as e:
        logger.error(f"Error parsing text file: {e}")
        return []


def _parse_ydk_file(filename: str) -> List[str]:
    """Parse a YDK deck list file.
    
    YDK Format:
    #main
    <card_id>
    <card_id>
    ...
    #extra
    <card_id>
    ...
    
    Args:
        filename: Path to the YDK file
        
    Returns:
        List of card names (empty if YDK parsing is not implemented)
    """
    # YDK files contain card IDs, not names
    # We would need to lookup names using the IDs
    logger.warning("YDK format parsing requires card ID to name mapping, which is not implemented yet")
    logger.warning("Please convert your YDK file to a plain text file with one card name per line")
    return []


def write_corrections(corrections: Dict[str, str], filename: str) -> None:
    """Write card name corrections to a file.
    
    Args:
        corrections: Dictionary mapping original names to corrected names
        filename: Path to the output file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Yu-Gi-Oh! Card Name Corrections\n")
            f.write("# Original Name -> Corrected Name\n\n")
            
            for original, corrected in sorted(corrections.items()):
                f.write(f"{original} -> {corrected}\n")
                
        logger.info(f"Wrote {len(corrections)} corrections to {filename}")
    except Exception as e:
        logger.error(f"Error writing corrections file: {e}")


def get_default_deck_list() -> List[str]:
    """Get the default deck list."""
    return [
        # Main Deck
        "Snake-eye Flamberge Dragon", "Snake-eye Diabellstar", "Snake-eye Ash", 
        "Snake-eye Oak", "Snake-eye Poplar", "Snake-eye Birch", 
        "Fabled Lurrie", "Lacrima the Crimson Tear", "Fiendsmith Engraver", 
        "Fiendsmith in Paradise", "Fiendsmith Kyrie", "Rainbow Dragon", 
        "Crystal Beast Rainbow Dragon", "Crystal Beast Sapphire Pegasus", 
        "Crystal Beast Cobalt Eagle", "Crystal Beast Ruby Carbuncle", 
        "Magicians' Soul", "Illusion of Chaos", "Chaos Allure Queen", 
        "Allure Queen LV3", "Allure Queen LV5", "World Legacy - \"World Chalice\"", 
        "Chosen by the World Chalice", "Dragon Buster Destruction Sword", 
        "World Legacy - \"World Shield\"", "Dramatic Snake-eye Chase", 
        "Divine Temple of the Snake-eyes", "One for One", "Fiendsmith Tract", 
        "Rainbow Bridge", "Crystal Bond", "Golden Rule", 
        "Awakening of the Crystal Ultimates", "Rainbow Bridge of the Heart", 
        "Foolish Burial Goods", "Called by the Grave", "Triple Tactics Thrust", 
        "Triple Tactics Talents", "Vaylantz World - Shinra Bansho", 
        "Vaylantz World - Konig Wissen", "World Legacy Succession", 
        "Rainbow Bridge of Salvation", "Harpies' Feather Storm", "Infinite Impermanence",
        # Extra Deck
        "Protector Whelp of the Destruction Swordsman", "Magisitus Chorozo", 
        "Necroquip Princess", "Snake-eye Doomed Dragon", "Gallant Granite", 
        "Infernal Flame Banshee", "D/D/D Wave High King Caesar", 
        "Moon of the Closed Heaven", "Mekk-Knight Crusadia Avramax", 
        "I:P Masquerena", "Relinquished Anima", "Knightmare Gryphon", 
        "A Bao A Qu, The Lightless Shadow", "Cross-Sheep", "Fiendsmith Requiem", 
        "Fiendsmith Agnumday", "Fiendsmith Sequence", "Fiendsmith Desirae", 
        "Ib the World Chalice Justiciar", "Rciela Sinister Soul of the White Forest", 
        "Power Tool Dragon", "Cherubini, Ebon Angel of the Burning Abyss"
    ]


def ensure_dir_exists(dir_path: str) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to the directory
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.debug(f"Created directory: {dir_path}")
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
