# tests/test_api.py
import pytest
from unittest.mock import patch, MagicMock
from yugioh_db_generator.api.card_api import YGOPRODeckAPI

def test_api_initialization():
    api = YGOPRODeckAPI(cache_dir=None, use_cache=False)
    assert api is not None
    assert api.use_cache is False
    assert api.cache_dir is None

@patch('yugioh_db_generator.api.card_api.requests.get')
def test_get_card_by_name(mock_get):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'data': [{'name': 'Dark Magician', 'type': 'Effect Monster'}]
    }
    mock_get.return_value = mock_response
    
    # Test the API call
    api = YGOPRODeckAPI(cache_dir=None, use_cache=False)
    card = api.get_card_by_name('Dark Magician')
    
    # Assertions
    assert card is not None
    assert card['name'] == 'Dark Magician'
    mock_get.assert_called_once()