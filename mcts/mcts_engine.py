import math
import pandas as pd
import numpy as np
from .cards import MonsterCard, SpellCard, TrapCard
class MCTSNode:
    def __init__(self, card_hand, parent=None):
        self.card_hand = card_hand
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.card_played = None

    def uct_value(self, exploration_factor=1.41, epsilon=1e-6):
        """Calculate the UCT value, incorporating inherent card value (like NA) for prioritization."""
        if self.visits == 0:
            # Use the card's NA to break ties for unvisited nodes
            return self.card_played.NA + exploration_factor  # Exploration factor adds preference to unvisited nodes
        return (self.wins / (self.visits + epsilon)) + exploration_factor * math.sqrt(
            math.log(self.parent.visits + epsilon) / (self.visits + epsilon)
        )
    
class MCTS:
    def __init__(self, card_data, simulations=1000, mode="pure"):
        self.simulations = simulations
        self.cards = card_data
        self.root = None
        self.mode = mode 
        self.played_monster = False

    def select(self, node):
        """Select the best node to expand based on UCT and card value."""
        best_value = -float('inf')
        best_node = None
        for child in node.children:
            uct_value = child.uct_value()
            print(f"Card: {child.card_played.name}, UCT Value: {uct_value}, NA: {child.card_played.NA}")
            if uct_value > best_value:
                best_value = uct_value
                best_node = child
        return best_node

    def expand(self, node):
        """Generate all possible actions (cards to play from hand)."""
        played_cards = {child.card_played for child in node.children}
        for card in node.card_hand:
            if card in played_cards:
                continue  # Skip cards that have already been expanded
            print(f"Expanding with card: {card.name} (NA={card.NA})")
            new_hand = [c for c in node.card_hand if c != card]  # Remove the played card
            child_node = MCTSNode(new_hand, parent=node)
            child_node.card_played = card
            node.children.append(child_node)

    @staticmethod
    def determine_monster_position(card, enemy_cards):
        if not isinstance(card, MonsterCard):
            return None  # Only MonsterCards have positions

        if not enemy_cards:
            return "attack"  # Default to attack when there are no enemies

        avg_enemy_attack = sum(c.attack for c in enemy_cards) / len(enemy_cards)
        avg_enemy_defense = sum(c.defense for c in enemy_cards) / len(enemy_cards)

        # Decision logic
        if card.attack > avg_enemy_defense:  # Strong offense
            return "attack"
        elif card.defense > avg_enemy_attack:  # Strong defense
            return "defense"
        else:  # Balanced
            return "attack" if card.attack >= card.defense else "defense"

    def simulate(self, node, enemy_cards=None):
        hand = node.card_hand
        total_score = 0

        for card in hand:
            print(f"Card: {card.name}, NA: {card.NA}")

            if isinstance(card, MonsterCard):
                # Determine position during simulation but do not overwrite existing positions
                if not card.position:
                    position = self.determine_monster_position(card, enemy_cards)
                    card.set_position(position)
                print(f"Simulated Position for {card.name}: {card.position}")

            # Add card's NA to the total score
            total_score += card.NA

        return total_score

    def evaluate_generic_card(self, card, enemy_cards):
        """Evaluate any card except MonsterCard based on its attributes."""
        card_score = card.NA  # Start with the base score (e.g., intrinsic value of the card)

        # Example of card-specific evaluations (you can extend this based on your game logic)
        if isinstance(card, SpellCard):
            # Evaluate spell card (you can adjust this logic as needed)
            if 'destroy' in card.effect.lower():
                card_score += 20  # Add bonus for destruction effects
            if 'buff' in card.effect.lower():
                card_score += 15  # Add bonus for buff effects

        elif isinstance(card, TrapCard):
            # Evaluate trap card (you can adjust this logic as needed)
            if 'counter' in card.effect.lower():
                card_score += 25  # Bonus for counter-trap effects

        # Add other card type-specific evaluation logic here as needed

        return card_score
        
    def calculate_archetype_synergy(self, card, hand):
        bonus = 0
        for other_card in hand:
            if card != other_card and card.archetype == other_card.archetype:
                bonus += 10  # Bonus for matching archetype
            return bonus


    def calculate_synergy_bonus(self, card, hand):
        bonus = 0
        if 'spellcaster' in card.effect.lower():
            bonus += 15 
        bonus += self.calculate_archetype_synergy(card, hand)
        return bonus

    def feature_based_score(self, card, enemy_cards):
        """Evaluate card based on features and interactions with enemy cards."""
        score = card.NA
        enemy_cards = ""
        if 'destroy' in card.effect.lower():
            score += 20
        return score

    def backpropagate(self, node, result):
        """ Backpropagate the result of the simulation to update the nodes """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
    
    def process_best_move(self, moves_log, enemy_cards):
        """Select the best move and remove the played card from the hand."""
        best_child = self.select(self.root)
        played_card = best_child.card_played

        if isinstance(played_card, MonsterCard):
            # Determine the correct position using the provided enemy cards
            position = self.determine_monster_position(played_card, enemy_cards)
            played_card.set_position(position)  # Set the card's position

            print(f"Card: {played_card.name}, Position: {position}")
            
            # Ensure that a Monster card can only be played once
            if self.played_monster:
                print(f"Monster card {played_card.name} cannot be played again.")
                return False
            self.played_monster = True  # Mark that a Monster card has been played

        # Log the move
        moves_log.append({
            "played_card": played_card.name,
            "card_id": played_card.id,
            "type": played_card.type,
            "na_value": played_card.NA,
            "position": position if isinstance(played_card, MonsterCard) else ""  # Empty for non-Monster cards
        })

        # Remove the played card from the hand and set it as the new root
        new_hand = [c for c in self.root.card_hand if c != played_card]
        self.root = MCTSNode(new_hand)
        return True
        
    def simulate_round(self, enemy_cards):
        """Expand the root node, simulate results, and backpropagate."""
        self.expand(self.root)
        result = self.simulate(self.root, enemy_cards if self.mode != "pure" else [])
        self.backpropagate(self.root, result)
        
    def determine_mode(self, enemy_cards):
        if not enemy_cards:
            print("\nNo enemy cards present. Running in pure MCTS mode (your cards only).")
            return "pure"
        else:
            print("\nEnemy cards detected. Running in MCTS with enemy consideration mode.")
            return "with_enemy"

    def run_simulation(self, initial_hand, enemy_cards):
        """Run simulations continuously until no valid moves can be made."""
        moves_log = []

        if self.root is None:
            self.root = MCTSNode(initial_hand)

        self.mode = self.determine_mode(enemy_cards)

        # Run simulations until the hand is empty or no valid moves can be made
        while self.root.card_hand:
            self.simulate_round(enemy_cards)
            if not self.process_best_move(moves_log, enemy_cards):
                break  # Exit if no valid moves are left

        # Final check for empty hand
        if not self.root.card_hand:
            moves_log.append({"message": "No cards left in your hand"})
            return {"log": moves_log, "can_continue": True}

        return {"log": moves_log, "can_continue": True}

