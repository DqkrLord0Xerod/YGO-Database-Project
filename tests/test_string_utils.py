# tests/test_string_utils.py
import pytest
from yugioh_db_generator.utils.string_utils import (
    normalize_card_name,
    generate_name_variations,
    extract_tokens,
    find_distinctive_tokens,
    extract_archetype,
    clean_query_for_api
)

def test_normalize_card_name():
    # Test basic normalization
    assert normalize_card_name("Blue-Eyes White Dragon") == "blueeyes white dragon"
    
    # Test apostrophes and special characters
    assert normalize_card_name("Magicians' Soul") == "magicians soul"
    
    # Test diacritics and unicode characters
    assert normalize_card_name("Téa's Friendship") == "teas friendship"
    
    # Test extra spaces
    assert normalize_card_name("  Dark  Magician  ") == "dark magician"

def test_generate_name_variations():
    # Test basic variations
    variations = generate_name_variations("Snake-eye Flamberge Dragon")
    assert "Snake-eye Flamberge Dragon" in variations
    assert "Snake eye Flamberge Dragon" in variations
    assert "Snake-Eyes Flamberge Dragon" in variations
    
    # Test possessive variations
    variations = generate_name_variations("Magicians' Soul")
    assert "Magicians' Soul" in variations
    assert "Magicians Soul" in variations
    assert "Magician's Soul" in variations
    
    # Test specific archetype variations
    variations = generate_name_variations("Fiendsmith in Paradise")
    assert "Fiendsmith in Paradise" in variations
    assert "Fiendsmith's in Paradise" in variations

def test_extract_tokens():
    # Test basic tokenization
    tokens = extract_tokens("Blue-Eyes White Dragon")
    assert "blue" in tokens
    assert "eyes" in tokens
    assert "white" in tokens
    assert "dragon" in tokens
    
    # Test stopword removal
    tokens = extract_tokens("Chosen by the World Chalice")
    assert "chosen" in tokens
    assert "world" in tokens
    assert "chalice" in tokens
    assert "the" not in tokens
    assert "by" not in tokens

def test_find_distinctive_tokens():
    # Test finding distinctive tokens
    tokens = find_distinctive_tokens("Snake-eye Flamberge Dragon")
    assert "flamberge" in tokens
    assert "dragon" in tokens
    assert "snake" in tokens
    
    # Test minimum length filtering
    tokens = find_distinctive_tokens("Xyz Dragon Cannon", min_length=4)
    assert "dragon" in tokens
    assert "cannon" in tokens
    assert "xyz" not in tokens  # Too short with min_length=4
    
    tokens = find_distinctive_tokens("Xyz Dragon Cannon", min_length=2)
    assert "xyz" in tokens  # Now included with min_length=2

def test_extract_archetype():
    # Test archetype extraction
    assert extract_archetype("Snake-eye Flamberge Dragon") == "Snake-eye"
    assert extract_archetype("Crystal Beast Sapphire Pegasus") == "Crystal Beast"
    assert extract_archetype("Dark Magician") is None  # Not in the defined archetypes
    assert extract_archetype("World Legacy - \"World Chalice\"") == "World Legacy"

def test_clean_query_for_api():
    # Test cleaning queries
    assert clean_query_for_api("Blue-Eyes") == "Blue-Eyes"
    assert clean_query_for_api("Harpie's Feather Duster") == "Harpie%27s Feather Duster"
    assert clean_query_for_api("\"World Chalice\"") == "%22World Chalice%22"
    assert clean_query_for_api("Card & Effect") == "Card  Effect"  # Special chars removed
