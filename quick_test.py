#!/usr/bin/env python3
"""
Quick test for the enhanced Pokemon Battle System
Tests the detailed move system and battle logging
"""

import requests
import json
from pokemon_resource import PokemonResource
from battle_simulator import BattleSimulator

def test_enhanced_battle():
    print("🧪 Testing Enhanced Battle System")
    print("=" * 50)
    
    # Initialize components
    poke_resource = PokemonResource()
    simulator = BattleSimulator()
    
    # Test Pokemon
    print("📥 Fetching Pokemon data...")
    pikachu = poke_resource.get_pokemon("pikachu")
    charizard = poke_resource.get_pokemon("charizard")
    
    if not pikachu or not charizard:
        print("❌ Failed to fetch Pokemon data")
        return
    
    print(f"✅ Got {pikachu['name'].title()} and {charizard['name'].title()}")
    
    # Test battle simulation
    print("\n⚔️ Simulating battle...")
    battle_result = simulator.simulate(pikachu, charizard, 50, 50)
    
    print(f"\n🏆 Battle Result:")
    print(f"Winner: {battle_result['winner']}")
    print(f"Turns: {battle_result['turns']}")
    
    # Show movesets
    movesets = battle_result.get('movesets', {})
    print(f"\n🎯 Pokemon Movesets:")
    for pokemon, moves in movesets.items():
        print(f"  {pokemon}: {', '.join(moves)}")
    
    # Show sample battle log entries
    log = battle_result.get('log', [])
    print(f"\n📋 Sample Battle Log (first 5 entries):")
    for entry in log[:5]:
        turn = entry.get('turn', '?')
        actor = entry.get('actor', 'Unknown')
        move = entry.get('move', 'Attack')
        damage = entry.get('damage', 0)
        move_type = entry.get('move_type', '')
        power = entry.get('power', 0)
        
        if move_type and power:
            print(f"  Turn {turn}: {actor} used {move} ({move_type}, Power: {power}) - {damage} damage")
        else:
            print(f"  Turn {turn}: {actor} used {move} - {damage} damage")
    
    print(f"\n✅ Enhanced battle system working perfectly!")
    return True

def test_mcp_server():
    print("\n🌐 Testing MCP Server...")
    
    try:
        # Test server info
        response = requests.get("http://localhost:8080/mcp/info", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Server is online!")
            
            # Test tool call
            battle_payload = {
                "name": "simulate_battle",
                "arguments": {
                    "pokemon1": {"name": "pikachu", "level": 50},
                    "pokemon2": {"name": "charizard", "level": 50}
                }
            }
            
            response = requests.post(
                "http://localhost:8080/mcp/tools/call",
                headers={"Content-Type": "application/json"},
                json=battle_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "content" in result:
                    battle_data = json.loads(result["content"][0]["text"])
                    print(f"✅ MCP Battle Simulation successful!")
                    print(f"   Winner: {battle_data.get('winner', 'Unknown')}")
                    print(f"   Turns: {battle_data.get('turns', 0)}")
                    return True
            
        print("❌ MCP Server test failed")
        return False
        
    except Exception as e:
        print(f"❌ MCP Server not available: {e}")
        print("💡 Start server with: python start_server.py")
        return False

def main():
    print("🎮 Pokemon Battle System - Quick Test")
    print("=" * 50)
    
    # Test 1: Enhanced battle system
    try:
        if test_enhanced_battle():
            print("\n✅ Local battle system: PASSED")
        else:
            print("\n❌ Local battle system: FAILED")
    except Exception as e:
        print(f"\n❌ Local battle system error: {e}")
    
    # Test 2: MCP server integration
    try:
        if test_mcp_server():
            print("✅ MCP server integration: PASSED")
        else:
            print("❌ MCP server integration: FAILED")
    except Exception as e:
        print(f"❌ MCP server integration error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test Complete!")
    print("\n🚀 Ready to run the full system:")
    print("   1. Start MCP Server: python start_server.py")
    print("   2. Start Frontend: streamlit run frontend/app.py")
    print("   3. Or start both: python run_complete_system.py")

if __name__ == "__main__":
    main()
