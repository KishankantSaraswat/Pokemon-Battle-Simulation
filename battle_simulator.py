import math
import random
from copy import deepcopy

# type effectiveness chart - kinda messy but works
type_chart = {
    "normal": {"rock":0.5, "ghost":0.0, "steel":0.5},
    "fire": {"grass":2.0, "ice":2.0, "bug":2.0, "steel":2.0, "water":0.5, "fire":0.5, "rock":0.5, "dragon":0.5},
    "water": {"fire":2.0, "ground":2.0, "rock":2.0, "water":0.5, "grass":0.5, "dragon":0.5},
    "electric": {"water":2.0, "flying":2.0, "electric":0.5, "grass":0.5, "ground":0.0, "dragon":0.5},
    "grass": {"water":2.0, "ground":2.0, "rock":2.0, "fire":0.5, "grass":0.5, "poison":0.5, "flying":0.5, "bug":0.5, "dragon":0.5, "steel":0.5},
    "ice": {"grass":2.0, "ground":2.0, "flying":2.0, "dragon":2.0, "fire":0.5, "water":0.5, "ice":0.5, "steel":0.5},
    "fighting": {"normal":2.0, "ice":2.0, "rock":2.0, "dark":2.0, "steel":2.0, "poison":0.5, "flying":0.5, "psychic":0.5, "bug":0.5, "fairy":0.5, "ghost":0.0},
    "poison": {"grass":2.0, "fairy":2.0, "poison":0.5, "ground":0.5, "rock":0.5, "ghost":0.5, "steel":0.0},
    "ground": {"fire":2.0, "electric":2.0, "poison":2.0, "rock":2.0, "steel":2.0, "grass":0.5, "bug":0.5, "flying":0.0},
    "flying": {"electric":0.5, "ice":0.5, "rock":0.5, "grass":2.0, "fighting":2.0, "bug":2.0},
    "psychic": {"fighting":2.0, "poison":2.0, "psychic":0.5, "steel":0.5, "dark":0.0},
    "bug": {"grass":2.0, "psychic":2.0, "dark":2.0, "fire":0.5, "fighting":0.5, "poison":0.5, "flying":0.5, "ghost":0.5, "steel":0.5, "fairy":0.5},
    "rock": {"fire":2.0, "ice":2.0, "flying":2.0, "bug":2.0, "fighting":0.5, "ground":0.5, "steel":0.5},
    "ghost": {"psychic":2.0, "ghost":2.0, "dark":0.5, "normal":0.0},
    "dragon": {"dragon":2.0, "steel":0.5, "fairy":0.0},
    "dark": {"fighting":0.5, "ghost":2.0, "psychic":2.0, "dark":0.5, "fairy":0.5},
    "steel": {"ice":2.0, "rock":2.0, "fairy":2.0, "fire":0.5, "water":0.5, "electric":0.5, "steel":0.5},
    "fairy": {"fighting":2.0, "dragon":2.0, "dark":2.0, "fire":0.5, "poison":0.5, "steel":0.5}
}

