# tests/test_integration.py
import os
import pytest
import tempfile
import json
import csv
from unittest.mock import patch, MagicMock

from yugioh_db_generator.core.card_database import CardDatabaseGenerator
from yugioh_db_generator.api.card_api import YGOPRODeckAPI
from yugioh_db_generator.utils.file_utils import read_deck_list, write_corrections


class MockAPIResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self.json_data = json_data or {}
        
    def json(self):
        return self.json_data
        
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP Error: {self.status_code}")


@pytest.fixture
def mock_api_data():
    """Create mock card data for testing."""
    return {
        "Dark Magician": {
            "name": "Dark Magician",
            "type": "Normal Monster",
            "attribute": "DARK",
            "level": 7,
            "atk": 2500,
            "def": 2100,
            "desc": "The ultimate wizard in terms of attack and defense.",
            "race": "Spellcaster"
        },
        "Blue-Eyes White Dragon": {
            "name": "Blue-Eyes White Dragon",
            "type": "Normal Monster",
            "attribute": "LIGHT",
            "level": 8,
            "atk": 3000,
            "def": 2500,
            "desc": "This legendary dragon is a powerful engine of destruction.",
            "race": "Dragon"
        },
        "Pot of Greed": {
            "name": "Pot of Greed",
            "type": "Spell Card",
            "desc": "Draw 2 cards.",
            "race": "Normal"
        },
        "Mirror Force": {
            "name": "Mirror Force",
            "type": "Trap Card",
            "desc": "When an opponent's monster declares an attack: Destroy all your opponent's Attack Position monsters.",
            "race": "Normal"
        }
    }


