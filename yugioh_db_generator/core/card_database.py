"""Core functionality for generating Yu-Gi-Oh! card databases."""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from yugioh_db_generator.api.card_api import YGOPRODeckAPI
from yugioh_db_generator.core.search_engine import CardSearchEngine
from yugioh_db_generator.core.formatter import CardFormatter


class CardDatabaseGenerator:
    """Main class for generating Yu-Gi-Oh! card databases."""
    
    def __init__(
        self, 
        output_file: str = "yugioh_card_database.md",
        output_format: str = "markdown",
        max_workers: int = 4,
        cache_dir: str = None,
        use_cache: bool = True,
        similarity_threshold: float = 0.7, 
        rulings_db_path: str = "konami_rulings.json"
    ):
        """Initialize the database generator.
        
        Args:
            output_file: Path to the output file
            output_format: Format for the output ('markdown', 'json', 'csv', or 'text')
            max_workers: Number of threads for parallel processing
            cache_dir: Directory to store cached API responses
            use_cache: Whether to use cached responses
            similarity_threshold: Minimum similarity score for fuzzy matching
        """
        self.logger = logging.getLogger(__name__)
        
        self.output_file = output_file
        self.output_format = output_format
        self.max_workers = max_workers
        
        # Initialize API client
        self.api_client = YGOPRODeckAPI(cache_dir=cache_dir, use_cache=use_cache)
        
        # Initialize search engine
        self.search_engine = CardSearchEngine(
            api_client=self.api_client,
            similarity_threshold=similarity_threshold
        )
        
        # Initialize formatter
        self.formatter = CardFormatter(
            format_type=output_format,
            konami_rulings_db=rulings_db_path  # Pass the rulings database path
        )        
        # Store processed cards
        self.processed_cards = {}
    
    def generate_database(self, deck_list: List[str]) -> None:
        """Generate a card database from a deck list.
        
        Args:
            deck_list: List of card names to process
        """
        self.logger.info(f"Generating database for {len(deck_list)} cards")
        
        # Clean up card names
        deck_list = [name.strip() for name in deck_list if name.strip()]
        
        # Process cards (parallel or sequential)
        if self.max_workers > 1:
            self._parallel_process(deck_list)
        else:
            self._sequential_process(deck_list)
        
        # Format and save the database
        self._save_database()
        
        self.logger.info(f"Database saved to: {self.output_file}")
    
    def _parallel_process(self, deck_list: List[str]) -> None:
        """Process cards in parallel using multiple threads."""
        self.logger.info(f"Processing cards using {self.max_workers} threads")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a future for each card
            futures = {}
            for i, card_name in enumerate(deck_list):
                future = executor.submit(self._process_card, card_name, i+1, len(deck_list))
                futures[future] = card_name
            
            # Process results as they complete
            for future in as_completed(futures):
                card_name = futures[future]
                try:
                    # Get the result (any exceptions will be raised here)
                    result = future.result()
                except Exception as e:
                    self.logger.error(f"Error processing card '{card_name}': {e}")
    
    def _sequential_process(self, deck_list: List[str]) -> None:
        """Process cards sequentially."""
        for i, card_name in enumerate(deck_list):
            try:
                self._process_card(card_name, i+1, len(deck_list))
                # Small delay to avoid hammering the API
                time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"Error processing card '{card_name}': {e}")
    
    def _process_card(self, card_name: str, current: int, total: int) -> Dict[str, Any]:
        """Process a single card.
        
        Args:
            card_name: Name of the card to process
            current: Current card number (for progress reporting)
            total: Total number of cards (for progress reporting)
            
        Returns:
            Processed card data
        """
        self.logger.info(f"Processing card {current}/{total}: {card_name}")
        
        # Search for the card
        card_data = self.search_engine.search(card_name)
        
        # Format the card data
        formatted_card = self.formatter.format_card(card_data, card_name)
        
        # Store the processed card
        self.processed_cards[card_name] = {
            'data': card_data,
            'formatted': formatted_card
        }
        
        return self.processed_cards[card_name]
    
    def _save_database(self) -> None:
        """Format and save the complete database."""
        # Get the list of cards in order
        cards = list(self.processed_cards.keys())
        
        # Generate the complete database content
        content = self.formatter.format_database(
            cards=[self.processed_cards[card]['formatted'] for card in cards],
            title="Yu-Gi-Oh! Card Database"
        )
        
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.output_file)), exist_ok=True)
        
        # Write the content to the output file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_name_corrections(self) -> Dict[str, str]:
        """Get the mapping of original card names to corrected ones.
        
        Returns:
            Dictionary mapping original names to corrected names
        """
        return self.search_engine.get_name_corrections()
