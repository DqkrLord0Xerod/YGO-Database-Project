"""API client for fetching Yu-Gi-Oh! banlist data."""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional


class BanlistAPI:
    """Client for fetching Yu-Gi-Oh! banlist data."""
    
    BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php?banlist=tcg"
    
    def __init__(self, cache_dir: str = None, use_cache: bool = True):
        """Initialize the banlist API client.
        
        Args:
            cache_dir: Directory to store cached banlist data
            use_cache: Whether to use cached data
        """
        self.logger = logging.getLogger(__name__)
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        
        # Create cache directory if it doesn't exist
        if self.use_cache and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            
        self.banlist_cache = {}
        self.cache_file = os.path.join(self.cache_dir, "banlist_cache.json") if self.cache_dir else None
    
    def get_banlist(self) -> Dict[str, str]:
        """Get the current TCG banlist.
        
        Returns:
            Dictionary mapping card names to their status
        """
        # Check if cache is already loaded
        if self.banlist_cache:
            return self.banlist_cache
            
        # Try to load from cache file
        if self.use_cache and self.cache_file and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.banlist_cache = json.load(f)
                    self.logger.info(f"Loaded banlist data from cache ({len(self.banlist_cache)} cards)")
                    return self.banlist_cache
            except Exception as e:
                self.logger.warning(f"Error loading banlist cache: {e}")
        
        # Fetch from API
        try:
            response = requests.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            self.banlist_cache = {}
            for card in data.get('data', []):
                card_name = card['name']
                ban_info = card.get('banlist_info', {}).get('ban_tcg', 'Unlimited')
                self.banlist_cache[card_name] = ban_info
                
            self.logger.info(f"Fetched banlist data from API ({len(self.banlist_cache)} cards)")
            
            # Cache the results
            self._save_cache()
            
            return self.banlist_cache
            
        except Exception as e:
            self.logger.error(f"Error fetching banlist data: {e}")
            return {}
    
    def get_card_status(self, card_name: str) -> str:
        """Get the limitation status for a specific card.
        
        Args:
            card_name: Name of the card to check
            
        Returns:
            Status ('Forbidden', 'Limited', 'Semi-Limited', 'Unlimited')
        """
        # Make sure banlist is loaded
        if not self.banlist_cache:
            self.get_banlist()
            
        # Get status from cache
        status = self.banlist_cache.get(card_name, 'Unlimited')
        
        # Convert API return values to standard format
        status_map = {
            "Banned": "Forbidden",
            "Limited": "Limited",
            "Semi-Limited": "Semi-Limited",
            "Unlimited": "Unlimited"
        }
        
        return status_map.get(status, "Unlimited")
    
    def clear_cache(self):
        """Clear the banlist cache."""
        self.banlist_cache = {}
        
        # Remove cache file if it exists
        if self.cache_file and os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
                self.logger.info("Banlist cache cleared")
            except Exception as e:
                self.logger.warning(f"Error clearing banlist cache file: {e}")
    
    def _save_cache(self):
        """Save the banlist cache to a file."""
        if not self.use_cache or not self.cache_file:
            return
            
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.banlist_cache, f)
                self.logger.debug(f"Saved banlist cache ({len(self.banlist_cache)} cards)")
        except Exception as e:
            self.logger.warning(f"Error saving banlist cache: {e}")
