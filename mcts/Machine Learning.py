from Cards import load_cards_from_csv
from MCTS import MCTS
import pandas as pd
import numpy as np
import random

def get_mode_from_user():
    modes = ["pure", "enemy", "feature_learning"]
    print("\nSelect MCTS mode:")
    print("1. Pure (Only card value calculation)")
    print("2. Enemy (Considers enemy cards)")
    print("3. Feature Learning (Considers card effects like destroy, banish, etc.)")

    while True:
        try:
            choice = int(input("Enter the number of your choice (1-3): ").strip())
            if 1 <= choice <= len(modes):
                return modes[choice - 1]
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    # Load cards from CSV
    filepath = "yugioh_cards_preprocessed.csv"
    cards, cards_name = load_cards_from_csv(filepath)

    print("Available cards in the deck:")
    for card in cards:
        print(f"- {card.name}")
    
    print(len(cards))

    # Input initial hand
    # initial_hand = []
    # while len(initial_hand) < 4:
    #     card_name = input(f"Enter card name ({len(initial_hand)+1}/5): ").strip().lower()
    #     if card_name in cards_name:
    #         initial_hand.append(cards_name[card_name])
    #     else:
    #         print("Invalid card name. Please enter a valid card from the deck.")
    
    # debugging purpose
    initial_hand = random.sample(cards, 4)
    print("\nRandomized Initial Hand:")
    for card in initial_hand:
            print(f"- {card.name} - {card.NA} - {card.EP}" )

    # Input enemy cards
    enemy_cards = []
    print("\nEnter enemy cards by name to define the field. Type 'done' when finished.")
    while True:
        card_name = input(f"Enter enemy card name ({len(enemy_cards)+1}): ").strip().lower()
        if card_name == "done":
            break
        if card_name in cards_name:
            enemy_cards.append(cards_name[card_name])
        else:
            print("Invalid card name. Please enter a valid card from the deck.")

    
    mode = get_mode_from_user()
    mcts = MCTS(card_data=cards, simulations=1000, mode=mode if mode == "feature_learning" else None)
    best_card = mcts.run(initial_hand, enemy_cards)

    print("\nYour initial hand:")
    for card in initial_hand:
        print(f"- {card.name} (ATK: {card.atk}, Level: {card.level}, EP: {card.EP})")

    print("\nEnemy field:")
    for card in enemy_cards:
        print(f"- {card.name} (ATK: {card.atk}, Level: {card.level}, EP: {card.EP})")

    # Output best card to play
    if best_card:
        print(f"\nThe best card to play is: {best_card.name} - {best_card.NA}")
    else:
        print("\nNo valid moves left.")

