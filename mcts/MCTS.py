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
    
    def process_best_move(self):
        """Select the best move and remove the played card from the hand."""
        best_child = self.select(self.root)
        if best_child:
            played_card = best_child.card_played
            print(f"\nBest card to play: {played_card.name}")
            self.root.card_hand.remove(played_card)
            print(f"\nRemoved {played_card.name} from hand.")
            # Update the root node
            self.root = MCTSNode(self.root.card_hand)
            return True  # Move successful
        else:
            print("No valid moves left.")
            return False  # No moves left
        
    def simulate_round(self, enemy_cards):
        """Expand the root node, simulate results, and backpropagate."""
        self.expand(self.root)
        result = self.simulate(self.root, enemy_cards if self.mode != "pure" else [])
        self.backpropagate(self.root, result)
    
    def manage_enemy_cards(self, enemy_cards):
        """Allow the user to add new enemy cards during the simulation."""
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
                
    def manage_player_cards(self, player_hand):
        """Allow the user to add or remove cards from the player's hand during the simulation."""
        print("\nManage your cards:")
        print("1. Add a card to your hand")
        print("2. Remove a card from your hand")
        print("3. Done")

        while True:
            choice = input("Select an option (1/2/3): ").strip()
            
            if choice == "1":  # Add a card
                available_cards = [card for card in self.cards if card not in player_hand]
                if available_cards:
                    print("\nAvailable cards to add to your hand:")
                    for card in available_cards:
                        print(f"- {card.name}")
                    card_name = input("Enter the name of the card to add: ").strip().lower()
                    matching_card = next((card for card in available_cards if card.name.lower() == card_name), None)
                    if matching_card:
                        player_hand.append(matching_card)
                        print(f"Added {matching_card.name} to your hand.")
                    else:
                        print("Invalid card name. No card added.")
                else:
                    print("No more cards available to add to your hand.")
            
            elif choice == "2":  # Remove a card
                if player_hand:
                    print("\nCurrent cards in your hand:")
                    for card in player_hand:
                        print(f"- {card.name}")
                    card_name = input("Enter the name of the card to remove: ").strip().lower()
                    matching_card = next((card for card in player_hand if card.name.lower() == card_name), None)
                    if matching_card:
                        player_hand.remove(matching_card)
                        print(f"Removed {matching_card.name} from your hand.")
                    else:
                        print("Invalid card name. No card removed.")
                else:
                    print("Your hand is empty. Nothing to remove.")
            
            elif choice == "3":  # Done
                print("Finished managing your cards.")
                break
            
            else:
                print("Invalid choice. Please select 1, 2, or 3.")

    def determine_mode(self, enemy_cards):
        """Determine the mode dynamically based on the presence of enemy cards."""
        if not enemy_cards:
            print("\nNo enemy cards present. Running in pure MCTS mode (your cards only).")
            return "pure"
        else:
            print("\nEnemy cards detected. Running in MCTS with enemy consideration mode.")
            return "with_enemy"

    def run_simulation(self, initial_hand, enemy_cards):
        """Main simulation loop."""
        self.root = MCTSNode(initial_hand)

        while True:
            # Determine mode
            self.mode = self.determine_mode(enemy_cards)

            # Simulate a round
            self.simulate_round(enemy_cards)

            # Process the best move
            if not self.process_best_move():
                break  # Exit if no valid moves

            # Check if hand is empty
            if not self.root.card_hand:
                print("\nNo cards left in your hand.")
                break
            
            self.manage_player_cards(self.root.card_hand)

            # Manage enemy cards
            self.manage_enemy_cards(enemy_cards)

            # Continue simulation or exit
            continue_sim = input("\nContinue simulation? (yes/no): ").strip().lower()
            if continue_sim != "yes":
                break