@pytest.fixture
def sample_deck_list():
    """Create a sample deck list file for testing."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, 'w') as f:
        f.write("# Main Deck\n")
        f.write("Dark Magician\n")
        f.write("Blue-Eyes White Dragon\n")
        f.write("Pot of Greed\n")
        f.write("Mirror Force\n")
        f.write("# This is a comment\n")
        f.write("Misspelled Crad Name\n")  # Intentional misspelling
    return path


@pytest.fixture
def cleanup():
    """Fixture to clean up temporary files after tests."""
    temp_files = []
    
    def _record_file(file_path):
        temp_files.append(file_path)
        return file_path
        
    yield _record_file
    
    # Clean up after tests
    for file_path in temp_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


@patch('yugioh_db_generator.api.card_api.requests.get')
def test_end_to_end_markdown(mock_get, mock_api_data, sample_deck_list, cleanup):
    """Test the entire workflow with Markdown output."""
    # Mock API responses
    def mock_api_response(*args, **kwargs):
        url = args[0]
        if "name=Dark%20Magician" in url:
            return MockAPIResponse(json_data={"data": [mock_api_data["Dark Magician"]]})
        elif "name=Blue-Eyes%20White%20Dragon" in url:
            return MockAPIResponse(json_data={"data": [mock_api_data["Blue-Eyes White Dragon"]]})
        elif "name=Pot%20of%20Greed" in url:
            return MockAPIResponse(json_data={"data": [mock_api_data["Pot of Greed"]]})
        elif "name=Mirror%20Force" in url:
            return MockAPIResponse(json_data={"data": [mock_api_data["Mirror Force"]]})
        elif "cardinfo.php?" in url and "fname=" in url:
            # Handle fuzzy search
            query = url.split("fname=")[1]
            if "miss" in query.lower() or "crad" in query.lower():
                # Return an empty result for misspelled card
                return MockAPIResponse(json_data={"data": []})
            else:
                # Return all cards for other searches
                return MockAPIResponse(json_data={"data": list(mock_api_data.values())})
        elif url.endswith("cardinfo.php"):
            # Return all cards for full database request
            return MockAPIResponse(json_data={"data": list(mock_api_data.values())})
        else:
            return MockAPIResponse(status_code=404)
    
    mock_get.side_effect = mock_api_response
    
    # Set up output files
    output_file = cleanup(tempfile.mkstemp(suffix=".md")[1])
    corrections_file = cleanup(tempfile.mkstemp(suffix=".txt")[1])
    
    # Create and run the generator
    generator = CardDatabaseGenerator(
        output_file=output_file,
        output_format="markdown",
        max_workers=1,  # Sequential for predictable testing
        cache_dir=None,
        use_cache=False
    )
    
    deck_list = read_deck_list(sample_deck_list)
    generator.generate_database(deck_list)
    
    # Check that output file was created and contains expected content
    assert os.path.exists(output_file)
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Verify the content
    assert "# Yu-Gi-Oh! Card Database" in content
    assert "## Dark Magician" in content
    assert "## Blue-Eyes White Dragon" in content
    assert "## Pot of Greed" in content
    assert "## Mirror Force" in content
    assert "## Misspelled Crad Name" in content
    assert "Card information not found" in content  # For the misspelled card
    
    # Check corrections
    corrections = generator.get_name_corrections()
    assert len(corrections) == 0  # No corrections in this test case


@patch('yugioh_db_generator.api.card_api.requests.get')
def test_end_to_end_json(mock_get, mock_api_data, sample_deck_list, cleanup):
    """Test the entire workflow with JSON output."""
    # Set up the same mock API as before
    mock_get.side_effect = lambda *args, **kwargs: MockAPIResponse(
        json_data={"data": list(mock_api_data.values())}
    )
    
    # Set up output file
    output_file = cleanup(tempfile.mkstemp(suffix=".json")[1])
    
    # Create and run the generator
    generator = CardDatabaseGenerator(
        output_file=output_file,
        output_format="json",
        max_workers=1,
        cache_dir=None,
        use_cache=False
    )
    
    deck_list = read_deck_list(sample_deck_list)
    generator.generate_database(deck_list)
    
    # Check that output file was created
    assert os.path.exists(output_file)
    
    # Verify the JSON content
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    assert data["title"] == "Yu-Gi-Oh! Card Database"
    assert len(data["cards"]) >= 5  # 5 cards from the deck list
    
    # Check specific cards
    card_names = [card["name"] for card in data["cards"]]
    assert "Dark Magician" in card_names
    assert "Blue-Eyes White Dragon" in card_names
    assert "Pot of Greed" in card_names
    assert "Mirror Force" in card_names
    assert "Misspelled Crad Name" in card_names


@patch('yugioh_db_generator.api.card_api.requests.get')
def test_end_to_end_csv(mock_get, mock_api_data, sample_deck_list, cleanup):
    """Test the entire workflow with CSV output."""
    # Set up the same mock API as before
    mock_get.side_effect = lambda *args, **kwargs: MockAPIResponse(
        json_data={"data": list(mock_api_data.values())}
    )
    
    # Set up output file
    output_file = cleanup(tempfile.mkstemp(suffix=".csv")[1])
    
    # Create and run the generator
    generator = CardDatabaseGenerator(
        output_file=output_file,
        output_format="csv",
        max_workers=1,
        cache_dir=None,
        use_cache=False
    )
    
    deck_list = read_deck_list(sample_deck_list)
    generator.generate_database(deck_list)
    
    # Check that output file was created
    assert os.path.exists(output_file)
    
    # Verify the CSV content
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) >= 5  # 5 cards from the deck list
    
    # Check that all expected columns are present
    expected_columns = ['Name', 'Type', 'Property', 'Description', 'Limitation', 
                       'Attribute', 'Level/Rank/Link', 'Monster Type', 'ATK', 'DEF']
    for column in expected_columns:
        assert column in rows[0]
    
    # Check specific cards
    card_names = [row['Name'] for row in rows]
    assert "Dark Magician" in card_names
    assert "Blue-Eyes White Dragon" in card_names
    assert "Pot of Greed" in card_names
    assert "Mirror Force" in card_names


@patch('yugioh_db_generator.api.card_api.requests.get')
def test_name_corrections_workflow(mock_get, mock_api_data, cleanup):
    """Test the name correction workflow."""
    # Mock API to correct "Drak Magician" to "Dark Magician"
    def mock_api_response(*args, **kwargs):
        url = args[0]
        if "name=Drak%20Magician" in url:
            return MockAPIResponse(json_data={"data": []})  # Not found by exact name
        elif "fname=Drak" in url or "fname=Magician" in url:
            # Return Dark Magician for fuzzy search
            return MockAPIResponse(json_data={"data": [mock_api_data["Dark Magician"]]})
        elif url.endswith("cardinfo.php"):
            # Return all cards for full database request
            return MockAPIResponse(json_data={"data": list(mock_api_data.values())})
        else:
            return MockAPIResponse(status_code=404)
    
    mock_get.side_effect = mock_api_response
    
    # Set up temporary files
    output_file = cleanup(tempfile.mkstemp(suffix=".md")[1])
    corrections_file = cleanup(tempfile.mkstemp(suffix=".txt")[1])
    
    # Create and run the generator
    generator = CardDatabaseGenerator(
        output_file=output_file,
        output_format="markdown",
        max_workers=1,
        cache_dir=None,
        use_cache=False
    )
    
    # Process a deck list with misspelled name
    deck_list = ["Drak Magician"]
    generator.generate_database(deck_list)
    
    # Check corrections
    corrections = generator.get_name_corrections()
    assert len(corrections) == 1
    assert "Drak Magician" in corrections
    assert corrections["Drak Magician"] == "Dark Magician"
    
    # Test writing corrections to file
    write_corrections(corrections, corrections_file)
    assert os.path.exists(corrections_file)
    
    with open(corrections_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Drak Magician -> Dark Magician" in content
