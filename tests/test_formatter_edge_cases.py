# tests/test_formatter_edge_cases.py
import pytest
from unittest.mock import patch, MagicMock
from yugioh_db_generator.core.formatter import CardFormatter

def test_formatter_with_empty_data():
    """Test formatter with empty or none data."""
    formatter = CardFormatter(format_type="markdown")
    
    # Test with None data
    result = formatter.format_card(None, "Test Card")
    assert "Test Card" in result
    assert "Card information not found" in result
    
    # Test with empty dictionary
    result = formatter.format_card({}, "Test Card")
    assert "Test Card" in result
    
    # Test database formatting with empty list
    result = formatter.format_database([])
    assert "Yu-Gi-Oh! Card Database" in result
    assert len(result) < 50  # Should be just the title with no card data

def test_formatter_extreme_values():
    """Test formatter with extreme or unusual values."""
    formatter = CardFormatter(format_type="markdown")
    
    # Test with extremely long card name
    long_name = "Super Extremely Fantastically Unbelievably Ridiculously " * 5 + "Long Card Name"
    result = formatter.format_card({"type": "Monster", "desc": "Test description"}, long_name)
    assert long_name in result
    
    # Test with unusual numeric values
    unusual_card = {
        "type": "Monster",
        "desc": "Test description",
        "atk": -1000,
        "def": 9999999,
        "level": 0
    }
    result = formatter.format_card(unusual_card, "Unusual Card")
    assert "-1000/9999999" in result
    assert "Level 0" in result
    
    # Test with unusual characters in card text
    unusual_text = {
        "type": "Monster",
        "desc": "Test description with unusual characters: ♥♦♣♠ αβγδ 你好世界"
    }
    result = formatter.format_card(unusual_text, "Unicode Card")
    assert "♥♦♣♠" in result
    assert "αβγδ" in result
    assert "你好世界" in result

def test_json_format_special_cases():
    """Test JSON formatter with special cases."""
    formatter = CardFormatter(format_type="json")
    
    # Test with minimal data
    minimal_card = {"name": "Minimal Card", "desc": "Just the basics"}
    result = formatter.format_card(minimal_card, "Minimal Card")
    assert result["name"] == "Minimal Card"
    assert result["text"] == "Just the basics"
    assert "cardType" in result
    
    # Test with list values
    list_card = {
        "name": "List Card", 
        "desc": "Card with list values",
        "type": ["Monster", "Effect"],
        "attribute": ["DARK", "LIGHT"]
    }
    result = formatter.format_card(list_card, "List Card")
    assert isinstance(result["property"], str)  # Should convert list to string
    
    # Test database formatting
    cards = [
        formatter.format_card({"name": "Card 1", "desc": "Description 1"}, "Card 1"),
        formatter.format_card({"name": "Card 2", "desc": "Description 2"}, "Card 2")
    ]
    result = formatter.format_database(cards, "Test Database")
    import json
    parsed = json.loads(result)
    assert parsed["title"] == "Test Database"
    assert len(parsed["cards"]) == 2

def test_csv_format_handling():
    """Test CSV formatter handling of special cases."""
    formatter = CardFormatter(format_type="csv")
    
    # Test with basic monster card
    monster_card = {
        "name": "Test Monster",
        "type": "Effect Monster",
        "attribute": "LIGHT",
        "level": 4,
        "atk": 1500,
        "def": 1200,
        "desc": "This is a test monster card."
    }
    result = formatter.format_card(monster_card, "Test Monster")
    assert result["Name"] == "Test Monster"
    assert result["Level/Rank/Link"] == "Level 4"
    assert result["ATK"] == "1500"  # Should be converted to string
    
    # Test with spell card (should have N/A for monster-specific fields)
    spell_card = {
        "name": "Test Spell",
        "type": "Spell Card",
        "desc": "This is a test spell card."
    }
    result = formatter.format_card(spell_card, "Test Spell")
    assert result["Type"] == "Spell"
    assert result["Attribute"] == "N/A"
    assert result["ATK"] == "N/A"
    
    # Test database formatting with mixed card types
    cards = [
        formatter.format_card(monster_card, "Test Monster"),
        formatter.format_card(spell_card, "Test Spell")
    ]
    result = formatter.format_database(cards)
    
    # Updated test to account for OfficialRulings column
    # Check for essential columns - don't rely on exact order
    assert "Name" in result
    assert "Type" in result
    assert "Property" in result 
    assert "Description" in result
    assert "Limitation" in result
    assert "Attribute" in result
    assert "Level/Rank/Link" in result
    assert "Monster Type" in result
    assert "ATK" in result
    assert "DEF" in result
    assert "OfficialRulings" in result  # This field is now expected
    
    # Also check for actual data
    assert "Test Monster,Monster" in result
    assert "Test Spell,Spell" in result