# tests/test_search.py
import pytest
from unittest.mock import patch, MagicMock
from yugioh_db_generator.core.search_engine import CardSearchEngine

def test_search_engine_initialization():
    api_client = MagicMock()
    search_engine = CardSearchEngine(api_client, similarity_threshold=0.8)
    assert search_engine is not None
    assert search_engine.similarity_threshold == 0.8
    assert search_engine.api_client == api_client

def test_correction_recording():
    api_client = MagicMock()
    search_engine = CardSearchEngine(api_client)
    
    # Test recording a correction
    search_engine._record_correction('Magisitus Chorozo', 'Magistus Chorozo')
    
    # Check if it was recorded correctly
    corrections = search_engine.get_name_corrections()
    assert 'Magisitus Chorozo' in corrections
    assert corrections['Magisitus Chorozo'] == 'Magistus Chorozo'