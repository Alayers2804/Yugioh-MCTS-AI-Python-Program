import pandas as pd
import numpy as np

effect_points_mapping = {
    'destroy': 10,
    'banish': 10,
    'draw': 20,
    'summon': 20,
    'discard': -10,
    'gain': 20,
    'lose': -10,
    'from your deck': 20,
    'inflict': 20
}

def normalize_card_type(card_type):
    card_type = card_type.strip().lower()

    # Switch-case style mapping
    card_type_map = {
        "spell card": "Spell",
        "trap card": "Trap",
        "skill card": "Skill",
        "token": "Token"  # Added Token
    }

    # Check if "monster" is in the type
    if "monster" in card_type:
        return "Monster"

    # Use the map to return specific types
    return card_type_map.get(card_type, None)
class Card:
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP):
        self.name = name            # Card's name
        self.id = id
        self.archetype = archetype  # Card's archetype (e.g., Dragon, Spellcaster, etc.)
        self.effect = effect        # Card's effect (description of its ability)
        self.attack = attack        # Card's attack points
        self.defense = defense
        self.level = level          # Card's level (e.g., 4, 7, 12)
        self.EP = EP                # Effect points calculated from the card's effect
        self.card_images = card_images
        self.type = "Generic"       # Default type, overridden in subclasses
        self.NA = self.calculate_na()  # Initially set to None, will be calculated after type is set

    def calculate_na(self):
        """ Calculate the card value (NA) using the default behavior (EP for non-Monster cards). """
        return self.EP  # Non-Monster cards just return their EP value.

    def __str__(self):
        """ Return a string representation of the card (name) """
        return self.name
class MonsterCard(Card):
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP):
        super().__init__(name, id, archetype, effect, attack, defense, level, card_images, EP)
        self.type = "Monster"  # Override type
        self.position = "attack"   # None, "attack", or "defense"

    def calculate_na(self):
        if self.level == 0:  # Check if level is 0 to avoid division by zero
            self.level = 1
        return (self.attack / 100) + (12 / self.level) + self.EP

    def set_position(self, position):
        """ Set the position of the card (attack or defense) """
        print(f"Setting position: {position} (Type: {type(position)})")
        if isinstance(position, str) and position.lower() in {"attack", "defense"}:
            self.position = position.lower()
        else:
            raise ValueError("Invalid position. Choose 'attack' or 'defense'.")

    def __str__(self):
        return f"Monster Card - {self.name}"

class SpellCard(Card):
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP, spell_effect):
        super().__init__(name, id, archetype, effect, attack, defense, level, card_images, EP)
        self.type = "Spell"  # Override type
        self.spell_effect = spell_effect

    def apply_effect(self, target_card):
        """ Apply the spell's effect to a target card """
        print(f"Applying {self.spell_effect} from {self.name} to {target_card.name}")
        
    def __str__(self):
        """ Return a string representation of the spell card """
        return f"Spell Card - {self.name}"
        
class TrapCard(Card):
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP, trap_effect):
        super().__init__(name, id, archetype, effect, attack, defense, level, card_images, EP)
        self.type = "Trap"  # Override type
        self.trap_effect = trap_effect

    def trigger(self, target_card):
        """ Trigger the trap's effect on a target card """
        print(f"Triggering {self.trap_effect} from {self.name} targeting {target_card.name}")

    def __str__(self):
        """ Return a string representation of the trap card """
        return f"Trap Card - {self.name}"

class SkillCard(Card):
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP, skill_effect):
        super().__init__(name, id, archetype, effect, attack, defense, level, card_images, EP)
        self.skill_effect = skill_effect  # A description of the skill's effect
        self.type = "Skill"

    def apply_skill(self, target_card):
        """ Apply the skill effect to a target card """
        print(f"Applying skill {self.skill_effect} from {self.name} to {target_card.name}")

    def __str__(self):
        """ Return a string representation of the skill card """
        return f"Skill Card - {self.name}"

class TokenCard(Card):
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP):
        super().__init__(name, id, archetype, effect, attack, defense, level, card_images, EP)
        self.type = "Token"  # Override type

    def __str__(self):
        return f"Token Card - {self.name}"


def calculate_effect_points(desc):
    points = 0 
    if pd.notnull(desc):  
        desc = desc.lower()
        desc_words = desc.split()  #

        for effect, value in effect_points_mapping.items():
            effect_words = effect.split()  

            if effect_words in (desc_words[i:i + len(effect_words)] for i in range(len(desc_words) - len(effect_words) + 1)):
                points += value  

    return points 

def load_cards_from_csv(filepath):
    # Read the CSV file
    df = pd.read_csv(filepath)

    # Ensure the required columns exist
    required_columns = {'name', 'id', 'desc', 'atk', 'def', 'level', 'archetype', 'card_images', 'type'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset: {missing_columns}")

    # Initialize card list and mapping
    cards = []
    card_map = {}

    for _, row in df.iterrows():
        # Normalize card type
        normalized_type = normalize_card_type(row['type'])
        if not normalized_type:
            raise ValueError(f"Unknown card type: {row['type']}")

        # Calculate Effect Points (EP) using the 'desc' field
        EP = calculate_effect_points(row['desc'])

        # Instantiate the correct card type
        if normalized_type == "Monster":
            card = MonsterCard(
                name=row['name'],
                id=row['id'], 
                archetype=row.get('archetype', ''),  # Archetype might be empty
                effect=row.get('desc', ''),         # Description might be empty
                attack=row['atk'], 
                defense=row['def'],
                level=row['level'], 
                EP=EP,
                card_images=row.get('card_images', '')
            )
        elif normalized_type == "Spell":
            card = SpellCard(
                name=row['name'],
                id=row['id'], 
                archetype=row.get('archetype', ''),  # Archetype might be empty
                effect=row.get('desc', ''),         # Description might be empty
                attack=row['atk'], 
                defense=row['def'],
                level=row['level'], 
                EP=EP,
                card_images=row.get('card_images', ''),
                spell_effect=row.get('desc', '')    # Spell effect derived from description
            )
        elif normalized_type == "Trap":
            card = TrapCard(
                name=row['name'],
                id=row['id'], 
                archetype=row.get('archetype', ''),  # Archetype might be empty
                effect=row.get('desc', ''),         # Description might be empty
                attack=row['atk'], 
                defense=row['def'],
                level=row['level'], 
                EP=EP,
                card_images=row.get('card_images', ''),
                trap_effect=row.get('desc', '')     # Trap effect derived from description
            )
        elif normalized_type == "Skill":
            card = SkillCard(
                name=row['name'],
                id=row['id'], 
                archetype=row.get('archetype', ''),  # Archetype might be empty
                effect=row.get('desc', ''),         # Description might be empty
                attack=row['atk'], 
                defense=row['def'],
                level=row['level'], 
                EP=EP,
                card_images=row.get('card_images', ''),
                skill_effect=row.get('desc', '')    # Skill effect derived from description
            )
        elif normalized_type == "Token":
            card = TokenCard(
            name=row['name'],
            id=row['id'], 
            archetype=row.get('archetype', ''),  # Archetype might be empty
            effect=row.get('desc', ''),         # Description might be empty
            attack=row['atk'], 
            defense=row['def'],
            level=row['level'], 
            EP=EP,
            card_images=row.get('card_images', '')
            )

        # Add the card to the list and mapping
        cards.append(card)
        card_map[card.name.lower()] = card

    return cards, card_map