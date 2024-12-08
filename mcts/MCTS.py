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
        """Simulate the outcome of a game based on the current mode"""
        hand = node.card_hand
        total_score = 0

        if self.mode == "pure":
            # Pure card value calculation
            for card in hand:
                total_score += card.NA  # Use the card's calculated value
        elif self.mode == "enemy":
            # Consider enemy cards
            for card in hand:
                for enemy_card in enemy_cards:
                    if card.atk > enemy_card.atk:
                        total_score += card.NA  # Positive score for stronger cards
                    else:
                        total_score -= 5  # Penalty for weaker cards
        elif self.mode == "feature_learning":
            # Incorporate feature-based scoring
            for card in hand:
                total_score += self.feature_based_score(card, enemy_cards)
        
        return total_score
    
    def feature_based_score(self, card, enemy_cards):
        """Score based on advanced features like 'destroy', 'banish', etc."""
        score = card.NA  # Start with base card value
        keywords = ['destroy', 'banish', 'draw', 'summon', 'inflict']
        if card.effect:
            for keyword in keywords:
                if keyword in card.effect.lower():
                    score += 20  # Assign bonus points for impactful effects
        return score

    def backpropagate(self, node, result):
        """ Backpropagate the result of the simulation to update the nodes """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def run(self, initial_hand, card_name):
        """Run MCTS with dynamic mode switching based on enemy field state."""
        self.root = MCTSNode(initial_hand)
        enemy_cards = card_name if card_name else []

        while True:
            # Determine the mode dynamically based on the presence of enemy cards
            if not enemy_cards:
                print("\nNo enemy cards present. Running in pure MCTS mode (your cards only).")
                current_mode = "pure"
            else:
                print("\nEnemy cards detected. Running in MCTS with enemy consideration mode.")
                current_mode = "with_enemy"

            # Expand and simulate
            node = self.root
            self.expand(node)
            if current_mode == "pure":
                result = self.simulate(node, [])  # Simulate with no enemy cards
            else:
                result = self.simulate(node, enemy_cards)  # Simulate with enemy cards
            self.backpropagate(node, result)

            # Select the best child
            best_child = self.select(self.root)
            if best_child:
                print(f"\nBest card to play: {best_child.card_played.name}")
                # Remove the played card from the hand
                played_card = best_child.card_played
                self.root.card_hand.remove(played_card)
                print(f"\nRemoved {played_card.name} from hand.")
            else:
                print("No valid moves left.")
                break  # Exit the loop when no valid moves are available

            # Check if the hand is empty
            if not self.root.card_hand:
                print("\nNo cards left in your hand.")
                break

            # Reinitialize the root for MCTS with the updated hand
            self.root = MCTSNode(self.root.card_hand)

            # Simulate adding a new enemy card
            add_enemy_card = input("\nAdd a new enemy card? (yes/no): ").strip().lower()
            if add_enemy_card == "yes":
                available_enemy_cards = [card for card in self.cards if card not in enemy_cards]
                if available_enemy_cards:
                    print("\nAvailable cards to add as enemy:")
                    for card in available_enemy_cards:
                        print(f"- {card.name}")
                    card_name = input("Enter the name of the enemy card to add: ").strip().lower()
                    matching_card = next((card for card in available_enemy_cards if card.name.lower() == card_name), None)
                    if matching_card:
                        enemy_cards.append(matching_card)
                        print(f"New enemy card added: {matching_card.name}")
                    else:
                        print("Invalid card name. No card added.")
                else:
                    print("No more cards available to add to the enemy field.")

            # Continue simulation or exit
            continue_sim = input("\nContinue simulation? (yes/no): ").strip().lower()
            if continue_sim != "yes":
                break