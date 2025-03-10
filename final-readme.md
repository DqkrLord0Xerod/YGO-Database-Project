# Yu-Gi-Oh! Card Database Generator

A professional-grade tool for generating comprehensive card information databases from Yu-Gi-Oh! deck lists. This modular Python package uses advanced search techniques to find accurate card information even with spelling variations and name inconsistencies.

## Features

- **Smart Card Matching**: Uses multi-level fuzzy search to correctly identify cards even with spelling variations
- **Flexible Input/Output**: Process card lists from files or command line with multiple output formats
- **Name Correction Reports**: Generates reports of card names that needed correction for reference
- **Parallel Processing**: Efficiently processes large deck lists using multiple threads
- **Robust Error Handling**: Gracefully handles API failures, card not found, and other issues
- **Caching System**: Reduces API calls by caching card data and search results
- **Multiple Output Formats**: Generate databases in Markdown, JSON, CSV or plain text

## Installation

### From PyPI (Recommended)

```bash
pip install yugioh-db-generator
```

### From Source

```bash
git clone https://github.com/yourusername/yugioh-db-generator.git
cd yugioh-db-generator
pip install -e .
```

## Quick Start

### Command Line Usage

Generate a database from a deck list file:

```bash
yugioh-db-generator --input my_deck.txt
```

Specify output format and file:

```bash
yugioh-db-generator --input my_deck.txt --output my_database.json --format json
```

Generate a name correction report:

```bash
yugioh-db-generator --input my_deck.txt --corrections corrected_names.txt
```

### Python Module Usage

```python
from yugioh_db_generator import CardDatabaseGenerator

# Initialize the generator
generator = CardDatabaseGenerator(
    output_file="cards.md",
    output_format="markdown",
    max_workers=4
)

# Process a deck list
deck_list = [
    "Snake-eye Flamberge Dragon",
    "Dark Magician",
    "Blue-Eyes White Dragon"
]

# Generate the database
generator.generate_database(deck_list)

# Get name corrections
corrections = generator.get_name_corrections()
print(corrections)
```

## Input Format

The generator accepts deck lists in plain text format with one card per line:

```
# Main Deck
Snake-eye Flamberge Dragon
Dark Magician
Blue-Eyes White Dragon

# Extra Deck
Stardust Dragon
Number 39: Utopia
```

Lines starting with `#` are treated as comments.

## Output Formats

### Markdown (Default)

```markdown
## Snake-Eyes Flamberge Dragon
Basic Information
* **Card Type**: Monster
* **Property**: Effect
* **Attribute**: FIRE
* **Level/Rank/Link Rating**: Level 8
* **Type**: Dragon
* **ATK/DEF**: 2500/2000
* **Limitation Status**: Unlimited

Card Text
If this card is Normal or Special Summoned: You can add 1 "Snake-eye" card...

Card Rulings & Interactions
* The "once per turn" effect(s) of Snake-Eyes Flamberge Dragon reset if the card leaves the field and returns.
* Effects that prevent targeting will prevent Snake-Eyes Flamberge Dragon from selecting those cards as targets.
```

### JSON

```json
{
  "title": "Yu-Gi-Oh! Card Database",
  "cards": [
    {
      "name": "Snake-eye Flamberge Dragon",
      "originalName": "Snake-eye Flamberge Dragon", 
      "matchedName": "Snake-Eyes Flamberge Dragon",
      "cardType": "Monster",
      "property": "Effect",
      "text": "If this card is Normal or Special Summoned: You can add 1 \"Snake-eye\" card...",
      "limitation": "Unlimited",
      "attribute": "FIRE",
      "level": "Level 8",
      "type": "Dragon",
      "atk": 2500,
      "def": 2000,
      "rulings": [
        "The \"once per turn\" effect(s) of Snake-eye Flamberge Dragon reset if the card leaves the field and returns."
      ]
    }
  ]
}
```

### CSV

```csv
Name,Type,Property,Attribute,Level/Rank/Link,Monster Type,ATK,DEF,Description,Limitation
Snake-eye Flamberge Dragon,Monster,Effect,FIRE,Level 8,Dragon,2500,2000,"If this card is Normal or Special Summoned: You can add 1 ""Snake-eye"" card...",Unlimited
```

## Advanced Usage

### Command Line Options

```
usage: yugioh-db-generator [-h] [--input INPUT] [--output OUTPUT]
                          [--format {markdown,json,csv,text}]
                          [--corrections CORRECTIONS] [--threads THREADS]
                          [--cache-dir CACHE_DIR] [--no-cache] [--clear-cache]
                          [--similarity-threshold SIMILARITY_THRESHOLD]
                          [--verbose] [--version]

Generate a comprehensive Yu-Gi-Oh! card database from a deck list

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Path to the input file containing card names (one per
                        line) (default: None)
  --output OUTPUT, -o OUTPUT
                        Path to the output file for the generated database
                        (default: yugioh_card_database.md)
  --format {markdown,json,csv,text}, -f {markdown,json,csv,text}
                        Output format for the database (default: markdown)
  --corrections CORRECTIONS, -c CORRECTIONS
                        Path to save a list of corrected card names (default:
                        None)
  --threads THREADS, -t THREADS
                        Number of threads for parallel processing (default: 4)
  --cache-dir CACHE_DIR
                        Directory to store cached card data (default:
                        ~/.yugioh_db_generator/cache)
  --no-cache            Disable using cached data (always fetch from API)
                        (default: False)
  --clear-cache         Clear the cache before running (default: False)
  --similarity-threshold SIMILARITY_THRESHOLD
                        Minimum similarity score for fuzzy matching (0.0-1.0)
                        (default: 0.7)
  --verbose, -v         Increase verbosity (can be used multiple times)
                        (default: 0)
  --version             Show the version and exit (default: False)
```

## Project Structure

```
yugioh_db_generator/
├── README.md                       # Project documentation
├── requirements.txt                # Project dependencies
├── setup.py                        # Package installation script
├── example_decklist.txt            # Example deck list file
├── yugioh_db_generator/            # Main package directory
│   ├── __init__.py                 # Package initialization
│   ├── __main__.py                 # Entry point for command-line usage
│   ├── api/                        # API interaction modules
│   │   ├── __init__.py
│   │   ├── card_api.py             # YGOPRODeck API client
│   │   └── banlist_api.py          # Banlist data fetching
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── card_database.py        # Card database management
│   │   ├── search_engine.py        # Advanced search algorithms
│   │   └── formatter.py            # Output formatting logic
│   ├── utils/                      # Utility functions
│   │   ├── __init__.py
│   │   ├── file_utils.py           # File reading/writing utilities
│   │   ├── logging_utils.py        # Logging configuration
│   │   └── string_utils.py         # String manipulation utilities
│   └── cli/                        # Command-line interface
│       ├── __init__.py
│       ├── parser.py               # Command-line argument parsing
│       └── interface.py            # User interface functions
```

## Extending the Project

### Adding New Output Formats

To add a new output format, modify the `CardFormatter` class in `formatter.py`:

1. Add your format to the `formatters` dictionary in `__init__`
2. Create a new method `_format_myformat` that formats card data
3. Update the `format_database` method to handle your format

### Adding New Card Sources

To support a new card database:

1. Create a new API client in the `api/` directory
2. Update the `CardDatabaseGenerator` to use your new API client
3. Modify the search engine to handle the new data format

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Data provided by the [YGOPRODeck API](https://db.ygoprodeck.com/api-guide/)
- Originally inspired by a command-line script for generating Yu-Gi-Oh! card databases
