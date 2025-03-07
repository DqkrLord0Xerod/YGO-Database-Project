"""Module for fetching and managing official Konami rulings."""

import os
import json
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup


class KonamiRulingsDatabase:
    """Manages a database of official Konami rulings."""
    
    def __init__(self, db_path: str = "konami_rulings.json", cache_dir: Optional[str] = None):
        """Initialize the rulings database.
        
        Args:
            db_path: Path to save the rulings database
            cache_dir: Directory for caching ruling data
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self.cache_dir = cache_dir
        
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            
        self.rulings_db = {}
        
        # Load existing database if it exists
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.rulings_db = json.load(f)
                self.logger.info(f"Loaded {len(self.rulings_db)} card rulings from {self.db_path}")
            except Exception as e:
                self.logger.warning(f"Error loading rulings database: {e}")
    
    def get_rulings(self, card_name: str) -> List[str]:
        """Get official rulings for a card.
        
        Args:
            card_name: Name of the card to get rulings for
            
        Returns:
            List of ruling strings
        """
        # Check if we already have rulings for this card
        if card_name in self.rulings_db:
            return self.rulings_db[card_name]
        
        # Try fetching from Konami database
        rulings = self._fetch_rulings(card_name)
        
        # Save to database
        if rulings:
            self.rulings_db[card_name] = rulings
            self._save_database()
            
        return rulings
    
    def _fetch_rulings(self, card_name: str) -> List[str]:
        """Fetch rulings from Konami's database.
        
        This is a placeholder implementation. Konami doesn't provide a direct API
        for rulings, so actual implementation would require web scraping or
        using a community-maintained database.
        
        Args:
            card_name: Name of the card to fetch rulings for
            
        Returns:
            List of ruling strings
        """
        # This would need to be implemented based on available sources
        # Currently return an empty list as placeholder
        self.logger.info(f"No rulings found for {card_name}")
        return []
    
    def add_ruling(self, card_name: str, ruling: str) -> None:
        """Add a ruling to the database.
        
        Args:
            card_name: Name of the card
            ruling: Ruling text
        """
        if card_name not in self.rulings_db:
            self.rulings_db[card_name] = []
            
        if ruling not in self.rulings_db[card_name]:
            self.rulings_db[card_name].append(ruling)
            self._save_database()
    
    def add_rulings_from_file(self, file_path: str) -> int:
        """Add rulings from a JSON file.
        
        File format should be {card_name: [ruling1, ruling2, ...]}
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Number of cards with added rulings
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                rulings_data = json.load(f)
                
            count = 0
            for card_name, rulings in rulings_data.items():
                if card_name not in self.rulings_db:
                    self.rulings_db[card_name] = []
                    
                # Add new rulings
                for ruling in rulings:
                    if ruling not in self.rulings_db[card_name]:
                        self.rulings_db[card_name].append(ruling)
                        
                count += 1
                
            # Save the updated database
            self._save_database()
            self.logger.info(f"Added rulings for {count} cards from {file_path}")
            return count
            
        except Exception as e:
            self.logger.error(f"Error adding rulings from file: {e}")
            return 0
    
    def _save_database(self) -> None:
        """Save the rulings database to file."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.rulings_db, f, indent=2)
            self.logger.info(f"Saved rulings database with {len(self.rulings_db)} cards")
        except Exception as e:
            self.logger.error(f"Error saving rulings database: {e}")
    
    def clear_rulings(self, card_name: str) -> None:
        """Clear rulings for a specific card.
        
        Args:
            card_name: Name of the card to clear rulings for
        """
        if card_name in self.rulings_db:
            del self.rulings_db[card_name]
            self._save_database()
            self.logger.info(f"Cleared rulings for {card_name}")
    
    def clear_all_rulings(self) -> None:
        """Clear all rulings in the database."""
        self.rulings_db = {}
        self._save_database()
        self.logger.info("Cleared all rulings from database")


# Example import of rulings from a community database
def import_yugioh_wiki_rulings(output_file: str = "konami_rulings.json") -> None:
    """Import rulings from Yu-Gi-Oh! Wiki.
    
    This is a placeholder for demonstration. Actual implementation would
    require web scraping from sources with ruling information.
    
    Args:
        output_file: Path to save the rulings database
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting Yu-Gi-Oh! Wiki rulings import")
    
    # Sample data format - in a real implementation, this would be scraped
    sample_rulings = {
        "Dark Magician": [
            "If this card is Tributed for a Tribute Summon, it is not 'sent from the field to the Graveyard'.",
            "If this card is Tributed for 'Dedication through Light and Darkness', 'Dark Magic Attack' cannot be activated that turn."
        ],
        "Blue-Eyes White Dragon": [
            "Effects that respecify ATK/DEF values, like 'Shield & Sword', don't count as increasing or decreasing the ATK/DEF.",
            "This card can be Special Summoned with 'Ancient Rules'."
        ],
        "Pot of Greed": [
            "You cannot activate this card if there are fewer than 2 cards in your Deck.",
            "Both cards are drawn simultaneously, not one at a time."
        ]
    }
    
    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_rulings, f, indent=2)
        logger.info(f"Saved sample rulings for {len(sample_rulings)} cards to {output_file}")
    except Exception as e:
        logger.error(f"Error saving rulings: {e}")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    import_yugioh_wiki_rulings()
    
    # Initialize and test the database
    db = KonamiRulingsDatabase()
    
    # Add a custom ruling
    db.add_ruling("Mystical Space Typhoon", "This card does not negate the effects of cards it destroys.")
    
    # Print rulings for a card
    print(db.get_rulings("Dark Magician"))