"""String manipulation utilities for Yu-Gi-Oh! Card Database Generator."""

import re
import unicodedata
from typing import List, Optional, Tuple


def normalize_card_name(card_name: str) -> str:
    """Normalize a card name for comparison and searching.
    
    Removes special characters, apostrophes, and converts to lowercase.
    
    Args:
        card_name: The card name to normalize
        
    Returns:
        Normalized card name
    """
    # Convert to lowercase
    name = card_name.lower()
    
    # Remove special characters and apostrophes
    name = re.sub(r"['\",\-]", "", name)
    
    # Remove additional spaces
    name = re.sub(r"\s+", " ", name).strip()
    
    # Normalize unicode characters
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    
    return name


def generate_name_variations(card_name: str) -> List[str]:
    """Generate common variations of a card name.
    
    Args:
        card_name: The original card name
        
    Returns:
        List of possible name variations
    """
    variations = [
        card_name,  # Original name
        card_name.replace("-", " "),  # Replace hyphens with spaces
        card_name.replace("'s", ""),  # Remove possessive
        card_name.replace("'", ""),   # Remove apostrophes
    ]
    
    # Add specific alternative spellings for known variations
    name_variants = [
        ("Snake-eye", "Snake-Eyes"),
        ("Harpies'", "Harpie's"),
        ("Magicians'", "Magician's"),
        ("Magisitus", "Magistus"),
        ("Fiendsmith", "Fiendsmith's"),
        ("Rciela Sinister Soul", "Rciela, Sinister Soul")
    ]
    
    for search, replace in name_variants:
        if search in card_name:
            variations.append(card_name.replace(search, replace))
    
    return variations


def extract_tokens(card_name: str) -> List[str]:
    """Extract meaningful tokens from a card name.
    
    Args:
        card_name: The card name to tokenize
        
    Returns:
        List of tokens
    """
    # Extract words, ignoring common words
    tokens = re.findall(r'\b\w+\b', card_name.lower())
    
    # Common words to ignore in tokenization
    stop_words = {'the', 'of', 'a', 'an', 'in', 'and', 'to', 'with', 'by', 'from'}
    
    return [token for token in tokens if token not in stop_words]


def find_distinctive_tokens(card_name: str, min_length: int = 3) -> List[str]:
    """Find the most distinctive tokens in a card name.
    
    Args:
        card_name: The card name to analyze
        min_length: Minimum length for a token to be considered distinctive
        
    Returns:
        List of distinctive tokens, sorted by importance
    """
    tokens = extract_tokens(card_name)
    
    # Filter by length and sort by length (longer tokens are generally more distinctive)
    distinctive = [token for token in tokens if len(token) >= min_length]
    distinctive.sort(key=len, reverse=True)
    
    return distinctive


def extract_archetype(card_name: str) -> Optional[str]:
    """Extract a possible archetype from a card name.
    
    Args:
        card_name: The card name to analyze
        
    Returns:
        Extracted archetype if found, None otherwise
    """
    # Common archetypes
    archetypes = [
        "Snake-eye", "Snake-Eyes", 
        "Crystal Beast", 
        "Fiendsmith", "Fiendsmith's",
        "World Legacy", "World Chalice",
        "Allure Queen",
        "Vaylantz"
    ]
    
    # Check for archetype in name
    for archetype in archetypes:
        if archetype.lower() in card_name.lower():
            return archetype
    
    return None


def clean_query_for_api(query: str) -> str:
    """Clean a query string for API requests.
    
    Args:
        query: The query string to clean
        
    Returns:
        Cleaned query string
    """
    # Replace special characters that cause API issues
    clean = query.replace("'", "%27").replace('"', '%22')
    
    # Remove characters that might break the API call
    clean = re.sub(r'[^\w\s%\-]', '', clean)
    
    return clean.strip()
