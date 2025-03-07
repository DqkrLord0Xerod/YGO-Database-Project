"""Advanced AI-based rule generation for Yu-Gi-Oh! cards."""

import re
import logging
from typing import List, Dict, Any, Set, Optional
import json
import os


class AIRuleGenerator:
    """Generate card rulings and interactions using AI techniques.
    
    This module analyzes card text to generate contextually accurate
    rulings and interactions, including:
    
    1. Pattern-based rule generation using card text analysis
    2. Contextual rule generation based on card properties
    3. Archetype-specific interaction rules
    4. Card-specific edge cases and common misplays
    """
    
    def __init__(self, rules_data_file: Optional[str] = None):
        """Initialize the rule generator.
        
        Args:
            rules_data_file: Path to JSON file with custom rules data
        """
        self.logger = logging.getLogger(__name__)
        
        # Load rules data
        self.rules_data = self._load_rules_data(rules_data_file)
        
        # Initialize pattern recognition system
        self._init_patterns()
    
    def _load_rules_data(self, rules_file: Optional[str]) -> Dict[str, Any]:
        """Load custom rules data from a JSON file."""
        # Default data
        data = {
            "archetypes": {},
            "card_specific_rules": {},
            "interaction_templates": [],
            "timing_rules": {},
            "common_misplays": []
        }
        
        # Try to load custom data if provided
        if rules_file and os.path.exists(rules_file):
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
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
                                
                self.logger.info(f"Loaded custom rules data from {rules_file}")
            except Exception as e:
                self.logger.warning(f"Error loading rules data: {e}")
                
        return data
    
    def _init_patterns(self):
        """Initialize pattern recognition for card effects."""
        # Card effect patterns for analysis
        self.effect_patterns = {
            "once_per_turn": re.compile(r"(?i)once per turn"),
            "hard_once_per_turn": re.compile(r"(?i)you can only (use|activate) this effect of .+ once per turn"),
            "targeting": re.compile(r"(?i)target"),
            "destruction": re.compile(r"(?i)destroy"),
            "negation": re.compile(r"(?i)negate"),
            "removal": re.compile(r"(?i)(banish|remove from play|return to (hand|deck))"),
            "special_summon": re.compile(r"(?i)special summon"),
            "search": re.compile(r"(?i)(add|search).+from your deck"),
            "cost": re.compile(r"(?i)(discard|pay|send to the GY).+;"),
            "trigger": re.compile(r"(?i)(when|if) (this card|a card|a monster)"),
            "continuous": re.compile(r"(?i)(while|as long as)"),
            "activation_requirement": re.compile(r"(?i)you can only activate this.+if"),
            "summoning_condition": re.compile(r"(?i)cannot be normal summoned/set"),
            "quick_effect": re.compile(r"(?i)(quick effect|during (your opponent's|either player's) (turn|main phase|battle phase))"),
            "counter": re.compile(r"(?i)when.+(is activated|activates|would be)"),
            "ignition": re.compile(r"(?i)(during your main phase|:) you can"),
            "chain": re.compile(r"(?i)(chain|in response|after this effect resolves)")
        }
        
        # Card property recognition
        self.property_recognizers = {
            "is_monster": lambda card: card.get("type", "").lower().find("monster") >= 0,
            "is_spell": lambda card: card.get("type", "").lower().find("spell") >= 0,
            "is_trap": lambda card: card.get("type", "").lower().find("trap") >= 0,
            "is_extra_deck": lambda card: any(t in card.get("type", "").lower() for t in ["fusion", "synchro", "xyz", "link"]),
            "is_effect_monster": lambda card: "effect" in card.get("type", "").lower(),
            "is_normal_monster": lambda card: "normal monster" in card.get("type", "").lower(),
            "is_quick_play": lambda card: "quick-play" in card.get("type", "").lower() or card.get("race", "").lower() == "quick-play",
            "is_continuous": lambda card: "continuous" in card.get("type", "").lower() or card.get("race", "").lower() == "continuous",
            "is_ritual": lambda card: "ritual" in card.get("type", "").lower(),
            "is_pendulum": lambda card: "pendulum" in card.get("type", "").lower(),
            "is_token": lambda card: "token" in card.get("type", "").lower(),
            "is_counter_trap": lambda card: card.get("type", "").lower() == "trap card" and card.get("race", "").lower() == "counter"
        }
    
    def analyze_card_text(self, card_text: str) -> Dict[str, bool]:
        """Analyze card text to identify effect patterns."""
        effects = {}
        for effect_name, pattern in self.effect_patterns.items():
            effects[effect_name] = bool(pattern.search(card_text))
        return effects
    
    def identify_card_properties(self, card_data: Dict[str, Any]) -> Dict[str, bool]:
        """Identify card properties based on its data."""
        properties = {}
        for prop_name, recognizer in self.property_recognizers.items():
            properties[prop_name] = recognizer(card_data)
        return properties
    
    def generate_rulings(self, card_name: str, card_data: Dict[str, Any]) -> List[str]:
        """Generate comprehensive rulings for a card.
        
        Args:
            card_name: The name of the card
            card_data: Card data from the API
            
        Returns:
            List of ruling strings
        """
        rulings = []
        card_text = card_data.get('desc', '')
        
        # Skip for empty text
        if not card_text:
            return ["Always verify card rulings with the official rulebook or a tournament judge."]
        
        # Extract card properties and effects
        properties = self.identify_card_properties(card_data)
        effects = self.analyze_card_text(card_text)
        archetype = self.extract_archetype(card_name, card_text)
        
        # Add basic pattern-based rulings
        rulings.extend(self._generate_pattern_based_rulings(card_name, card_text, effects))
        
        # Add property-based rulings
        rulings.extend(self._generate_property_based_rulings(card_name, properties))
        
        # Add archetype-specific rulings
        if archetype:
            rulings.extend(self._generate_archetype_rulings(card_name, archetype))
        
        # Add timing and activation rules
        rulings.extend(self._generate_timing_rules(card_name, card_text, effects, properties))
        
        # Add card-specific rules if available
        specific_rules = self._get_card_specific_rules(card_name)
        if specific_rules:
            rulings.extend(specific_rules)
        
        # Add common misplays if relevant
        misplays = self._generate_common_misplays(card_name, effects, properties)
        if misplays:
            rulings.extend(misplays)
        
        # If we couldn't generate many specific rulings, add generic ones
        if len(rulings) < 3:
            rulings.append(f"Always verify the timing and activation conditions of {card_name} with the current official rulebook.")
            rulings.append(f"For tournament play, consult with a judge for specific interactions involving {card_name}.")
        
        return rulings
    
    def extract_archetype(self, card_name: str, card_text: str) -> Optional[str]:
        """Extract the archetype from card name or text."""
        # Check common archetypes
        common_archetypes = [
            "Blue-Eyes", "Dark Magician", "Red-Eyes", "Elemental HERO", 
            "Odd-Eyes", "Pendulum Dragon", "Stardust", "Synchron", 
            "Cyber Dragon", "Utopia", "Galaxy-Eyes", "Rokket", "Dragonmaid",
            "Sky Striker", "Altergeist", "Salamangreat", "Thunder Dragon",
            "Madolche", "Shaddoll", "Lightsworn", "Burning Abyss", "Invoked",
            "Skystriker", "Danger!", "True Draco", "Crystron", "Orcust",
            "Kaiju", "Trickstar", "Gouki", "Mekk-Knight", "Crusadia",
            "Phantom Knight", "Predaplant", "Subterror", "Witchcrafter",
            "World Legacy", "Virtual World", "Dogmatika", "Tri-Brigade",
            "Drytron", "Cyberse", "Dracoslayer", "Dino", "Ghostrick",
            "Infernoid", "Marincess", "Megalith", "Myutant", "Plunder Patroll",
            "Prank-Kids", "Qli", "Time Thief", "Spellbook", "Speedroid", 
            "Windwitch", "Zoodiac", "Ancient Gear", "Abyss Actor",
            "Adamancipator", "Aroma", "Buster Blader", "Chaos", "Cubic",
            "Darklord", "Endymion", "Fabled", "Fluffal", "Fur Hire",
            "Gaia The Fierce Knight", "Gishki", "Gladiator Beast", "Gusto",
            "Ice Barrier", "Infernoble Knight", "Infernity", "Krawler",
            "Laval", "Lunalight", "Lyrilusc", "Magical Musket", "Meklord",
            "Metaphys", "Nekroz", "Nemeses", "Noble Knight", "Nordic",
            "Number", "Performapal", "Phantasm", "Photon", "Ritual Beast",
            "Raidraptor", "Shiranui", "Six Samurai", "Superheavy Samurai",
            "Swordsoul", "Tenyi", "Traptrix", "U.A.", "Vendread", "Watt",
            "Weather Painter", "X-Saber", "Yang Zing", "Yosenju", "Zefra",
            "Snake-eye", "Snake-Eyes", "Fiendsmith", "Crystal Beast", "Allure Queen",
            "Vaylantz"
        ]
        
        # Custom archetypes from rules data
        custom_archetypes = list(self.rules_data.get("archetypes", {}).keys())
        all_archetypes = common_archetypes + custom_archetypes
        
        # Check card name for archetype
        for archetype in all_archetypes:
            if archetype.lower() in card_name.lower():
                return archetype
        
        # Check card text for archetype references (more complex)
        archetype_mentions = []
        for archetype in all_archetypes:
            # Look for "X card", "X monster", "X spell/trap", or just "X" in quotes
            patterns = [
                f"{archetype} card",
                f"{archetype} monster",
                f"{archetype} spell",
                f"{archetype} trap",
                f'"{archetype}"'
            ]
            for pattern in patterns:
                if pattern.lower() in card_text.lower():
                    archetype_mentions.append(archetype)
                    break
        
        # Return the most mentioned archetype, if any
        if archetype_mentions:
            # Count occurrences and return the most frequent
            from collections import Counter
            return Counter(archetype_mentions).most_common(1)[0][0]
            
        return None
    
    def _generate_pattern_based_rulings(self, card_name: str, card_text: str, effects: Dict[str, bool]) -> List[str]:
        """Generate rulings based on card text patterns."""
        rulings = []
        
        # Once per turn effects
        if effects.get("once_per_turn", False):
            if effects.get("hard_once_per_turn", False):
                rulings.append(f"The \"you can only use this effect of {card_name} once per turn\" restriction is a limitation that applies even if this card leaves the field and returns, or if you control multiple copies of {card_name}.")
            else:
                rulings.append(f"The \"once per turn\" effect(s) of {card_name} reset if the card leaves the field and returns, or if you use the effect of a different copy of the card.")
        
        # Targeting effects
        if effects.get("targeting", False):
            rulings.append(f"Effects that prevent targeting (e.g., \"cannot be targeted by card effects\") will prevent {card_name} from selecting those cards as targets.")
            if "spell" in card_text.lower() or "trap" in card_text.lower():
                rulings.append(f"If a targeted card is no longer in the specified location when {card_name}'s effect resolves, that part of the effect that would affect that target does not resolve.")
        
        # Destruction effects
        if effects.get("destruction", False):
            rulings.append(f"Cards with destruction protection (e.g., \"cannot be destroyed by card effects\") cannot be destroyed by {card_name}'s effect.")
            
        # Negation effects
        if effects.get("negation", False):
            rulings.append(f"When {card_name} negates an effect, it only negates the effect and not the activation, unless otherwise specified. Cards or effects negated by {card_name} are still considered to have been activated or summoned.")
            
        # Quick effects
        if effects.get("quick_effect", False):
            rulings.append(f"{card_name} can be activated during either player's turn at Spell Speed 2, which means it can be chained to other effects except Counter Trap Cards (Spell Speed 3).")
        
        # Summoning condition
        if effects.get("summoning_condition", False):
            rulings.append(f"{card_name} must be Special Summoned by its own procedure and cannot be Special Summoned by other effects unless it was properly Special Summoned first.")
            
        # Cost vs. effect
        if effects.get("cost", False):
            rulings.append(f"Everything before the semicolon (;) in {card_name}'s text is a cost that must be paid at activation and is not part of the effect. This cost is paid even if the effect is negated.")
            
        # Trigger effects
        if effects.get("trigger", False) and not effects.get("quick_effect", False):
            rulings.append(f"The trigger effect of {card_name} must be activated at the first opportunity in a new Chain after its trigger condition is met.")
            
        # Continuous effects
        if effects.get("continuous", False):
            rulings.append(f"The continuous effect of {card_name} applies as long as the card remains face-up on the field, unless otherwise specified.")
            
        # Ignition effects
        if effects.get("ignition", False):
            rulings.append(f"The ignition effect of {card_name} can only be activated during your Main Phase when the Chain is empty, unless otherwise specified.")
            
        # Search effects
        if effects.get("search", False):
            rulings.append(f"When you add a card from your Deck to your hand with {card_name}, you must show that card to your opponent to verify it meets the required conditions.")
            
        # Special Summon
        if effects.get("special_summon", False):
            rulings.append(f"Monsters Special Summoned by {card_name}'s effect are considered properly summoned and can be later revived from the GY if they're sent there.")
            
        return rulings
        
    def _generate_property_based_rulings(self, card_name: str, properties: Dict[str, bool]) -> List[str]:
        """Generate rulings based on card properties."""
        rulings = []
        
        # Monster card rulings
        if properties.get("is_monster", False):
            if properties.get("is_effect_monster", False):
                rulings.append(f"As an Effect Monster, {card_name}'s effects can be negated by cards like \"Effect Veiler\" or \"Infinite Impermanence\".")
                
            if properties.get("is_extra_deck", False):
                if "is_fusion" in properties and properties["is_fusion"]:
                    rulings.append(f"{card_name} must first be Fusion Summoned with the appropriate Fusion materials or by other card effects that specifically allow its Special Summon.")
                elif "is_synchro" in properties and properties["is_synchro"]:
                    rulings.append(f"{card_name} must first be Synchro Summoned with the appropriate Tuner and non-Tuner monsters whose Levels equal exactly {card_data.get('level', '?')}.")
                elif "is_xyz" in properties and properties["is_xyz"]:
                    rulings.append(f"Xyz Materials attached to {card_name} are not treated as being on the field. When {card_name} leaves the field, its materials are sent to the GY.")
                elif "is_link" in properties and properties["is_link"]:
                    rulings.append(f"The Link Arrows on {card_name} determine which zones it points to for card effects that reference linked zones.")
            
            if properties.get("is_pendulum", False):
                rulings.append(f"When {card_name} is destroyed while in a Monster Zone, you can place it face-up in your Pendulum Zone instead of sending it to the GY.")
                
        # Spell card rulings
        elif properties.get("is_spell", False):
            if properties.get("is_quick_play", False):
                rulings.append(f"This Quick-Play Spell can be activated from your hand during your Main Phase, or can be activated from the field during either player's turn if it was Set on your field in a previous turn.")
            elif properties.get("is_continuous", False):
                rulings.append(f"This Continuous Spell remains on the field after activation. If this card is destroyed or removed from the field, any continuous effects it applies are no longer applied.")
            elif properties.get("is_ritual", False):
                rulings.append(f"This Ritual Spell is used to Ritual Summon a Ritual Monster. The total Levels of the monsters Tributed must equal or exceed the Level of the Ritual Monster being Summoned.")
                
        # Trap card rulings
        elif properties.get("is_trap", False):
            rulings.append(f"This Trap Card must be Set on the field for 1 turn before it can be activated.")
            
            if properties.get("is_counter_trap", False):
                rulings.append(f"This Counter Trap is Spell Speed 3 and can be chained to any Spell Speed 1 or 2 effect, including other Trap Cards or Quick-Play Spells. Only another Counter Trap can be chained to this card.")
            elif properties.get("is_continuous", False):
                rulings.append(f"This Continuous Trap remains on the field after activation. If this card is destroyed or removed from the field, any continuous effects it applies are no longer applied.")
                
        return rulings
        
    def _generate_archetype_rulings(self, card_name: str, archetype: str) -> List[str]:
        """Generate archetype-specific rulings."""
        rulings = []
        
        # Check if we have specific archetype rules in our data
        archetype_rules = self.rules_data.get("archetypes", {}).get(archetype, {})
        if archetype_rules:
            for rule in archetype_rules.get("general_rules", []):
                rulings.append(rule.replace("{card_name}", card_name))
                
            # Only add a few archetype rules to avoid overwhelming the user
            if len(rulings) < 2 and archetype_rules.get("interaction_rules", []):
                rulings.append(archetype_rules["interaction_rules"][0].replace("{card_name}", card_name))
        else:
            # Generic archetype ruling
            rulings.append(f"This card specifically supports the \"{archetype}\" archetype and works well with other \"{archetype}\" cards.")
            
        return rulings
        
    def _generate_timing_rules(self, card_name: str, card_text: str, effects: Dict[str, bool], properties: Dict[str, bool]) -> List[str]:
        """Generate timing and activation rules."""
        rulings = []
        
        # Check for activation triggers in the card text
        has_activation_timing = False
        activation_triggers = [
            "when", "if", "during", "at the", "after", "while",
            "end phase", "start phase", "main phase", "battle phase",
            "standby phase", "end step", "damage step"
        ]
        
        for trigger in activation_triggers:
            if trigger in card_text.lower():
                has_activation_timing = True
                break
                
        if has_activation_timing:
            # Check for common timing patterns
            if "when" in card_text.lower() and "you can" in card_text.lower():
                rulings.append(f"The \"When... you can\" effect of {card_name} is an optional trigger effect with a specific timing. It must be activated in the first Chain Link after the condition is met, or you will miss the timing.")
                
            if "during the damage step" in card_text.lower():
                rulings.append(f"{card_name} can be activated during the Damage Step, which is unusual as most cards cannot be activated during this step.")
                
            if "during either player's" in card_text.lower():
                rulings.append(f"{card_name} can be activated during either player's turn, making it versatile for both offense and defense.")
        
        # Add property-based timing rules
        if properties.get("is_counter_trap", False):
            rulings.append(f"As a Counter Trap, {card_name} can only be responded to by other Counter Traps due to its Spell Speed 3.")
            
        return rulings
        
    def _get_card_specific_rules(self, card_name: str) -> List[str]:
        """Get card-specific rules from the rules data."""
        specific_rules = self.rules_data.get("card_specific_rules", {}).get(card_name, [])
        return specific_rules
        
    def _generate_common_misplays(self, card_name: str, effects: Dict[str, bool], properties: Dict[str, bool]) -> List[str]:
        """Generate warnings about common misplays."""
        misplays = []
        
        # Check for common misplay patterns
        common_misplays = self.rules_data.get("common_misplays", [])
        for misplay in common_misplays:
            condition = misplay.get("condition", {})
            
            # Check if the conditions match this card
            matches = True
            for effect_name, required in condition.get("effects", {}).items():
                if effects.get(effect_name, False) != required:
                    matches = False
                    break
                    
            for prop_name, required in condition.get("properties", {}).items():
                if properties.get(prop_name, False) != required:
                    matches = False
                    break
                    
            # If all conditions match, add the misplay warning
            if matches and "text" in misplay:
                misplays.append(misplay["text"].replace("{card_name}", card_name))
                
        return misplays