from flask import Flask, render_template, jsonify, request
from mcts.mcts_engine import MCTS
from mcts.cards import load_cards_from_csv, MonsterCard, SpellCard, TokenCard, TrapCard, SkillCard

app = Flask(__name__)

filepath = "yugioh_cards_preprocessed_real.csv"
cards, cards_name = load_cards_from_csv(filepath)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route('/get_all_cards', methods=['GET'])
def get_card_names():
    """API endpoint to return card names with types, optionally filtered by a query."""
    query = request.args.get('q', '').lower()
    if query:  # Filter only if a query is provided
        matching_cards = [{"name": card.name, "type": card.type} for card in cards if query in card.name.lower()]
    else:
        matching_cards = [{"name": card.name, "type": card.type} for card in cards]  # Return all cards
    return jsonify(matching_cards)

@app.route('/machine-learning', methods=['POST'])
def machine_learning():
    """Run one step of the MCTS simulation."""
    try:
        # Parse Input
        data = request.json
        initial_hand_names = data.get('initial_hand', [])
        user_field = data.get("user_field", [])
        enemy_card_names = data.get('enemy_cards', [])
        # mode = data.get('mode', 'pure')

        # Validate and Convert Input
        user_hand = [cards_name[name.lower()] for name in initial_hand_names if name.lower() in cards_name]
        user_field = [cards_name[name.lower()] for name in user_field if name.lower() in cards_name]
        enemy_cards = [cards_name[name.lower()] for name in enemy_card_names if name.lower() in cards_name]
        if not user_hand:
            return jsonify({"error": "Initial hand is empty or invalid"}), 400

        # Reset the MCTS instance for a new simulation
        mcts = MCTS(card_data=cards, simulations=1000, mode=None)

        # Run one step of the simulation
        result = mcts.run_simulation(user_hand, user_field, enemy_cards)

        step_log_with_images = []
        for log in result["log"]:
            if "played_card" in log:
                card_name = log["played_card"].lower()
                card = cards_name.get(card_name)
                print(f"Card: {card_name}, ID: {card.id if card else 'None'}")  # Debugging line
                
                if isinstance(card, MonsterCard):  # Check if the card is a MonsterCard
                    position = card.position if card.position else ""  # Only for MonsterCards
                else:
                    position = ""  # For non-MonsterCards, use an empty string or skip

                step_log_with_images.append({
                    "played_card": card.name if card else None,
                    "card_id": card.id if card else None,
                    "na_Value" : card.NA if card else None,
                    "position": position  # Set the position only for MonsterCards
                })
            else:
                step_log_with_images.append(log)

        user_hand_cards=[]
        for card in user_hand:
            user_hand_cards.append({
                "card_name": card.name,
                "card_id": card.id,
                "na_Value": card.NA,
                "position": ""  # Assuming no position for user hand cards
            })
        
        return jsonify({
            "user_hand": user_hand_cards,
            "step_log": step_log_with_images,
            "can_continue": result["can_continue"]
        })
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)