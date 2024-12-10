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

class Card:
    def __init__(self, name, id, archetype, effect, attack, defense, level, card_images, EP):
        self.name = name            # Card's name
        self.id = id,
        self.archetype = archetype  # Card's archetype (e.g., Dragon, Spellcaster, etc.)
        self.effect = effect        # Card's effect (description of its ability)
        self.atk = attack              # Card's attack points
        self.defense = defense
        self.level = level          # Card's level (e.g., 4, 7, 12)
        self.EP = EP                # Effect points calculated from the card's effect
        self.card_images = card_images
        self.NA = self.calculate_na()  # Card value based on the formula

    def calculate_na(self):
        """ Calculate the card value (NA) using the formula """
        if self.level == 0:  # Avoid division by zero
            self.level = 1
        return (self.atk / 100) + (12 / self.level) + self.EP

    def __str__(self):
        """ Return a string representation of the card (name) """
        return self.name

class MonsterCard(Card):
    def __init__(self, name, id, archetype, effect, atk, level, card_images, EP):
        super().__init__(name, id, archetype, effect, atk, level, card_images, EP)
        self.position = None  # None, "attack", or "defense"

    def set_position(self, position):
        """ Set the position of the card (attack or defense) """
        if position.lower() in {"attack", "defense"}:
            self.position = position.lower()
        else:
            raise ValueError("Invalid position. Choose 'attack' or 'defense'.")

    def can_play(self):
        """ Check if the card can be played this turn """
        return not self.played

    def play_card(self):
        """ Mark the card as played """
        if self.can_play():
            self.played = True
        else:
            raise Exception(f"Card {self.name} is already played this turn.")

class SpellCard(Card):
    def __init__(self, name, id, archetype, effect, atk, level, card_images, EP, spell_effect):
        super().__init__(name, id, archetype, effect, atk, level, card_images, EP)
        self.spell_effect = spell_effect  # A description of the spell's effect

    def apply_effect(self, target_card):
        """ Apply the spell's effect to a target card """
        print(f"Applying {self.spell_effect} from {self.name} to {target_card.name}")
        
class TrapCard(Card):
    def __init__(self, name, id, archetype, effect, atk, level, card_images, EP, trap_effect):
        super().__init__(name, id, archetype, effect, atk, level, card_images, EP)
        self.trap_effect = trap_effect  # A description of the trap's effect

    def trigger(self, target_card):
        """ Trigger the trap's effect on a target card """
        print(f"Triggering {self.trap_effect} from {self.name} targeting {target_card.name}")

def calculate_effect_points(desc):
    points = 0
    if pd.notnull(desc):
        for effect, value in effect_points_mapping.items():
            if effect in desc.lower():
                points += value
    return points

def load_cards_from_csv(filepath):
    # Read the CSV file
    df = pd.read_csv(filepath)

    # Ensure the required columns exist
    required_columns = {'name', 'id', 'desc', 'atk', 'level', 'archetype', 'card_images'}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset: {missing_columns}")

    # Initialize card list and mapping
    cards = []
    card_map = {}

    for _, row in df.iterrows():
        # Calculate Effect Points (EP) using the 'desc' field
        EP = calculate_effect_points(row['desc'])

        card = Card(
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

        cards.append(card)
        card_map[card.name.lower()] = card

    return cards, card_map