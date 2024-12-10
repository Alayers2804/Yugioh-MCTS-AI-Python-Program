import math
import pandas as pd
import numpy as np

class MCTSNode:
    def __init__(self, card_hand, parent=None):
        self.card_hand = card_hand
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0
        self.card_played = None

    def uct_value(self, exploration_factor=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration_factor * math.sqrt(math.log(self.parent.visits + 1) / self.visits)
    
class MCTS:
    def __init__(self, card_data, simulations=1000, mode="pure"):
        self.simulations = simulations
        self.cards = card_data  # A list of all cards (DataFrame of card data)
        self.root = None
        self.mode = mode  # Mode can be 'pure', 'enemy', or 'feature_learning'

    def select(self, node):
        """ Select the best node to expand (based on UCT) """
        best_value = -float('inf')
        best_node = None
        for child in node.children:
            uct_value = child.uct_value()
            if uct_value > best_value:
                best_value = uct_value
                best_node = child
        return best_node

    def expand(self, node):
        """ Generate all possible actions (cards to play from hand) """
        for card in node.card_hand:
            new_hand = [c for c in node.card_hand if c != card]  # Remove the played card
            child_node = MCTSNode(new_hand, parent=node)
            child_node.card_played = card
            node.children.append(child_node)

    def simulate(self, node, enemy_cards=None):
        hand = node.card_hand
        total_score = 0
        if self.mode == "pure":
            for card in hand:
                total_score += card.NA 
        elif self.mode == "enemy":
            for card in hand:
                for enemy_card in enemy_cards:
                    if card.atk > enemy_card.atk:
                        total_score += card.NA 
                    else:
                        total_score -= 5  # Penalty for weaker cards
        elif self.mode == "feature_learning":
            # Incorporate feature-based scoring
            for card in hand:
                total_score += self.feature_based_score(card, enemy_cards)
        return total_score
    
    def feature_based_score(self, card, enemy_cards):
        # This is where the Feature based learning comes from
        score = card.NA  # Start with base card value
        enemy_score = enemy_cards.NA
        keywords = ['destroy', 'banish', 'draw', 'summon', 'inflict']
        if card.effect:
            for keyword in keywords:
                if keyword in card.effect.lower():
                    score += 20  
        return score

    def backpropagate(self, node, result):
        """ Backpropagate the result of the simulation to update the nodes """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
    
    def process_best_move(self, moves_log):
        """Select the best move and remove the played card from the hand."""
        best_child = self.select(self.root)
        if best_child:
            played_card = best_child.card_played
            moves_log.append({
                "played_card": played_card.name,
                "card_id": played_card.id,
            })
            self.root = MCTSNode(self.root.card_hand)
            return True
        else:
            print("No valid moves left.")
            moves_log.append({"message": "No valid moves left"})
            return False  # No moves left

        
    def simulate_round(self, enemy_cards):
        """Expand the root node, simulate results, and backpropagate."""
        self.expand(self.root)
        result = self.simulate(self.root, enemy_cards if self.mode != "pure" else [])
        self.backpropagate(self.root, result)
        
    def determine_mode(self, enemy_cards):
        """Determine the mode dynamically based on the presence of enemy cards."""
        if not enemy_cards:
            print("\nNo enemy cards present. Running in pure MCTS mode (your cards only).")
            return "pure"
        else:
            print("\nEnemy cards detected. Running in MCTS with enemy consideration mode.")
            return "with_enemy"

    def run_simulation(self, initial_hand, enemy_cards):
        """Run one step of the simulation."""
        # Initialize the root if not already done
        if self.root is None:
            self.root = MCTSNode(initial_hand)

        moves_log = []

        # Determine mode
        self.mode = self.determine_mode(enemy_cards)

        # Simulate one round
        self.simulate_round(enemy_cards)

        # Process the best move
        if not self.process_best_move(moves_log):
            moves_log.append({"message": "No valid moves left"})
            return {"log": moves_log, "can_continue": False}  # No valid moves, end simulation

        # Check if hand is empty
        if not self.root.card_hand:
            moves_log.append({"message": "No cards left in your hand"})
            return {"log": moves_log, "can_continue": False}  # End simulation

        return {"log": moves_log, "can_continue": True}

