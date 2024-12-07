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
    def __init__(self, card_data, simulations=1000):
        self.simulations = simulations
        self.cards = card_data  # A list of all cards (DataFrame of card data)
        self.root = None

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

    def simulate(self, node, enemy_cards):
        hand = node.card_hand
        total_score = 0

        print("\nSimulating with the following enemy cards:")
        for enemy_card in enemy_cards:
                print(f"- {enemy_card.name} (ATK: {enemy_card.atk}, Level: {enemy_card.level}, EP: {enemy_card.EP})")

        for card in hand:
            for enemy_card in enemy_cards:
                if card.atk > enemy_card.atk:
                    total_score += card.NA  
            else:
                total_score -= 5  
        return total_score

    def backpropagate(self, node, result):
        """ Backpropagate the result of the simulation to update the nodes """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def run(self, initial_hand, card_name):
        """Run MCTS with user-defined enemy cards."""
        self.root = MCTSNode(initial_hand)
        while True:
            enemy_cards = card_name
            node = self.root
            self.expand(node)
            result = self.simulate(node, enemy_cards)
            self.backpropagate(node, result)
            best_child = self.select(self.root)
            if best_child:
                print(f"\nBest card to play: {best_child.card_played.name}")
            else:
                print("No valid moves left.")
            continue_sim = input("\nContinue simulation? (yes/no): ").strip().lower()
            if continue_sim != "yes":
                break
