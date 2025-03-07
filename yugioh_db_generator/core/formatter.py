"""Formatters for Yu-Gi-Oh! card data in various output formats."""

import json
import csv
import io
import logging
import re
from typing import Dict, List, Any, Optional


class CardFormatter:
    """Formatter for Yu-Gi-Oh! card data."""
    
    def __init__(self, format_type: str = "markdown"):
        """Initialize the formatter.
        
        Args:
            format_type: Output format ('markdown', 'json', 'csv', or 'text')
        """
        self.logger = logging.getLogger(__name__)
        self.format_type = format_type.lower()
        
        # Mapping of format types to formatter methods
        self.formatters = {
            "markdown": self._format_markdown,
            "json": self._format_json,
            "csv": self._format_csv,
            "text": self._format_text
        }
        
        # Verify the format type is supported
        if self.format_type not in self.formatters:
            self.logger.warning(f"Unsupported format type: {format_type}. Defaulting to markdown.")
            self.format_type = "markdown"
    
    def format_card(self, card_data: Optional[Dict[str, Any]], original_name: str) -> Any:
        """Format a card according to the selected format type.
        
        Args:
            card_data: Card data to format (None if card not found)
            original_name: Original name of the card
            
        Returns:
            Formatted card data
        """
        formatter = self.formatters[self.format_type]
        
        if card_data:
            return formatter(card_data, original_name)
        else:
            return self._format_not_found(original_name)
    
    def format_database(self, cards: List[Any], title: str = "Yu-Gi-Oh! Card Database") -> str:
        """Format the complete database.
        
        Args:
            cards: List of formatted cards
            title: Title for the database
            
        Returns:
            Formatted database as a string
        """
        if self.format_type == "markdown":
            return f"# {title}\n\n" + "\n---\n\n".join(cards)
        
        elif self.format_type == "json":
            return json.dumps({"title": title, "cards": cards}, indent=2)
        
        elif self.format_type == "csv":
            # For CSV, we return the header plus all rows
            header = cards[0].keys() if cards and cards[0] else []
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=header)
            writer.writeheader()
            for card in cards:
                writer.writerow(card)
            return output.getvalue()
        
        elif self.format_type == "text":
            return f"{title}\n\n" + "\n\n".join(cards)
    
    def _format_markdown(self, card_data: Dict[str, Any], original_name: str) -> str:
        """Format a card in Markdown."""
        # Use the original name for consistency
        card_name = original_name
        
        # Determine card type
        full_type = card_data.get('type', '')
        if isinstance(full_type, list) and len(full_type) > 0:
            full_type = full_type[0]
            
        if "Monster" in full_type:
            card_type = "Monster"
        elif "Spell" in full_type:
            card_type = "Spell"
        elif "Trap" in full_type:
            card_type = "Trap"
        else:
            card_type = "Unknown"
        
        # Determine card property
        property_val = self._determine_property(card_data, full_type)
        
        # Get card specifics
        attribute = card_data.get('attribute', 'N/A') if "Monster" in full_type else "N/A"
        level_info = self._get_level_info(card_data, full_type)
        monster_type = self._get_monster_type(card_data, full_type)
        atk_def = f"{card_data.get('atk', '?')}/{card_data.get('def', '?')}" if "Monster" in full_type else "N/A"
        limitation = card_data.get('limitation', self._get_limitation(card_data))
        card_text = card_data.get('desc', 'No description available')
        
        # Generate rulings
        rulings = self._generate_rulings(card_name, card_text, property_val)
        
        # Build the formatted card section
        md = f"## {card_name}\n"
        md += "Basic Information\n"
        md += f"* **Card Type**: {card_type}\n"
        md += f"* **Property**: {property_val}\n"
        
        if "Monster" in full_type:
            md += f"* **Attribute**: {attribute}\n"
            md += f"* **Level/Rank/Link Rating**: {level_info}\n"
            md += f"* **Type**: {monster_type}\n"
            md += f"* **ATK/DEF**: {atk_def}\n"
        
        md += f"* **Limitation Status**: {limitation}\n\n"
        md += "Card Text\n"
        md += f"{card_text}\n\n"
        md += "Card Rulings & Interactions\n"
        
        for ruling in rulings:
            md += f"* {ruling}\n"
            
        return md
    
    def _format_json(self, card_data: Dict[str, Any], original_name: str) -> Dict[str, Any]:
        """Format a card as a JSON object."""
        # Determine card type and property
        full_type = card_data.get('type', '')
        if isinstance(full_type, list) and len(full_type) > 0:
            full_type = full_type[0]
            
        if "Monster" in full_type:
            card_type = "Monster"
        elif "Spell" in full_type:
            card_type = "Spell"
        elif "Trap" in full_type:
            card_type = "Trap"
        else:
            card_type = "Unknown"
            
        property_val = self._determine_property(card_data, full_type)
        
        # Build basic info
        result = {
            "name": original_name,
            "originalName": original_name,
            "matchedName": card_data.get('name', ''),
            "cardType": card_type,
            "property": property_val,
            "text": card_data.get('desc', ''),
            "limitation": card_data.get('limitation', self._get_limitation(card_data)),
            "rulings": self._generate_rulings(original_name, card_data.get('desc', ''), property_val)
        }
        
        # Add monster-specific fields
        if "Monster" in full_type:
            result.update({
                "attribute": card_data.get('attribute', 'N/A'),
                "level": self._get_level_info(card_data, full_type),
                "type": self._get_monster_type(card_data, full_type),
                "atk": card_data.get('atk', '?'),
                "def": card_data.get('def', '?')
            })
        
        return result
    
    def _format_csv(self, card_data: Dict[str, Any], original_name: str) -> Dict[str, str]:
        """Format a card as a CSV row."""
        # Determine card type and property
        full_type = card_data.get('type', '')
        if isinstance(full_type, list) and len(full_type) > 0:
            full_type = full_type[0]
            
        if "Monster" in full_type:
            card_type = "Monster"
        elif "Spell" in full_type:
            card_type = "Spell"
        elif "Trap" in full_type:
            card_type = "Trap"
        else:
            card_type = "Unknown"
            
        property_val = self._determine_property(card_data, full_type)
        
        # Build CSV row
        row = {
            "Name": original_name,
            "Type": card_type,
            "Property": property_val,
            "Description": card_data.get('desc', ''),
            "Limitation": card_data.get('limitation', self._get_limitation(card_data))
        }
        
        # Add monster-specific fields
        if "Monster" in full_type:
            row.update({
                "Attribute": card_data.get('attribute', 'N/A'),
                "Level/Rank/Link": self._get_level_info(card_data, full_type),
                "Monster Type": self._get_monster_type(card_data, full_type),
                "ATK": card_data.get('atk', '?'),
                "DEF": card_data.get('def', '?')
            })
        else:
            row.update({
                "Attribute": "N/A",
                "Level/Rank/Link": "N/A",
                "Monster Type": "N/A",
                "ATK": "N/A",
                "DEF": "N/A"
            })
        
        # Convert all values to strings for CSV
        return {k: str(v) for k, v in row.items()}
    
    def _format_text(self, card_data: Dict[str, Any], original_name: str) -> str:
        """Format a card as plain text."""
        # Use the original name for consistency
        card_name = original_name
        
        # Determine card type
        full_type = card_data.get('type', '')
        if isinstance(full_type, list) and len(full_type) > 0:
            full_type = full_type[0]
            
        if "Monster" in full_type:
            card_type = "Monster"
        elif "Spell" in full_type:
            card_type = "Spell"
        elif "Trap" in full_type:
            card_type = "Trap"
        else:
            card_type = "Unknown"
        
        property_val = self._determine_property(card_data, full_type)
        card_text = card_data.get('desc', 'No description available')
        
        text = f"{card_name}\n"
        text += f"Type: {card_type} | Property: {property_val}\n"
        
        if "Monster" in full_type:
            attribute = card_data.get('attribute', 'N/A')
            level_info = self._get_level_info(card_data, full_type)
            monster_type = self._get_monster_type(card_data, full_type)
            atk_def = f"{card_data.get('atk', '?')}/{card_data.get('def', '?')}"
            
            text += f"Attribute: {attribute} | {level_info} | Type: {monster_type} | ATK/DEF: {atk_def}\n"
        
        text += f"Limitation: {card_data.get('limitation', self._get_limitation(card_data))}\n\n"
        text += f"Text:\n{card_text}\n"
        
        return text
    
    def _format_not_found(self, card_name: str) -> Any:
        """Format a "card not found" entry."""
        if self.format_type == "markdown":
            md = f"## {card_name}\n"
            md += "Basic Information\n"
            md += "* **Card Type**: Unknown\n"
            md += "* **Property**: Unknown\n"
            md += "* **Limitation Status**: Unknown\n\n"
            md += "Card Text\n"
            md += "Card information not found in database. Please check the official Yu-Gi-Oh! database for accurate information.\n\n"
            md += "Card Rulings & Interactions\n"
            md += "* Card information not found. Please consult the official rulebook or a tournament judge for rulings.\n"
            return md
            
        elif self.format_type == "json":
            return {
                "name": card_name,
                "cardType": "Unknown",
                "property": "Unknown",
                "text": "Card information not found in database.",
                "limitation": "Unknown",
                "rulings": ["Card information not found. Please consult the official rulebook."]
            }
            
        elif self.format_type == "csv":
            return {
                "Name": card_name,
                "Type": "Unknown",
                "Property": "Unknown",
                "Description": "Card information not found in database.",
                "Limitation": "Unknown",
                "Attribute": "N/A",
                "Level/Rank/Link": "N/A",
                "Monster Type": "N/A",
                "ATK": "N/A",
                "DEF": "N/A"
            }
            
        elif self.format_type == "text":
            return f"{card_name}\nCard information not found in database."
    
    def _determine_property(self, card_data: Dict[str, Any], full_type: str) -> str:
        """Determine the card property based on its type."""
        property_val = "Normal"
        
        if "Monster" in full_type:
            for prop in ["Effect", "Ritual", "Fusion", "Synchro", "Xyz", "Pendulum", "Link"]:
                if prop in full_type:
                    property_val = prop
                    break
        elif "Spell" in full_type:
            spell_race = card_data.get('race', 'Normal')
            if isinstance(spell_race, list) and len(spell_race) > 0:
                spell_race = spell_race[0]
                
            property_map = {
                "Normal": "Normal",
                "Field": "Field",
                "Equip": "Equip",
                "Continuous": "Continuous",
                "Quick-Play": "Quick-Play",
                "Ritual": "Ritual"
            }
            property_val = property_map.get(spell_race, "Normal")
            
            # Check for specific spell types in the name
            if "Quick-Play" in full_type:
                property_val = "Quick-Play"
            
        elif "Trap" in full_type:
            trap_race = card_data.get('race', 'Normal')
            if isinstance(trap_race, list) and len(trap_race) > 0:
                trap_race = trap_race[0]
                
            property_map = {
                "Normal": "Normal",
                "Continuous": "Continuous", 
                "Counter": "Counter"
            }
            property_val = property_map.get(trap_race, "Normal")
            
        return property_val
    
    def _get_level_info(self, card_data: Dict[str, Any], full_type: str) -> str:
        """Get level/rank/link information for a monster card."""
        if "Monster" not in full_type:
            return "N/A"
            
        if "Link" in full_type and 'linkval' in card_data:
            return f"Link {card_data['linkval']}"
        elif "Xyz" in full_type and 'level' in card_data:
            return f"Rank {card_data['level']}"
        elif 'level' in card_data:
            return f"Level {card_data['level']}"
        else:
            return "N/A"
    
    def _get_monster_type(self, card_data: Dict[str, Any], full_type: str) -> str:
        """Get the monster type (race)."""
        if "Monster" not in full_type:
            return "N/A"
            
        monster_type = card_data.get('race', 'N/A')
        if isinstance(monster_type, list) and len(monster_type) > 0:
            monster_type = monster_type[0]
            
        return monster_type
    
    def _get_limitation(self, card_data: Dict[str, Any]) -> str:
        """Get the limitation status for a card."""
        # Check for banlist_info
        banlist_info = card_data.get('banlist_info', {})
        ban_tcg = banlist_info.get('ban_tcg', 'Unlimited')
        
        # Convert API return values to requested format
        status_map = {
            "Banned": "Forbidden",
            "Limited": "Limited",
            "Semi-Limited": "Semi-Limited",
            "Unlimited": "Unlimited"
        }
        
        return status_map.get(ban_tcg, "Unlimited")
    
    def _generate_rulings(self, card_name: str, card_text: str, property_val: str) -> List[str]:
        """Generate appropriate rulings based on card text analysis."""
        rulings = []
        
        # Skip for empty text
        if not card_text:
            return ["Always verify card rulings with the official rulebook or a tournament judge."]
        
        # Look for once per turn effects
        if "once per turn" in card_text.lower():
            rulings.append(f"The \"once per turn\" effect(s) of {card_name} reset if the card leaves the field and returns.")
        
        # Look for targeting effects
        if "target" in card_text.lower():
            rulings.append(f"Effects that prevent targeting will prevent {card_name} from selecting those cards as targets.")
        
        # Look for destruction effects
        if "destroy" in card_text.lower():
            rulings.append(f"Cards with destruction protection cannot be destroyed by {card_name}'s effect.")
        
        # Look for optional effects
        if any(x in card_text.lower() for x in ["you can", "you may"]):
            rulings.append(f"The effect of {card_name} that states \"you can\" is optional and can be activated at the player's discretion.")
        
        # Look for negation effects
        if "negate" in card_text.lower():
            rulings.append(f"When {card_name} negates an effect, it only negates the effect and not the activation, unless otherwise specified.")
            
        # Look for summoning conditions
        if "cannot be normal summoned/set" in card_text.lower():
            rulings.append(f"{card_name} must be Special Summoned by its own procedure and cannot be Special Summoned by other effects unless specified.")
            
        # Look for common archetypes in the text
        archetypes = ["Snake-eye", "Snake-Eyes", "Crystal Beast", "Fiendsmith", "Allure Queen", "World Legacy", "World Chalice"]
        for archetype in archetypes:
            if archetype.lower() in card_text.lower():
                rulings.append(f"This card specifically supports the \"{archetype}\" archetype and works well with other \"{archetype}\" cards.")
                break
        
        # Add property-specific rulings
        if property_val == "Quick-Play":
            rulings.append("This Quick-Play Spell can be activated from the hand during your opponent's turn if it was set on your field in a previous turn.")
        elif property_val == "Counter":
            rulings.append("This Counter Trap can be chained to the activation of other effects at Spell Speed 3.")
        elif property_val == "Link":
            rulings.append("The Link Arrows on this card determine which zones it points to for card effects that reference linked zones.")
        elif property_val == "Pendulum":
            rulings.append("When this card is destroyed while in a Monster Zone, you can place it in your Pendulum Zone instead of sending it to the GY.")
        
        # If we couldn't generate any specific rulings, add generic ones
        if not rulings:
            rulings.append(f"Always verify the timing and activation conditions of {card_name} with the current official rulebook.")
            rulings.append(f"For tournament play, consult with a judge for specific interactions involving {card_name}.")
        
        return rulings
