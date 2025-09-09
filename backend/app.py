from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
from battle_rules import get_battle_rules

app = Flask(__name__)
CORS(app)

POKEMON_API_BASE_URL = "http://127.0.0.1:8080/resources/pokemon"

def get_pokemon_data(name):
    response = requests.get(f"{POKEMON_API_BASE_URL}/{name.lower()}")
    if response.status_code == 200:
        return response.json()
    return None

def calculate_damage(attacker, defender, move):
    rules = get_battle_rules()
    
    base_damage = (((2 * attacker['level'] / 5 + 2) * move['power'] * 
                   attacker['stats']['attack'] / defender['stats']['defense']) / 50 + 2)
    
    stab = rules['battle_mechanics']['stab_bonus'] if move['type'] in attacker['type'].split('/') else 1
    
    effectiveness = 1
    for def_type in defender['type'].split('/'):
        if move['type'] in rules['type_effectiveness'] and def_type in rules['type_effectiveness'][move['type']]:
            effectiveness *= rules['type_effectiveness'][move['type']][def_type]
    
    critical = rules['battle_mechanics']['critical_multiplier'] if random.random() < rules['battle_mechanics']['critical_hit_chance'] else 1
    random_factor = random.uniform(0.85, 1.0)
    
    final_damage = int(base_damage * stab * effectiveness * critical * random_factor)
    
    return {
        'damage': final_damage,
        'critical': critical > 1,
        'effectiveness': effectiveness
    }

@app.route('/simulate-battle')
def simulate_battle():
    poke1 = request.args.get('poke1', '').lower()
    poke2 = request.args.get('poke2', '').lower()
    print(f"Simulating battle between {poke1} and {poke2}")
    
    if not (poke1 and poke2):
        return jsonify({'error': 'Both pokemon names are required'}), 400
    
    pokemon1 = get_pokemon_data(poke1)
    print(f"Pokemon 1 data: {pokemon1}")
    pokemon2 = get_pokemon_data(poke2)
    print(f"Pokemon 2 data: {pokemon2}")
    
    if not (pokemon1 and pokemon2):
        return jsonify({'error': 'One or both Pokemon not found'}), 404
    
    battle_log = []
    hp1 = pokemon1['stats']['hp']
    hp2 = pokemon2['stats']['hp']
    print(f"Initial HP - {pokemon1['name']}: {hp1}, {pokemon2['name']}: {hp2}")
    
    first = pokemon1 if pokemon1['stats']['speed'] >= pokemon2['stats']['speed'] else pokemon2
    second = pokemon2 if first == pokemon1 else pokemon1
    
    max_turns = get_battle_rules()['battle_mechanics']['max_turns']
    turn = 1
    
    while hp1 > 0 and hp2 > 0 and turn <= max_turns:
        # First Pokemon's turn
        move = random.choice(first['moves'])
        damage_result = calculate_damage(first, second, move)
        if first == pokemon1:
            hp2 -= damage_result['damage']
        else:
            hp1 -= damage_result['damage']
        
        battle_log.append({
            'turn': turn,
            'attacker': first['name'],
            'move': move['name'],
            'damage': damage_result['damage'],
            'critical': damage_result['critical'],
            'effectiveness': damage_result['effectiveness']
        })
        
        if hp1 <= 0 or hp2 <= 0:
            break
        
        # Second Pokemon's turn
        move = random.choice(second['moves'])
        damage_result = calculate_damage(second, first, move)
        if second == pokemon1:
            hp2 -= damage_result['damage']
        else:
            hp1 -= damage_result['damage']
        
        battle_log.append({
            'turn': turn,
            'attacker': second['name'],
            'move': move['name'],
            'damage': damage_result['damage'],
            'critical': damage_result['critical'],
            'effectiveness': damage_result['effectiveness']
        })
        
        turn += 1
    
    winner = pokemon1['name'] if hp1 > hp2 else pokemon2['name']
    if hp1 == hp2:
        winner = "Draw"
    
    return jsonify({
        'winner': winner,
        'battle_log': battle_log,
        'final_state': {
            f"{pokemon1['name']}_hp": max(0, hp1),
            f"{pokemon2['name']}_hp": max(0, hp2)
        }
    })

@app.route('/')
def home():
    return jsonify({
        'name': 'Pokemon Battle Simulation API',
        'version': '1.0',
        'endpoints': {
            'Get Pokemon': '/pokemon/<name>',
            'Battle': '/battle?poke1=<name>&poke2=<name>',
            'Simulate Battle': '/simulate-battle?poke1=<name>&poke2=<name>'
        },
        'status': 'online'
    })

@app.route('/pokemon/<name>')
def get_pokemon(name):
    pokemon = get_pokemon_data(name)
    if pokemon:
        return jsonify(pokemon)
    return jsonify({'error': 'Pokemon not found'}), 404

@app.route('/battle')
def get_battle_data():
    poke1 = request.args.get('poke1', '').lower()
    poke2 = request.args.get('poke2', '').lower()
    
    if not (poke1 and poke2):
        return jsonify({'error': 'Both pokemon names are required'}), 400
    
    pokemon1 = get_pokemon_data(poke1)
    pokemon2 = get_pokemon_data(poke2)
    
    if not (pokemon1 and pokemon2):
        return jsonify({'error': 'One or both Pokemon not found'}), 404
    
    return jsonify({
        'pokemon1': pokemon1,
        'pokemon2': pokemon2
    })

if __name__ == '__main__':
    app.run(debug=True)