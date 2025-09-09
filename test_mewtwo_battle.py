#!/usr/bin/env python3
"""
Test Mewtwo vs Mew battle to verify improved movesets
"""

from pokemon_resource import PokemonResource
from battle_simulator import BattleSimulator

def test_mewtwo_vs_mew():
    print("🧪 Testing Mewtwo vs Mew Battle")
    print("=" * 40)
    
    # Initialize components
    poke_resource = PokemonResource()
    simulator = BattleSimulator()
    
    # Get Pokemon data
    print("📥 Fetching legendary Pokemon...")
    mewtwo = poke_resource.get_pokemon("mewtwo")
    mew = poke_resource.get_pokemon("mew")
    
    if not mewtwo or not mew:
        print("❌ Failed to fetch Pokemon data")
        return
    
    print(f"✅ Got {mewtwo['name'].title()} and {mew['name'].title()}")
    
    # Show stats comparison
    print(f"\n📊 Stats Comparison:")
    print(f"{'Stat':<15} {'Mewtwo':<10} {'Mew':<10}")
    print("-" * 35)
    for stat in ['hp', 'attack', 'defense', 'speed', 'special-attack', 'special-defense']:
        mewtwo_stat = mewtwo['stats'].get(stat, 0)
        mew_stat = mew['stats'].get(stat, 0)
        print(f"{stat.title():<15} {mewtwo_stat:<10} {mew_stat:<10}")
    
    # Simulate multiple battles to see move variety
    print(f"\n⚔️ Simulating 3 battles to test move variety...")
    
    for battle_num in range(1, 4):
        print(f"\n🔥 Battle #{battle_num}:")
        battle_result = simulator.simulate(mewtwo, mew, 50, 50)
        
        winner = battle_result.get('winner', 'Unknown')
        turns = battle_result.get('turns', 0)
        
        print(f"🏆 Winner: {winner.title()} in {turns} turns")
        
        # Show movesets
        movesets = battle_result.get('movesets', {})
        for pokemon, moves in movesets.items():
            print(f"   {pokemon.title()} moves: {', '.join(moves)}")
        
        # Show first few moves used
        log = battle_result.get('log', [])
        print(f"   Moves used:")
        for entry in log[:4]:  # First 4 moves
            if entry.get('action') == 'attack':
                actor = entry.get('actor', 'Unknown')
                move = entry.get('move', 'Attack')
                move_type = entry.get('move_type', '')
                power = entry.get('power', 0)
                damage = entry.get('damage', 0)
                
                print(f"     {actor} used {move} ({move_type}, Power: {power}) - {damage} damage")

def main():
    print("🎮 Mewtwo vs Mew - Enhanced Move Test")
    print("=" * 50)
    
    test_mewtwo_vs_mew()
    
    print(f"\n🎯 Expected Improvements:")
    print(f"✅ Mewtwo should use: Psychic, Psybeam, Confusion, Hyper Beam")
    print(f"✅ Mew should use: Psychic, Confusion, Psybeam, Body Slam") 
    print(f"✅ Both should prioritize Psychic-type moves (STAB)")
    print(f"✅ No more Body Slam spam!")
    
    print(f"\n🚀 Ready for frontend testing:")
    print(f"   1. Start: python run_complete_system.py")
    print(f"   2. Try: Mewtwo vs Mew battle")
    print(f"   3. Check battle log for proper moves")

if __name__ == "__main__":
    main()