# moves and stuff - just added what I thought would work
moves_db = {
    # basic normal moves
    "tackle": {"power": 40, "type": "normal", "accuracy": 100, "category": "physical"},
    "body_slam": {"power": 85, "type": "normal", "accuracy": 100, "category": "physical"},
    "hyper_beam": {"power": 150, "type": "normal", "accuracy": 90, "category": "special"},  # op move
    
    # fire type stuff
    "ember": {"power": 40, "type": "fire", "accuracy": 100, "category": "special"},
    "flamethrower": {"power": 90, "type": "fire", "accuracy": 100, "category": "special"},  # classic move
    "fire_blast": {"power": 110, "type": "fire", "accuracy": 85, "category": "special"},
    
    # water attacks
    "water_gun": {"power": 40, "type": "water", "accuracy": 100, "category": "special"},
    "surf": {"power": 90, "type": "water", "accuracy": 100, "category": "special"},
    "hydro_pump": {"power": 110, "type": "water", "accuracy": 80, "category": "special"},  # sometimes misses
    
    # Electric moves
    "thunder_shock": {"power": 40, "type": "electric", "accuracy": 100, "category": "special"},
    "thunderbolt": {"power": 90, "type": "electric", "accuracy": 100, "category": "special"},
    "thunder": {"power": 110, "type": "electric", "accuracy": 70, "category": "special"},
    
    # Grass moves
    "vine_whip": {"power": 45, "type": "grass", "accuracy": 100, "category": "physical"},
    "razor_leaf": {"power": 55, "type": "grass", "accuracy": 95, "category": "physical"},
    "solar_beam": {"power": 120, "type": "grass", "accuracy": 100, "category": "special"},
    
    # Fighting moves
    "karate_chop": {"power": 50, "type": "fighting", "accuracy": 100, "category": "physical"},
    "brick_break": {"power": 75, "type": "fighting", "accuracy": 100, "category": "physical"},
    "close_combat": {"power": 120, "type": "fighting", "accuracy": 100, "category": "physical"},
    
    # Psychic moves
    "confusion": {"power": 50, "type": "psychic", "accuracy": 100, "category": "special"},
    "psychic": {"power": 90, "type": "psychic", "accuracy": 100, "category": "special"},
    "psybeam": {"power": 65, "type": "psychic", "accuracy": 100, "category": "special"},
    
    # Recovery/Status moves
    "rest": {"power": 0, "type": "psychic", "accuracy": 100, "category": "status"},
    "recover": {"power": 0, "type": "normal", "accuracy": 100, "category": "status"},
    "roost": {"power": 0, "type": "flying", "accuracy": 100, "category": "status"},
    
    # Ice moves
    "ice_beam": {"power": 90, "type": "ice", "accuracy": 100, "category": "special"},
    "blizzard": {"power": 110, "type": "ice", "accuracy": 70, "category": "special"},
    
    # Rock moves  
    "rock_slide": {"power": 75, "type": "rock", "accuracy": 90, "category": "physical"},
    "stone_edge": {"power": 100, "type": "rock", "accuracy": 80, "category": "physical"},
}

