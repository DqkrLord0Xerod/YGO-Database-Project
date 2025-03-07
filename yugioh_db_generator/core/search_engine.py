"""Advanced search engine for finding Yu-Gi-Oh! cards with fuzzy matching."""

import re
import difflib
import logging
from typing import Dict, List, Any, Optional, Tuple
import Levenshtein


class CardSearchEngine:
    """Advanced search engine for Yu-Gi-Oh! cards."""
    
    def __init__(self, api_client, similarity_threshold: float = 0.7):
        """Initialize the search engine.
        
        Args:
            api_client: API client for fetching card data
            similarity_threshold: Minimum similarity score (0-1) for fuzzy matches
        """
        self.logger = logging.getLogger(__name__)
        self.api_client = api_client
        self.similarity_threshold = similarity_threshold
        self.card_cache = {}
        self.correction_map = {}  # Maps original names to corrected ones
        
        # Initialize the local card database
        self._load_card_database()
    
    def _load_card_database(self):
        """Load the full card database for local searching."""
        self.all_cards = self.api_client.get_all_cards()
        self.all_card_names = [card['name'] for card in self.all_cards] if self.all_cards else []
        self.logger.info(f"Loaded {len(self.all_cards)} cards into search engine")
    
    def get_name_corrections(self) -> Dict[str, str]:
        """Get the mapping of original card names to corrected ones."""
        return self.correction_map
    
    def search(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Search for a card using multiple methods.
        
        Args:
            card_name: The name of the card to search for
            
        Returns:
            Card data if found, None otherwise
        """
        # Check the cache first
        if card_name in self.card_cache:
            return self.card_cache[card_name]
        
        # Try exact match
        card_data = self._exact_match(card_name)
        if card_data:
            self.card_cache[card_name] = card_data
            return card_data
        
        # Try fuzzy API search
        card_data = self._fuzzy_api_search(card_name)
        if card_data:
            self.card_cache[card_name] = card_data
            self._record_correction(card_name, card_data['name'])
            return card_data
        
        # Try local fuzzy match
        card_data = self._local_fuzzy_search(card_name)
        if card_data:
            self.card_cache[card_name] = card_data
            self._record_correction(card_name, card_data['name'])
            return card_data
        
        # Try token-based search
        card_data = self._token_search(card_name)
        if card_data:
            self.card_cache[card_name] = card_data
            self._record_correction(card_name, card_data['name'])
            return card_data
        
        # No matches found
        self.logger.warning(f"No card found for: {card_name}")
        return None
    
    def _record_correction(self, original: str, corrected: str):
        """Record a name correction for reporting."""
        if original != corrected:
            self.correction_map[original] = corrected
            self.logger.info(f"Corrected: '{original}' -> '{corrected}'")
    
    def _exact_match(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Try to find an exact match for a card name."""
        try:
            card_data = self.api_client.get_card_by_name(card_name)
            if card_data:
                self.logger.info(f"Found exact match for: {card_name}")
                return card_data
        except Exception as e:
            self.logger.warning(f"Error in exact match: {e}")
        
        return None
    
    def _fuzzy_api_search(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Search for a card using the API's partial search functionality."""
        try:
            # Generate multiple search queries
            search_queries = self._generate_search_queries(card_name)
            
            best_match = None
            best_similarity = 0
            
            for query in search_queries:
                results = self.api_client.search_cards(query)
                
                for card in results:
                    # Calculate similarity using Levenshtein distance
                    similarity = self._calculate_similarity(card_name, card['name'])
                    
                    if similarity > best_similarity and similarity >= self.similarity_threshold:
                        best_similarity = similarity
                        best_match = card
            
            if best_match:
                self.logger.info(
                    f"Fuzzy API match for '{card_name}': '{best_match['name']}' "
                    f"(similarity: {best_similarity:.2f})"
                )
                return best_match
                
        except Exception as e:
            self.logger.warning(f"Error in fuzzy API search: {e}")
        
        return None
    
    def _generate_search_queries(self, card_name: str) -> List[str]:
        """Generate various search queries based on the card name."""
        queries = []
        
        # Strategy 1: First few characters
        prefix_length = min(5, len(card_name) // 2) if len(card_name) > 5 else 3
        queries.append(card_name[:prefix_length])
        
        # Strategy 2: First word
        if " " in card_name:
            queries.append(card_name.split(" ")[0])
        
        # Strategy 3: Most distinctive word
        words = re.findall(r'\b\w+\b', card_name)
        if words:
            # Sort by length (longer words are often more distinctive)
            distinctive_words = sorted(words, key=len, reverse=True)
            if distinctive_words and distinctive_words[0] not in queries:
                queries.append(distinctive_words[0])
        
        # Strategy 4: Handle apostrophes
        if "'" in card_name:
            queries.append(card_name.split("'")[0])
        
        # Strategy 5: Common prefixes
        common_prefixes = [
            "Snake-eye", "Snake-Eye", "Fiendsmith", "Crystal Beast", 
            "World Legacy", "Allure Queen"
        ]
        
        for prefix in common_prefixes:
            if card_name.startswith(prefix):
                queries.append(prefix)
                break
        
        return list(set(queries))  # Remove duplicates
    
    def _local_fuzzy_search(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Try to find a match using local fuzzy string matching."""
        if not self.all_card_names:
            return None
            
        # Generate alternative spellings
        alternatives = self._generate_alternative_spellings(card_name)
        
        for alt in alternatives:
            # Use difflib's get_close_matches for fuzzy matching
            matches = difflib.get_close_matches(
                alt, self.all_card_names, n=1, cutoff=self.similarity_threshold
            )
            
            if matches:
                best_match = matches[0]
                # Calculate similarity for reporting
                similarity = self._calculate_similarity(card_name, best_match)
                self.logger.info(
                    f"Local fuzzy match for '{card_name}': '{best_match}' "
                    f"(similarity: {similarity:.2f}, using: '{alt}')"
                )
                
                # Find the corresponding card data
                for card in self.all_cards:
                    if card['name'] == best_match:
                        return card
        
        return None
    
    def _generate_alternative_spellings(self, card_name: str) -> List[str]:
        """Generate alternative spellings for the card name."""
        alternatives = [
            card_name,  # Original name
            card_name.replace("-", " "),  # Replace hyphens with spaces
            card_name.replace("'s", ""),  # Remove possessive
            card_name.replace("'", ""),   # Remove apostrophes
        ]
        
        # Add specific alternative spellings for known variations
        name_variants = [
            ("Snake-eye", "Snake-Eyes"),
            ("Harpies'", "Harpie's"),
            ("Magicians'", "Magician's"),
            ("Magisitus", "Magistus"),
            ("Fiendsmith", "Fiendsmith's"),
            ("Rciela Sinister Soul", "Rciela, Sinister Soul")
        ]
        
        for search, replace in name_variants:
            if search in card_name:
                alternatives.append(card_name.replace(search, replace))
        
        return alternatives
    
    def _token_search(self, card_name: str) -> Optional[Dict[str, Any]]:
        """Search by breaking the card name into tokens."""
        tokens = re.findall(r'\b\w+\b', card_name)
        if len(tokens) < 2 or not self.all_cards:
            return None
            
        # Score each card based on token matches and semantic similarity
        candidates = []
        
        for card in self.all_cards:
            card_name_lower = card['name'].lower()
            # Tokenize card name
            card_tokens = set(re.findall(r'\b\w+\b', card_name_lower))
            
            # Count matching tokens
            matching_tokens = 0
            for token in tokens:
                if token.lower() in card_tokens:
                    # Give higher weight to longer tokens
                    matching_tokens += len(token)
            
            # Calculate overall similarity
            similarity = self._calculate_similarity(card_name.lower(), card_name_lower)
            
            # Combined score: token matches + similarity
            if matching_tokens > 0 or similarity > self.similarity_threshold / 2:
                score = matching_tokens + (similarity * 10)
                candidates.append((score, similarity, card))
        
        # Sort by score (highest first)
        candidates.sort(reverse=True)
        
        # Return best candidate if good enough
        if candidates and candidates[0][1] >= self.similarity_threshold / 1.5:  # Lower threshold for token search
            best_card = candidates[0][2]
            self.logger.info(
                f"Token search match for '{card_name}': '{best_card['name']}' "
                f"(similarity: {candidates[0][1]:.2f})"
            )
            return best_card
            
        return None
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate the similarity between two strings.
        
        Uses a combination of ratio and token_sort_ratio for more accurate matching.
        """
        # Normalize strings for comparison
        s1 = str1.lower()
        s2 = str2.lower()
        
        # Calculate standard similarity ratio
        standard_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
        
        # Calculate Levenshtein distance-based ratio
        lev_ratio = 1 - (Levenshtein.distance(s1, s2) / max(len(s1), len(s2), 1))
        
        # Calculate token sort ratio (order-independent)
        s1_tokens = sorted(s1.split())
        s2_tokens = sorted(s2.split())
        token_ratio = difflib.SequenceMatcher(None, ' '.join(s1_tokens), ' '.join(s2_tokens)).ratio()
        
        # Return weighted average of the ratios
        return (standard_ratio * 0.4) + (lev_ratio * 0.3) + (token_ratio * 0.3)
