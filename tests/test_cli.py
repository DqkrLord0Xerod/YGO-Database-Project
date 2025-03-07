# tests/test_cli.py
import pytest
from unittest.mock import patch, MagicMock
import sys
from yugioh_db_generator.__main__ import main
from yugioh_db_generator.cli.parser import create_parser

def test_parser_creation():
    parser = create_parser()
    assert parser is not None
    
    # Test basic argument parsing
    args = parser.parse_args(['--output', 'test.md'])
    assert args.output == 'test.md'
    assert args.format == 'markdown'  # Default value