def get_moves(poke_data):
    # get moves for a pokemon - tried to make it smart
    types = [t.lower() for t in poke_data.get('types', ['normal'])]
    name = poke_data.get('name', '').lower()
    stats = poke_data.get('stats', {})
    
    moves = []  # will store the moves here
    
    # hardcoded moves for some popular pokemon
    special_moves = {
        'mewtwo': ['psychic', 'psybeam', 'confusion', 'hyper_beam'],  # legendary
        'mew': ['psychic', 'confusion', 'psybeam', 'body_slam'], 
        'pikachu': ['thunderbolt', 'thunder_shock', 'thunder', 'tackle'],  # mascot
        'charizard': ['flamethrower', 'fire_blast', 'ember', 'body_slam'],
        'blastoise': ['surf', 'water_gun', 'hydro_pump', 'body_slam'],  # water starter
        'venusaur': ['solar_beam', 'razor_leaf', 'vine_whip', 'body_slam'],
        'gengar': ['confusion', 'psybeam', 'tackle', 'body_slam'],
        'alakazam': ['psychic', 'confusion', 'psybeam', 'tackle'],
        'machamp': ['karate_chop', 'brick_break', 'close_combat', 'body_slam'],
        'dragonite': ['body_slam', 'hyper_beam', 'tackle', 'flamethrower'],
        'gyarados': ['surf', 'hydro_pump', 'body_slam', 'hyper_beam'],
        'snorlax': ['body_slam', 'hyper_beam', 'tackle', 'surf'],
        'lapras': ['surf', 'water_gun', 'hydro_pump', 'body_slam'],
        'articuno': ['surf', 'water_gun', 'tackle', 'body_slam'],
        'zapdos': ['thunderbolt', 'thunder', 'thunder_shock', 'body_slam'],
        'moltres': ['flamethrower', 'fire_blast', 'ember', 'body_slam']
    }
    
    # check if we have custom moves for this pokemon
    if name in special_moves:
        return special_moves[name]
    
    # otherwise try to figure out moves from types
    main_type = types[0] if types else 'normal'
    
    available_moves = []
    
    # Add STAB moves (prioritize powerful ones)
    type_move_priority = {
        'psychic': ['psychic', 'confusion', 'psybeam'],
        'electric': ['thunderbolt', 'thunder', 'thunder_shock'],
        'fire': ['flamethrower', 'fire_blast', 'ember'],
        'water': ['surf', 'hydro_pump', 'water_gun'],
        'grass': ['solar_beam', 'razor_leaf', 'vine_whip'],
        'fighting': ['close_combat', 'brick_break', 'karate_chop'],
        'normal': ['hyper_beam', 'body_slam', 'tackle']
    }
    
    # Add moves for primary type
    if main_type in type_move_priority:
        available_moves.extend(type_move_priority[main_type][:3])
    
    # Add moves for secondary type if exists
    if len(types) > 1:
        secondary_type = types[1]
        if secondary_type in type_move_priority:
            secondary_moves = [move for move in type_move_priority[secondary_type][:2] 
                             if move not in available_moves]
            available_moves.extend(secondary_moves)
    
    # Add coverage move based on stats
    attack = stats.get('attack', 0)
    special_attack = stats.get('special-attack', 0)
    
    if special_attack > attack and len(available_moves) < 4:
        # Special attacker - add special moves
        coverage_moves = ['psychic', 'flamethrower', 'surf', 'thunderbolt']
    else:
        # Physical attacker - add physical moves
        coverage_moves = ['body_slam', 'brick_break', 'hyper_beam', 'tackle']
    
    for move in coverage_moves:
        if move not in available_moves and len(available_moves) < 4:
            available_moves.append(move)
    
    # Ensure we have exactly 4 moves
    while len(available_moves) < 4:
        available_moves.append('tackle')
    
    return available_moves[:4]

def pick_move(poke, opponent_types, moves):
    # simple move selection - not perfect but works
    import random
    
    good_moves = []
    
    for move in moves:
        if move not in moves_db:
            continue
            
        move_info = moves_db[move]
        power = move_info['power']
        move_type = move_info['type']
        
        # check type effectiveness
        effectiveness = get_effectiveness(move_type, opponent_types)
        
        # same type bonus
        poke_types = [t.lower() for t in poke.get('types', [])]
        same_type = move_type in poke_types
        
        # basic scoring
        score = power * effectiveness
        if same_type:
            score *= 1.5  # stab
        
        good_moves.append((move, score))
    
    if not good_moves:
        return 'tackle'  # fallback
    
    # sort and pick - usually best move but sometimes random
    good_moves.sort(key=lambda x: x[1], reverse=True)
    
    if random.random() < 0.8:
        return good_moves[0][0]  # best move
    else:
        return random.choice(good_moves)[0]  # random move

def get_effectiveness(attack_type, def_types):
    # check how effective a move is
    multiplier = 1.0
    for def_type in def_types:
        if attack_type in type_chart:
            multiplier *= type_chart[attack_type].get(def_type.lower(), 1.0)
    return multiplier

def damage_formula(level, power, attack, defense, modifier):
    """Calculate damage using Pokemon damage formula (adjusted for longer battles)"""
    # Original Pokemon damage formula but with reduced damage
    base = ((2*level)/5 + 2) * power * (attack / defense)
    base = base / 50 + 2
    
    # Reduce damage by 60% to make battles much longer
    base = base * 0.4
    
    final_damage = max(1, math.floor(base * modifier))
    
    # Cap maximum damage to prevent one-shots (lowered for longer battles)
    max_damage_cap = 35  # No single move can do more than 35 damage
    return min(final_damage, max_damage_cap)

