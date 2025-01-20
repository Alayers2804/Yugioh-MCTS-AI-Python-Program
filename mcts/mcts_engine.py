import math
from .Cards import MonsterCard, SpellCard, TrapCard
class MCTSNode:
    def __init__(self, card_hand, parent=None, user_field=None):
        self.card_hand = card_hand
        self.user_field = user_field if user_field else []
        self.parent = parent
        self.children = []
        self.card_played = None
        self.visits = 0
        self.wins = 0
        
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
        
    @staticmethod
    def determine_monster_position(card, enemy_cards):
        if not isinstance(card, MonsterCard):
            return None  

        if not enemy_cards:
            return "attack"  

        avg_enemy_attack = sum(c.attack for c in enemy_cards) / len(enemy_cards)
        avg_enemy_defense = sum(c.defense for c in enemy_cards) / len(enemy_cards)

        if card.attack > avg_enemy_defense:
            return "attack"
        elif card.defense > avg_enemy_attack:
            return "defense"
        else:  # Balanced
            return "attack" if card.attack >= card.defense else "defense"

    def boost_archetype_na(self, card, user_field, user_hand, boost_value=5):  
        # Check if user_field is empty  
        if not user_field:  
            print(f"User field is empty. Skipping boost for {card.name}.")  
            return  # Skip boosting if user_field is empty  
    
        # Reset NA to its default value before boosting  
        default_na_value = card.default_na if hasattr(card, 'default_na') else card.NA  # Assuming 'default_na' holds the default value  
        card.NA = default_na_value  
        print(f"Reset NA for {card.name} to default value: {card.NA}.")  
    
        if not card.archetype or card.archetype.lower() in ["none", "empty"]:  
            print(f"{card.name} has an empty or None archetype. NA remains {card.NA}.")  
            return  # Skip boosting for cards with no archetype  
    
        if hasattr(card, 'boosted') and card.boosted:  
            print(f"{card.name} has already been boosted. NA remains {card.NA}.")  
            return  # Skip boosting if already done  
    
        # Check if archetype matches any card in the user field and hand  
        archetype_match_in_field = any(field_card.archetype == card.archetype for field_card in user_field)  
        archetype_match_in_hand = any(hand_card.archetype == card.archetype for hand_card in user_hand)  
    
        # Boost NA if there is an archetype match in both field and hand  
        if archetype_match_in_field and archetype_match_in_hand:  
            card.NA += boost_value  
            print(f"Boosted NA for {card.name} (archetype: {card.archetype}) by {boost_value}. New NA: {card.NA}.")  
            card.boosted = True  # Mark as boosted  
        else:  
            print(f"No archetype match found for {card.name}. NA remains {card.NA}.")  


    def check_enough_tributes(self, user_field, tribute_needed):
        """Check if the user has enough cards for the tribute and return updated field."""
        if len(user_field) < tribute_needed:
            print(f"Not enough cards for tribute. Need {tribute_needed}, but only have {len(user_field)}.")
            return []
        return user_field  
    
    def reset_boosted_status(self, cards):  
        for card in cards:  
            # Debugging before resetting  
            if hasattr(card, 'boosted'):  
                print(f"Before Reset: {card.name} - boosted: {card.boosted}, NA: {card.NA}")  
    
            # Reset the boosted status  
            if hasattr(card, 'boosted'):  
                card.boosted = False  # Reset the boosted status  
    
            # Reset NA to its default value  
            if hasattr(card, 'default_na'):  
                card.NA = card.default_na  # Assign the default NA value  
                print(f"Reset NA for {card.name} to its default value: {card.NA}.")  
            else:  
                print(f"{card.name} does not have a default NA value. NA remains: {card.NA}.")  
    
            # Debugging after resetting  
            print(f"After Reset: {card.name} - boosted: {card.boosted}, NA: {card.NA}")  

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

        for card in node.card_hand:
            if isinstance(card, MonsterCard):
                if not self.played_monster:  # Ensure only one monster is played
                    tribute_needed = card.requires_tribute()
                    if len(node.user_field) < tribute_needed:
                        print(f"Skipping {card.name}: Not enough tributes.")
                        continue  # Skip playing this card if not enough tributes

                    # Proceed if there are enough tributes
                    new_field = self.check_enough_tributes(node.user_field, tribute_needed)
                    self.boost_archetype_na(card, node.user_field, node.card_hand)
                    child_node = MCTSNode(
                        card_hand=[c for c in node.card_hand if c != card],  # Remove played card from hand
                        user_field=new_field,  # Updated field
                        parent=node
                    )
                    child_node.card_played = card
                    node.children.append(child_node)
            else:
                    self.boost_archetype_na(card, node.user_field, node.card_hand)
                    child_node = MCTSNode(
                        card_hand=[c for c in node.card_hand if c != card],  # Remove played card from hand
                        user_field=node.user_field,
                        parent=node
                    )
                    child_node.card_played = card
                    node.children.append(child_node)
                    

        node.card_hand = [card for card in node.card_hand]

        if not self.played_monster:
            print("No monster card was played.")
        
    def simulate(self, node, enemy_cards=None):
        hand = node.card_hand
        total_score = 0

        for card in hand:
            # Ensure boosting is only done under valid conditions
            self.boost_archetype_na(card, user_field=node.user_field, user_hand=hand)
            print(f"Card: {card.name}, NA: {card.NA}")
            
            if isinstance(card, MonsterCard):
                tribute_needed = card.requires_tribute()
                
                if tribute_needed > 0:
                    # Check if the player has enough cards for the tribute before tributing
                    if len(node.user_field) < tribute_needed:
                        print(f"Skipping {card.name} (Level {card.level}): Not enough tributes.")
                        continue 

                    # If there are enough cards for tribute, remove them only when necessary
                    node.user_field = self.check_enough_tributes(node.user_field, tribute_needed)
                    
                    position = self.determine_monster_position(card, enemy_cards)
                    card.set_position(position)
                    print(f"Simulated Position for {card.name}: {card.position}")

            total_score += card.NA

        return total_score

    def backpropagate(self, node, result):
        """ Backpropagate the result of the simulation to update the nodes """
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
    
    def process_best_move(self, moves_log, enemy_cards):
        best_child = self.select(self.root)
        if best_child is None:
            print("No valid moves to process.")
            return False

        played_card = best_child.card_played

        if isinstance(played_card, MonsterCard):
            tribute_needed = played_card.requires_tribute()
            if len(self.root.user_field) < tribute_needed:
                print(f"Cannot play {played_card.name} (Level {played_card.level}): Not enough tributes.")
                return False  # Skip if not enough tributes
            self.played_monster = True
            self.root.user_field = self.check_enough_tributes(self.root.user_field, tribute_needed)
            position = self.determine_monster_position(played_card, enemy_cards)
            played_card.set_position(position)

            print(f"Played monster card: {played_card.name}, Position: {position}")

        # Record the played card in the log
        moves_log.append({
            "played_card": played_card.name,
            "card_id": played_card.id,
            "type": played_card.type,
            "na_value": played_card.NA,
            "position": played_card.position if isinstance(played_card, MonsterCard) else ""
        })

        # Update the root node
        new_hand = [c for c in self.root.card_hand if c != played_card]
        self.root = MCTSNode(new_hand, user_field=self.root.user_field)
        return True

        
    def simulate_round(self, enemy_cards):
        print(f"Simulating round. Cards in hand: {[card.name for card in self.root.card_hand]}")
        print(f"User field before simulation: {[card.name for card in self.root.user_field]}")

        self.expand(self.root)  # Process the card hand and expand the tree
        result = self.simulate(self.root)
        print(f"Simulation result: {result}")

        self.backpropagate(self.root, result)  # Backpropagate the result to the root
        print("Backpropagation complete.")

        # After expanding, if no valid moves were found, ensure the cards are updated
        if not self.root.card_hand:
            print("No cards left in the hand after processing.")
        
    def determine_mode(self, enemy_cards):
        if not enemy_cards:
            print("\nNo enemy cards present. Running in pure MCTS mode (your cards only).")
            return "pure"
        else:
            print("\nEnemy cards detected. Running in MCTS with enemy consideration mode.")
            return "with_enemy"

    def run_simulation(self, initial_hand, user_field, enemy_cards):
        """Run simulations continuously until no valid moves can be made."""
        moves_log = []
        
        self.reset_boosted_status(initial_hand)

        if self.root is None:
            print("Initializing root node with:")
            print(f"Initial hand: {[card.name for card in initial_hand]}")
            print(f"User field: {[card.name for card in user_field]}")
            self.root = MCTSNode(initial_hand, user_field=user_field)

        self.mode = self.determine_mode(enemy_cards)
        while self.root.card_hand:
            self.simulate_round(enemy_cards)
            if not self.process_best_move(moves_log, enemy_cards):
                break 

        if not self.root.card_hand:
            moves_log.append({"message": "No cards left in your hand"})
            return {"log": moves_log, "can_continue": True}

        return {"log": moves_log, "can_continue": True}
