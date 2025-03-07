"""API client for interacting with the YGOPRODeck API."""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import quote


class YGOPRODeckAPI:
    """Client for interacting with the YGOPRODeck API."""
    
    BASE_URL = "https://db.ygoprodeck.com/api/v7"
    CARD_INFO_ENDPOINT = "/cardinfo.php"
    SEARCH_ENDPOINT = "/cardinfo.php?fname={query}"
    RATE_LIMIT_DELAY = 0.1  # seconds between API calls
    
    def __init__(self, cache_dir: str = None, use_cache: bool = True):
        """Initialize the API client.
        
        Args:
            cache_dir: Directory to store cached responses
            use_cache: Whether to use cached responses
        """
        self.logger = logging.getLogger(__name__)
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        if self.use_cache and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Delay requests to respect API rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, endpoint: str) -> str:
        """Get the cache file path for an endpoint."""
        if not self.cache_dir:
            return None
            
        # Create a safe filename from the endpoint
        safe_name = endpoint.replace("/", "_").replace("?", "_").replace("=", "_")
        return os.path.join(self.cache_dir, f"{safe_name}.json")
    
    def _get_from_cache(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Get response from cache if available."""
        if not self.use_cache:
            return None
            
        cache_path = self._get_cache_path(endpoint)
        if not cache_path or not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Error reading from cache: {e}")
            return None
    
    def _save_to_cache(self, endpoint: str, data: Dict[str, Any]):
        """Save response to cache."""
        if not self.use_cache or not self.cache_dir:
            return
            
        cache_path = self._get_cache_path(endpoint)
        if not cache_path:
            return
            
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.warning(f"Error saving to cache: {e}")
    
    def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a request to the API."""
        # Check cache first
        cached_data = self._get_from_cache(endpoint)
        if cached_data:
            self.logger.debug(f"Using cached data for: {endpoint}")
            return cached_data
        
        # Respect rate limiting
        self._respect_rate_limit()
        
        # Make the request
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            self.logger.debug(f"Making API request to: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache the response
            self._save_to_cache(endpoint, data)
            
            return data
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"API request failed: {e}")
            return None
    
    def get_card_by_name(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Get card information by exact name."""
        try:
            # Handle special characters
            encoded_name = quote(card_name.replace("'", "%27").replace('"', '%22'))
            endpoint = f"{self.CARD_INFO_ENDPOINT}?name={encoded_name}"
            
            data = self._make_request(endpoint)
            if data and "data" in data and len(data["data"]) > 0:
                return data["data"][0]
                
            return None
        except Exception as e:
            self.logger.warning(f"Error getting card by name: {e}")
            return None
    
    def search_cards(self, query: str) -> List[Dict[str, Any]]:
        """Search for cards using a partial name."""
        try:
            encoded_query = quote(query)
            endpoint = self.SEARCH_ENDPOINT.format(query=encoded_query)
            
            data = self._make_request(endpoint)
            if data and "data" in data:
                return data["data"]
                
            return []
        except Exception as e:
            self.logger.warning(f"Error searching cards: {e}")
            return []
    
    def get_all_cards(self) -> List[Dict[str, Any]]:
        """Get all cards in the database."""
        try:
            data = self._make_request(self.CARD_INFO_ENDPOINT)
            if data and "data" in data:
                return data["data"]
                
            return []
        except Exception as e:
            self.logger.warning(f"Error getting all cards: {e}")
            return []
    
    def clear_cache(self):
        """Clear the API cache."""
        if not self.cache_dir or not os.path.exists(self.cache_dir):
            return
            
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))
            self.logger.info("API cache cleared")
        except Exception as e:
            self.logger.warning(f"Error clearing cache: {e}")
