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
    def __init__(self, name, archetype, effect, atk, level, EP):
        self.name = name            # Card's name
        self.archetype = archetype  # Card's archetype (e.g., Dragon, Spellcaster, etc.)
        self.effect = effect        # Card's effect (description of its ability)
        self.atk = atk              # Card's attack points
        self.level = level          # Card's level (e.g., 4, 7, 12)
        self.EP = EP                # Effect points calculated from the card's effect
        self.NA = self.calculate_na()  # Card value based on the formula

    def calculate_na(self):
        """ Calculate the card value (NA) using the formula """
        if self.level == 0:  # Avoid division by zero
            self.level = 1
        return (self.atk / 100) + (12 / self.level) + self.EP

    def __str__(self):
        """ Return a string representation of the card (name) """
        return self.name

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
    required_columns = {'name', 'desc', 'atk', 'level', 'archetype'}
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
            archetype=row.get('archetype', ''),  # Archetype might be empty
            effect=row.get('desc', ''),         # Description might be empty
            atk=row['atk'], 
            level=row['level'], 
            EP=EP
        )

        cards.append(card)
        card_map[card.name.lower()] = card

    return cards, card_map