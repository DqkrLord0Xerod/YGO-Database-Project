# tests/test_formatter.py
import pytest
from yugioh_db_generator.core.formatter import CardFormatter

def test_formatter_initialization():
    formatter = CardFormatter(format_type="markdown")
    assert formatter is not None
    assert formatter.format_type == "markdown"
    
    # Test with invalid format type (should default to markdown)
    formatter = CardFormatter(format_type="invalid")
    assert formatter.format_type == "markdown"

def test_not_found_formatting():
    formatter = CardFormatter(format_type="markdown")
    result = formatter._format_not_found("Test Card")
    
    # Check if the not found card is formatted correctly
    assert "Test Card" in result
    assert "Card information not found" in result