class BattleSimulator:
    def __init__(self):
        pass  # Remove seed for more realistic battles

    def simulate(self, p1, p2, lv1=50, lv2=50):
        """Enhanced battle simulation with detailed move information"""
        # Initialize Pokemon states with movesets and boosted HP
        # Double HP for much longer, strategic battles
        hp1_boosted = int(p1["stats"]["hp"] * 2.0)
        hp2_boosted = int(p2["stats"]["hp"] * 2.0)
        
        state1 = {
            "pokemon": deepcopy(p1), 
            "hp": hp1_boosted,
            "max_hp": hp1_boosted,
            "level": lv1, 
            "status": None,
            "moves": get_moves(p1)
        }
        state2 = {
            "pokemon": deepcopy(p2), 
            "hp": hp2_boosted,
            "max_hp": hp2_boosted,
            "level": lv2, 
            "status": None,
            "moves": get_moves(p2)
        }
        
        turn = 0
        log = []
        max_turns = 100  # Increased for longer, more strategic battles
        
        while state1["hp"] > 0 and state2["hp"] > 0 and turn < max_turns:
            turn += 1
            
            # Speed check with random factor for variety
            sp1 = p1["stats"]["speed"] * (0.5 if state1["status"]=="paralysis" else 1.0)
            sp2 = p2["stats"]["speed"] * (0.5 if state2["status"]=="paralysis" else 1.0)
            
            # Add some randomness to speed ties
            if abs(sp1 - sp2) <= 5:  # Close speeds
                first, second = (state1, state2) if random.random() < 0.5 else (state2, state1)
            else:
                first, second = (state1, state2) if sp1 > sp2 else (state2, state1)

            # Each Pokemon's turn
            for actor, target in ((first, second), (second, first)):
                if actor["hp"] <= 0 or target["hp"] <= 0:
                    break
                    
                # Status condition checks
                if actor["status"] == "paralysis" and random.random() < 0.25:
                    log.append({
                        "turn": turn, 
                        "actor": actor["pokemon"]["name"], 
                        "action": "paralyzed",
                        "move": "(paralyzed)",
                        "damage": 0,
                        "target_hp": target["hp"],
                        "effectiveness": 1.0,
                        "critical": False
                    })
                    continue
                
                # pick a move
                selected_move = pick_move(
                    actor["pokemon"], 
                    target["pokemon"]["types"], 
                    actor["moves"]
                )
                
                move_data = moves_db.get(selected_move,
                    {"power": 50, "type": "normal", "accuracy": 100, "category": "physical"})
                
                # Accuracy check
                accuracy_roll = random.randint(1, 100)
                if accuracy_roll > move_data["accuracy"]:
                    log.append({
                        "turn": turn,
                        "actor": actor["pokemon"]["name"],
                        "action": "missed",
                        "move": selected_move.replace('_', ' ').title(),
                        "damage": 0,
                        "target_hp": target["hp"],
                        "effectiveness": 1.0,
                        "critical": False
                    })
                    continue
                
                # Handle healing/recovery moves
                if move_data["category"] == "status" and selected_move in ["rest", "recover", "roost"]:
                    # Heal 50% of max HP
                    heal_amount = actor["max_hp"] // 2
                    actor["hp"] = min(actor["max_hp"], actor["hp"] + heal_amount)
                    
                    log.append({
                        "turn": turn,
                        "actor": actor["pokemon"]["name"],
                        "action": "heal",
                        "move": selected_move.replace('_', ' ').title(),
                        "damage": -heal_amount,  # Negative for healing
                        "target_hp": actor["hp"],
                        "effectiveness": 1.0,
                        "critical": False
                    })
                    continue
                
                # Calculate damage
                move_type = move_data["type"]
                power = move_data["power"]
                
                # STAB (Same Type Attack Bonus)
                stab = 1.5 if move_type in [t.lower() for t in actor["pokemon"]["types"]] else 1.0
                
                # Type effectiveness
                effectiveness = get_effectiveness(move_type, target["pokemon"]["types"])
                
                # Critical hit (6.25% chance)
                critical = random.random() < 0.0625
                critical_multiplier = 2.0 if critical else 1.0
                
                # Status effect modifications
                burn_mod = 0.5 if (actor["status"] == "burn" and move_data["category"] == "physical") else 1.0
                
                # Random factor (85-100% for variance)
                random_factor = random.uniform(0.85, 1.0)
                
                # Total damage modifier
                modifier = stab * effectiveness * critical_multiplier * burn_mod * random_factor
                
                # Select attack/defense stats based on move category
                if move_data["category"] == "physical":
                    attack_stat = actor["pokemon"]["stats"]["attack"]
                    defense_stat = target["pokemon"]["stats"]["defense"]
                else:  # special
                    attack_stat = actor["pokemon"]["stats"]["special-attack"]
                    defense_stat = target["pokemon"]["stats"]["special-defense"]
                
                # Calculate final damage
                damage = damage_formula(actor["level"], power, attack_stat, defense_stat, modifier)
                target["hp"] = max(0, target["hp"] - damage)
                
                # Log the move with detailed information
                log.append({
                    "turn": turn,
                    "actor": actor["pokemon"]["name"],
                    "move": selected_move.replace('_', ' ').title(),
                    "move_type": move_type.title(),
                    "power": power,
                    "category": move_data["category"].title(),
                    "damage": damage,
                    "target_hp": target["hp"],
                    "effectiveness": effectiveness,
                    "critical": critical,
                    "stab": stab > 1.0,
                    "action": "attack"
                })
                
                # Check if target fainted
                if target["hp"] <= 0:
                    break
            
            # Apply residual status damage
            for state in [state1, state2]:
                if state["hp"] > 0:
                    residual_damage = 0
                    if state["status"] == "poison":
                        residual_damage = max(1, math.floor(state["pokemon"]["stats"]["hp"] * 0.0625))
                        state["hp"] = max(0, state["hp"] - residual_damage)
                        log.append({
                            "turn": turn,
                            "actor": state["pokemon"]["name"],
                            "action": "poison_damage",
                            "move": "(Poison)",
                            "damage": residual_damage,
                            "target_hp": state["hp"],
                            "effectiveness": 1.0,
                            "critical": False
                        })
                    elif state["status"] == "burn":
                        residual_damage = max(1, math.floor(state["pokemon"]["stats"]["hp"] * 0.0625))
                        state["hp"] = max(0, state["hp"] - residual_damage)
                        log.append({
                            "turn": turn,
                            "actor": state["pokemon"]["name"],
                            "action": "burn_damage",
                            "move": "(Burn)",
                            "damage": residual_damage,
                            "target_hp": state["hp"],
                            "effectiveness": 1.0,
                            "critical": False
                        })
            
            # Check for battle end
            if state1["hp"] <= 0 or state2["hp"] <= 0:
                break

        # Determine winner
        if state1["hp"] > 0 and state2["hp"] <= 0:
            winner = state1["pokemon"]["name"]
        elif state2["hp"] > 0 and state1["hp"] <= 0:
            winner = state2["pokemon"]["name"]
        else:
            winner = "draw" if state1["hp"] == state2["hp"] else (
                state1["pokemon"]["name"] if state1["hp"] > state2["hp"] else state2["pokemon"]["name"]
            )

        return {
            "turns": turn, 
            "winner": winner, 
            "log": log,
            "final_hp": {
                state1["pokemon"]["name"]: state1["hp"],
                state2["pokemon"]["name"]: state2["hp"]
            },
            "movesets": {
                state1["pokemon"]["name"]: [move.replace('_', ' ').title() for move in state1["moves"]],
                state2["pokemon"]["name"]: [move.replace('_', ' ').title() for move in state2["moves"]]
            }
        }
