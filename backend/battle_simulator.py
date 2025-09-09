import random
from battle_rules import get_battle_rules

def calculate_damage(attacker, defender, move):
    rules = get_battle_rules()
    
    # Base damage calculation
    base_damage = (((2 * attacker['level'] / 5 + 2) * move['power'] * 
                   attacker['stats']['attack'] / defender['stats']['defense']) / 50 + 2)
    
    # STAB (Same Type Attack Bonus)
    stab = rules['battle_mechanics']['stab_bonus'] if move['type'] in attacker['type'].split('/') else 1
    
    # Type effectiveness
    effectiveness = 1
    for def_type in defender['type'].split('/'):
        if move['type'] in rules['type_effectiveness'] and def_type in rules['type_effectiveness'][move['type']]:
            effectiveness *= rules['type_effectiveness'][move['type']][def_type]
    
    # Critical hit
    critical = rules['battle_mechanics']['critical_multiplier'] if random.random() < rules['battle_mechanics']['critical_hit_chance'] else 1
    
    # Random factor (0.85 to 1.00)
    random_factor = random.uniform(0.85, 1.0)
    
    final_damage = int(base_damage * stab * effectiveness * critical * random_factor)
    
    return {
        'damage': final_damage,
        'critical': critical > 1,
        'effectiveness': effectiveness,
        'description': get_damage_description(effectiveness, critical > 1)
    }

def get_damage_description(effectiveness, is_critical):
    description = []
    if is_critical:
        description.append("A critical hit!")
    if effectiveness > 1:
        description.append("It's super effective!")
    elif effectiveness < 1 and effectiveness > 0:
        description.append("It's not very effective...")
    elif effectiveness == 0:
        description.append("It has no effect...")
    return " ".join(description)