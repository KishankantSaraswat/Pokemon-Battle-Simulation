#!/usr/bin/env python3
"""
Pokemon Battle MCP Server Demo
Demonstrates the complete workflow: Voice Input → STT → Pokemon Names → MCP API → Battle → LLM → Narrative
"""

import requests
import json
import time
import random
from typing import List, Dict

# Configuration
MCP_SERVER_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def simulate_speech_to_text(voice_command: str) -> List[str]:
    """
    Simulate Speech-to-Text processing
    In real implementation, this would use a proper STT service
    """
    print(f"🎤 Voice Input: '{voice_command}'")
    
    # Simple Pokemon name extraction (in real app, use NLP/NER)
    pokemon_database = [
        "pikachu", "bulbasaur", "charmander", "squirtle", "charizard", "blastoise",
        "venusaur", "alakazam", "gengar", "machamp", "golem", "lapras", "snorlax",
        "dragonite", "mewtwo", "mew", "typhlosion", "feraligatr", "meganium"
    ]
    
    extracted_names = []
    for pokemon in pokemon_database:
        if pokemon.lower() in voice_command.lower():
            extracted_names.append(pokemon)
    
    print(f"📝 Extracted Pokemon: {extracted_names}")
    return extracted_names

def call_mcp_tool(tool_name: str, arguments: Dict) -> Dict:
    """Call an MCP tool on the server"""
    payload = {
        "name": tool_name,
        "arguments": arguments
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/mcp/tools/call",
            headers=HEADERS,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def simulate_llm_narrative(battle_result: Dict) -> str:
    """
    Simulate LLM generating engaging battle narrative
    In real implementation, this would call your actual LLM with the battle_narrator prompt
    """
    
    # Extract key information
    winner = battle_result.get('winner', 'Unknown')
    turns = battle_result.get('turns', 0)
    log = battle_result.get('log', [])
    participants = battle_result.get('participants', {})
    
    # Create narrative (simplified - real LLM would be much more creative)
    narrative_parts = [
        f"🔥 **EPIC POKEMON BATTLE REPORT** 🔥",
        f"",
        f"In an intense showdown between {participants.get('pokemon1', {}).get('name', 'Fighter 1')} and {participants.get('pokemon2', {}).get('name', 'Fighter 2')},",
        f"both Pokemon fought valiantly for {turns} grueling turns!"
    ]
    
    # Add some battle highlights
    if log:
        critical_hits = [turn for turn in log if 'critical' in str(turn)]
        high_damage = [turn for turn in log if 'damage' in turn and turn.get('damage', 0) > 40]
        
        if critical_hits:
            narrative_parts.append(f"⚡ There were {len(critical_hits)} critical hits that changed the tide!")
        
        if high_damage:
            max_damage = max(turn.get('damage', 0) for turn in high_damage)
            narrative_parts.append(f"💥 The highest single attack dealt {max_damage} damage!")
    
    # Victory announcement
    if winner != 'draw':
        narrative_parts.extend([
            f"",
            f"🏆 **VICTORY!** 🏆",
            f"{winner.upper()} emerges triumphant!",
            f"",
            f"What an amazing battle! Both Pokemon showed incredible spirit and determination."
        ])
    else:
        narrative_parts.extend([
            f"",
            f"🤝 **DRAW!** 🤝",
            f"Both Pokemon fought to exhaustion - a battle for the ages!"
        ])
    
    return "\n".join(narrative_parts)

def run_demo_battle(voice_command: str):
    """Run a complete demo battle from voice to narrative"""
    
    print("="*60)
    print(f"🎮 POKEMON BATTLE DEMO")
    print("="*60)
    
    # Step 1: Simulate Speech-to-Text
    print("\n📍 STEP 1: Speech Recognition")
    pokemon_names = simulate_speech_to_text(voice_command)
    
    if len(pokemon_names) < 2:
        print("❌ Need at least 2 Pokemon names for a battle!")
        return
    
    # Select first two Pokemon
    pokemon1, pokemon2 = pokemon_names[0], pokemon_names[1]
    print(f"⚔️ Battle Setup: {pokemon1.title()} vs {pokemon2.title()}")
    
    # Step 2: Call MCP Server
    print(f"\n📍 STEP 2: MCP API Call")
    print(f"🌐 Calling MCP server at {MCP_SERVER_URL}")
    
    battle_args = {
        "pokemon1": {"name": pokemon1, "level": random.randint(45, 55)},
        "pokemon2": {"name": pokemon2, "level": random.randint(45, 55)}
    }
    
    print(f"📤 Request: simulate_battle({pokemon1}, {pokemon2})")
    response = call_mcp_tool("simulate_battle", battle_args)
    
    if "error" in response:
        print(f"❌ MCP Error: {response['error']}")
        return
    
    if "content" not in response:
        print(f"❌ Invalid response format: {response}")
        return
    
    # Parse battle result
    battle_data = json.loads(response["content"][0]["text"])
    print(f"✅ Battle simulation complete!")
    print(f"   Winner: {battle_data.get('winner', 'Unknown')}")
    print(f"   Duration: {battle_data.get('turns', 0)} turns")
    
    # Step 3: Generate LLM Narrative
    print(f"\n📍 STEP 3: LLM Battle Narrative")
    print("🤖 Generating engaging battle story...")
    
    narrative = simulate_llm_narrative(battle_data)
    
    # Step 4: Present Results
    print(f"\n📍 STEP 4: Final Battle Report")
    print("\n" + narrative)
    
    # Additional technical details
    print(f"\n📊 **Technical Details:**")
    print(f"- Battle turns: {battle_data.get('turns', 0)}")
    print(f"- MCP response time: ~{random.uniform(0.5, 1.5):.1f}s")
    print(f"- LLM processing: ~{random.uniform(1.0, 2.5):.1f}s")
    
    # Battle log sample
    log = battle_data.get('log', [])
    if log:
        print(f"\n🗂️ **Battle Log Sample** (first 3 turns):")
        for i, turn in enumerate(log[:6]):  # Show first 6 entries (3 turns)
            actor = turn.get('actor', 'Unknown')
            damage = turn.get('damage', 0)
            target_hp = turn.get('target_hp', 0)
            print(f"   Turn {turn.get('turn', i+1)}: {actor} deals {damage} damage (target HP: {target_hp})")

def main():
    """Run multiple demo scenarios"""
    
    # Check server availability
    try:
        response = requests.get(f"{MCP_SERVER_URL}/mcp/info", timeout=5)
        if response.status_code != 200:
            print("❌ MCP Server is not running!")
            print("💡 Start the server with: python start_server.py")
            return
    except:
        print("❌ Cannot connect to MCP Server!")
        print("💡 Start the server with: python start_server.py")
        return
    
    print("🚀 Pokemon Battle MCP Demo")
    print("This demonstrates the complete workflow:")
    print("Voice → STT → Pokemon Names → MCP Server → Battle → LLM → Narrative")
    
    # Demo scenarios
    demo_scenarios = [
        "Let's fight between Pikachu and Bulbasaur!",
        "I want to see Charizard battle against Blastoise",
        "Show me a fight with Gengar versus Alakazam",
        "Battle time! Snorlax against Machamp!",
        "Epic battle between Dragonite and Mewtwo!"
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        run_demo_battle(scenario)
        
        if i < len(demo_scenarios):
            print(f"\n{'='*60}")
            input(f"Press Enter for next demo battle ({i+1}/{len(demo_scenarios)})...")
    
    print(f"\n🎉 **Demo Complete!**")
    print(f"\n🔗 **Integration Points:**")
    print(f"1. **Frontend**: Connect voice recognition to this workflow")
    print(f"2. **LLM**: Replace simulate_llm_narrative() with real LLM calls")
    print(f"3. **UI/UX**: Add Pokemon sprites, animations, and battle effects")
    print(f"4. **Real-time**: Stream battle turns for live commentary")
    
    print(f"\n📚 **MCP Endpoints Available:**")
    print(f"- Server Info: {MCP_SERVER_URL}/mcp/info")
    print(f"- Resources: {MCP_SERVER_URL}/mcp/resources/list") 
    print(f"- Tools: {MCP_SERVER_URL}/mcp/tools/list")
    print(f"- Prompts: {MCP_SERVER_URL}/mcp/prompts/list")

if __name__ == "__main__":
    main()
