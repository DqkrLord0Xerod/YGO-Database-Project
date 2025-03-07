"""Advanced deck analysis module for Yu-Gi-Oh! deck lists."""

import logging
from typing import List, Dict, Any, Tuple, Set, Optional
from collections import Counter, defaultdict
import json
import os
import re


class DeckStrengthAnalyzer:
    """Analyzes a Yu-Gi-Oh! deck for strength, consistency, and balance.
    
    Features:
    - Archetype identification
    - Card synergy analysis
    - Consistency metrics
    - Card ratio recommendations
    - Meta comparison
    - Weaknesses identification
    - Suggested improvements
    """
    
    def __init__(self, meta_data_file: Optional[str] = None):
        """Initialize the deck analyzer.
        
        Args:
            meta_data_file: Path to JSON file with meta game data
        """
        self.logger = logging.getLogger(__name__)
        
        # Load meta data
        self.meta_data = self._load_meta_data(meta_data_file)
        
        # Card type categories
        self.card_categories = {
            "monsters": ["Normal Monster", "Effect Monster", "Ritual Monster", "Fusion Monster", 
                        "Synchro Monster", "Xyz Monster", "Pendulum Monster", "Link Monster"],
            "spells": ["Spell Card"],
            "traps": ["Trap Card"],
            "extra_deck": ["Fusion Monster", "Synchro Monster", "Xyz Monster", "Link Monster"]
        }
        
        # Card purpose categorization
        self.card_purposes = {
            "starters": [],  # Cards that initiate combos
            "extenders": [],  # Cards that extend combos
            "handtraps": ["Ash Blossom & Joyous Spring", "Effect Veiler", "Ghost Ogre & Snow Rabbit",
                         "Ghost Belle & Haunted Mansion", "D.D. Crow", "PSY-Framegear Gamma", 
                         "Nibiru, the Primal Being", "Infinite Impermanence"],
            "board_breakers": ["Raigeki", "Dark Hole", "Lightning Storm", "Evenly Matched", 
                              "Harpie's Feather Duster", "Twin Twisters", "Cosmic Cyclone", 
                              "Droll & Lock Bird", "Kaiju", "Lava Golem", "Ra - Sphere Mode"],
            "engines": {}  # Card engines and their components
        }
        
        # Common engines in the meta
        self.known_engines = {
            "adventurer": ["Water Enchantress of the Temple", "Rite of Aramesir", "Fateful Adventure", 
                          "Dracoback, the Rideable Dragon", "Illegal Knight"],
            "branded": ["Fallen of Albaz", "Branded Fusion", "Lubellion the Searing Dragon", 
                       "Albion the Branded Dragon", "Mirrorjade the Iceblade Dragon"],
            "dogmatika": ["Dogmatika Ecclesia, the Virtuous", "Nadir Servant", "Dogmatika Fleurdelis, the Knighted", 
                         "Dogmatika Maximus", "Titaniklad the Ash Dragon"],
            "dpe": ["Destiny HERO - Destroyer Phoenix Enforcer", "Fusion Destiny", 
                   "Destiny HERO - Celestial", "Destiny HERO - Dasher"],
            "tearlaments": ["Tearlaments Sulliek", "Tearlaments Scheiren", "Tearlaments Havnis", 
                          "Tearlaments Merrli", "Primeval Planet Perlereino"],
            "spright": ["Spright Blue", "Spright Jet", "Spright Starter", "Spright Elf", "Gigantic Spright"],
            "swordsoul": ["Swordsoul of Mo Ye", "Swordsoul Strategist Longyuan", "Swordsoul Emergence", 
                         "Incredible Ecclesia, the Virtuous"],
            "tenyi": ["Monk of the Tenyi", "Tenyi Spirit - Ashuna", "Tenyi Spirit - Vishuda", 
                     "Tenyi Spirit - Adhara", "Dragon Circle of the Tenyi"]
        }
        
    def _load_meta_data(self, meta_file: Optional[str]) -> Dict[str, Any]:
        """Load meta game data from a JSON file."""
        # Default meta data
        data = {
            "top_decks": {},
            "tier_list": {},
            "staple_cards": [],
            "card_popularity": {},
            "archetype_synergies": {}
        }
        
        # Try to load custom data if provided
        if meta_file and os.path.exists(meta_file):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    # Merge custom data with defaults
                    for key, value in custom_data.items():
                        if key in data:
                            if isinstance(value, dict):
                                data[key].update(value)
                            elif isinstance(value, list):
                                data[key].extend(value)
                            else:
                                data[key] = value
                                
                self.logger.info(f"Loaded meta game data from {meta_file}")
            except Exception as e:
                self.logger.warning(f"Error loading meta data: {e}")
                
        return data
    
    def analyze_deck(self, deck_list: List[str], card_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a Yu-Gi-Oh! deck for strength and consistency.
        
        Args:
            deck_list: List of card names in the deck
            card_data: Dictionary mapping card names to their data
            
        Returns:
            Analysis results
        """
        # Initialize analysis results
        analysis = {
            "deck_size": len(deck_list),
            "card_types": {},
            "archetypes": {},
            "main_archetype": None,
            "card_purposes": {},
            "engines": {},
            "consistency_score": 0,
            "power_score": 0,
            "resilience_score": 0,
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "meta_comparison": {}
        }
        
        # Count card types
        analysis["card_types"] = self._analyze_card_types(deck_list, card_data)
        
        # Identify archetypes
        archetypes = self._identify_archetypes(deck_list, card_data)
        analysis["archetypes"] = archetypes
        if archetypes:
            # Main archetype is the one with the most cards
            analysis["main_archetype"] = max(archetypes.items(), key=lambda x: x[1])[0]
        
        # Categorize cards by purpose
        analysis["card_purposes"] = self._categorize_by_purpose(deck_list, card_data)
        
        # Identify engines
        analysis["engines"] = self._identify_engines(deck_list)
        
        # Calculate scores
        scores = self._calculate_scores(deck_list, card_data, analysis)
        analysis.update(scores)
        
        # Identify strengths and weaknesses
        analysis["strengths"] = self._identify_strengths(analysis)
        analysis["weaknesses"] = self._identify_weaknesses(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis, deck_list, card_data)
        
        # Compare with meta
        analysis["meta_comparison"] = self._compare_with_meta(analysis)
        
        return analysis
    
    # Add this method to the DeckStrengthAnalyzer class in deck_analyzer.py

def _identify_archetypes(self, deck_list):
    """Identify archetypes in the deck."""
    archetypes = {
        "Snake-eye": 0,
        "Crystal Beast": 0,
        "Fiendsmith": 0,
        "World Legacy": 0,
        "Allure Queen": 0,
        "Vaylantz": 0
    }
    
    # Count archetype occurrences
    for card_name in deck_list:
        for archetype in archetypes:
            if archetype in card_name:
                archetypes[archetype] += 1
    
    # Filter out archetypes with 0 counts
    return {k: v for k, v in archetypes.items() if v > 0}


def _analyze_card_types(self, deck_list: List[str], card_data: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Analyze the distribution of card types in the deck."""
        counts = {
            "monsters": 0,
            "spells": 0,
            "traps": 0,
            "extra_deck": 0,
            "normal_monsters": 0,
            "effect_monsters": 0,
            "ritual_monsters": 0,
            "fusion_monsters": 0,
            "synchro_monsters": 0,
            "xyz_monsters": 0,
            "pendulum_monsters": 0,
            "link_monsters": 0,
            "normal_spells": 0,
            "continuous_spells": 0,
            "quick_play_spells": 0,
            "ritual_spells": 0,
            "field_spells": 0,
            "equip_spells": 0,
            "normal_traps": 0,
            "continuous_traps": 0,
            "counter_traps": 0
        }
        
        for card_name in deck_list:
            card = card_data.get(card_name, {})
            card_type = card.get("type", "").lower()
            
            # Skip if card data not found
            if not card_type:
                continue
                
            # Count by main type
            if "monster" in card_type:
                counts["monsters"] += 1
                
                # Count by monster type
                if "normal" in card_type and "monster" in card_type and "effect" not in card_type:
                    counts["normal_monsters"] += 1
                if "effect" in card_type:
                    counts["effect_monsters"] += 1
                if "ritual" in card_type:
                    counts["ritual_monsters"] += 1
                if "fusion" in card_type:
                    counts["fusion_monsters"] += 1
                    counts["extra_deck"] += 1
                if "synchro" in card_type:
                    counts["synchro_monsters"] += 1
                    counts["extra_deck"] += 1
                if "xyz" in card_type:
                    counts["xyz_monsters"] += 1
                    counts["extra_deck"] += 1
                if "pendulum" in card_type:
                    counts["pendulum_monsters"] += 1
                if "link" in card_type:
                    counts["link_monsters"] += 1
                    counts["extra_deck"] += 1
                    
            elif "spell" in card_type:
                counts["spells"] += 1
                
                # Count by spell type
                race = card.get("race", "").lower()
                if race == "normal" or (race == "" and "normal" not in card_type):
                    counts["normal_spells"] += 1
                if "continuous" in card_type or race == "continuous":
                    counts["continuous_spells"] += 1
                if "quick-play" in card_type or race == "quick-play":
                    counts["quick_play_spells"] += 1
                if "ritual" in card_type or race == "ritual":
                    counts["ritual_spells"] += 1
                if "field" in card_type or race == "field":
                    counts["field_spells"] += 1
                if "equip" in card_type or race == "equip":
                    counts["equip_spells"] += 1
                    
            elif "trap" in card_type:
                counts["traps"] += 1
                
                # Count by trap type
                race = card.get("race", "").lower()
                if race == "normal" or (race == "" and "normal" not in card_type):
                    counts["normal_traps"] += 1
                if "continuous" in card_type or race == "continuous":
                    counts["continuous_traps"] += 1
                if "counter" in card_type or race == "counter":
                    counts["counter_traps"] += 1
                    
        return counts