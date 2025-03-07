# Yu-Gi-Oh! Card Database Generator

A powerful tool to generate comprehensive card information for Yu-Gi-Oh! deck lists.

## Features

- **Flexible Input:** Process card lists from files or command line
- **Intelligent Card Matching:** Uses advanced fuzzy search to find cards with spelling variations
- **Customizable Output:** Generate card data in different formats (Markdown, JSON, CSV)
- **Parallel Processing:** Efficiently process large deck lists using multiple threads
- **Offline Support:** Cache card data for faster subsequent runs
- **Corrected Names Report:** Generates a report of cards that needed name correction

## Installation

```bash
# Install from PyPI
pip install yugioh-db-generator

# Or install from source
git clone https://github.com/yourusername/yugioh-db-generator.git
cd yugioh-db-generator
pip install -e .
```

## Usage

### Command Line

```bash
# Basic usage with a deck list file
yugioh-db-generator --input my_deck.txt

# Specify output file and format
yugioh-db-generator --input my_deck.txt --output my_database.md --format markdown

# Generate a name correction report
yugioh-db-generator --input my_deck.txt --corrections corrected_names.txt

# Use multiple threads for faster processing
yugioh-db-generator --input my_deck.txt --threads 8
```

### As a Python Module

```python
from yugioh_db_generator import CardDatabaseGenerator

# Initialize the generator
generator = CardDatabaseGenerator()

# Process a deck list
deck_list = [
    "Blue-Eyes White Dragon",
    "Dark Magician",
    "Pot of Greed"
]

# Generate the database
generator.generate_database(deck_list, output_file="cards.md")

# Get a list of corrected names
corrections = generator.get_name_corrections()
print(corrections)
```

## Input Formats

The tool accepts deck lists in the following formats:

### Plain Text (one card per line)
```
Blue-Eyes White Dragon
Dark Magician
Pot of Greed
```

### YDK Format (exported from YGOPro)
```
#main
12345678
87654321
#extra
56781234
...
```

## Output Formats

- **Markdown**: Formatted card information with sections (default)
- **JSON**: Machine-readable data format
- **CSV**: Spreadsheet-compatible format
- **Text**: Simple text format

## License

MIT License
