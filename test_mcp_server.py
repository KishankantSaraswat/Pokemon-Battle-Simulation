#!/usr/bin/env python3
"""
Test script for Pokemon Battle MCP Server
Demonstrates all MCP functionality including resources, tools, and prompts.
"""

import requests
import json
import time
from typing import Dict, Any

# Server configuration
SERVER_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def make_request(method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
    """Make HTTP request and return JSON response"""
    url = f"{SERVER_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, headers=HEADERS, json=data)
        
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return {"error": str(e)}

def test_server_info():
    """Test server information endpoint"""
    print_section("1. Server Information")
    
    # Test main index
    response = make_request("GET", "/")
    print("📍 Server Status:")
    print(json.dumps(response, indent=2))
    
    # Test MCP info
    response = make_request("GET", "/mcp/info")
    print("\n🔧 MCP Server Info:")
    print(json.dumps(response, indent=2))

def test_resources():
    """Test MCP resources functionality"""
    print_section("2. MCP Resources")
    
    # List resources
    response = make_request("GET", "/mcp/resources/list")
    print("📋 Available Resources:")
    print(json.dumps(response, indent=2))
    
    # Read Pokemon data resource
    print("\n🔍 Reading Pokemon Resource (Pikachu):")
    data = {"uri": "pokemon://data/pikachu"}
    response = make_request("POST", "/mcp/resources/read", data)
    if "contents" in response:
        print("✅ Pokemon data retrieved successfully")
        # Parse and display key info
        pokemon_data = json.loads(response["contents"][0]["text"])
        print(f"Name: {pokemon_data['name']}")
        print(f"Types: {', '.join(pokemon_data['types'])}")
        print(f"HP: {pokemon_data['stats']['hp']}")
        print(f"Attack: {pokemon_data['stats']['attack']}")
    else:
        print("❌ Failed to retrieve Pokemon data")
        print(json.dumps(response, indent=2))
    
    # Read battle preview resource
    print("\n⚔️ Reading Battle Preview Resource:")
    data = {"uri": "pokemon://battle/pikachu/bulbasaur"}
    response = make_request("POST", "/mcp/resources/read", data)
    if "contents" in response:
        print("✅ Battle preview retrieved successfully")
        battle_data = json.loads(response["contents"][0]["text"])
        print(f"Matchup: {battle_data['matchup']}")
        print("Type advantages:")
        for key, advantages in battle_data['type_advantages'].items():
            if advantages:
                print(f"  {key}: {', '.join(advantages)}")
    else:
        print("❌ Failed to retrieve battle preview")

def test_tools():
    """Test MCP tools functionality"""
    print_section("3. MCP Tools")
    
    # List tools
    response = make_request("GET", "/mcp/tools/list")
    print("🛠️ Available Tools:")
    print(json.dumps(response, indent=2))
    
    # Test get_pokemon tool
    print("\n🔍 Testing get_pokemon tool:")
    data = {
        "name": "get_pokemon",
        "arguments": {"name": "charizard"}
    }
    response = make_request("POST", "/mcp/tools/call", data)
    if "content" in response:
        print("✅ get_pokemon tool successful")
        pokemon_info = json.loads(response["content"][0]["text"])
        print(f"Retrieved: {pokemon_info['name']} - Types: {', '.join(pokemon_info['types'])}")
    else:
        print("❌ get_pokemon tool failed")
        print(json.dumps(response, indent=2))
    
    # Test compare_pokemon tool
    print("\n📊 Testing compare_pokemon tool:")
    data = {
        "name": "compare_pokemon",
        "arguments": {
            "pokemon1": "charizard",
            "pokemon2": "blastoise"
        }
    }
    response = make_request("POST", "/mcp/tools/call", data)
    if "content" in response:
        print("✅ compare_pokemon tool successful")
        comparison = json.loads(response["content"][0]["text"])
        print(f"Comparison: {comparison['pokemon1']['name']} vs {comparison['pokemon2']['name']}")
        print("Stat differences:")
        for stat, diff in comparison['stat_comparison'].items():
            print(f"  {stat}: {diff}")
    else:
        print("❌ compare_pokemon tool failed")
    
    # Test simulate_battle tool
    print("\n⚔️ Testing simulate_battle tool:")
    data = {
        "name": "simulate_battle",
        "arguments": {
            "pokemon1": {"name": "pikachu", "level": 50},
            "pokemon2": {"name": "bulbasaur", "level": 50}
        }
    }
    response = make_request("POST", "/mcp/tools/call", data)
    if "content" in response:
        print("✅ simulate_battle tool successful")
        battle_result = json.loads(response["content"][0]["text"])
        print(f"Battle Result: {battle_result['summary']}")
        print(f"Winner: {battle_result['winner']}")
        print(f"Turns: {battle_result['turns']}")
        print("Participants:")
        for key, participant in battle_result['participants'].items():
            print(f"  {participant['name']} (Level {participant['level']}) - Types: {', '.join(participant['types'])}")
    else:
        print("❌ simulate_battle tool failed")
        print(json.dumps(response, indent=2))

def test_prompts():
    """Test MCP prompts functionality"""
    print_section("4. MCP Prompts")
    
    # List prompts
    response = make_request("GET", "/mcp/prompts/list")
    print("💬 Available Prompts:")
    print(json.dumps(response, indent=2))
    
    # Get battle narrator prompt
    print("\n🎭 Battle Narrator Prompt:")
    data = {"name": "battle_narrator"}
    response = make_request("POST", "/mcp/prompts/get", data)
    if "messages" in response:
        print("✅ Battle narrator prompt retrieved")
        prompt_content = response["messages"][0]["content"]["text"]
        print("Prompt preview:")
        print(prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content)
    else:
        print("❌ Failed to retrieve battle narrator prompt")
    
    # Get pokemon expert prompt
    print("\n🔬 Pokemon Expert Prompt:")
    data = {"name": "pokemon_expert"}
    response = make_request("POST", "/mcp/prompts/get", data)
    if "messages" in response:
        print("✅ Pokemon expert prompt retrieved")
        prompt_content = response["messages"][0]["content"]["text"]
        print("Prompt preview:")
        print(prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content)
    else:
        print("❌ Failed to retrieve pokemon expert prompt")

def test_legacy_compatibility():
    """Test legacy endpoint compatibility"""
    print_section("5. Legacy Compatibility")
    
    # Test legacy Pokemon endpoint
    print("🔄 Testing legacy Pokemon endpoint:")
    response = make_request("GET", "/resources/pokemon/squirtle")
    if "name" in response:
        print(f"✅ Legacy endpoint working: {response['name']}")
    else:
        print("❌ Legacy Pokemon endpoint failed")
    
    # Test legacy battle endpoint
    print("\n🔄 Testing legacy battle endpoint:")
    data = {
        "pokemon1": {"name": "squirtle", "level": 45},
        "pokemon2": {"name": "charmander", "level": 45}
    }
    response = make_request("POST", "/tools/simulate_battle", data)
    if "winner" in response:
        print(f"✅ Legacy battle endpoint working: {response['winner']} wins!")
    else:
        print("❌ Legacy battle endpoint failed")

def demo_voice_integration():
    """Demonstrate how voice integration would work"""
    print_section("6. Voice Integration Demo")
    
    # Simulate voice input processing
    voice_commands = [
        "Let's fight between Pikachu and Bulbasaur",
        "Battle Charizard against Blastoise",
        "Show me a fight with Gengar versus Alakazam"
    ]
    
    print("🎤 Simulating voice command processing:")
    
    for i, command in enumerate(voice_commands, 1):
        print(f"\n{i}. Voice Command: '{command}'")
        
        # Simple name extraction (in real implementation, use NLP)
        pokemon_names = []
        common_pokemon = ["pikachu", "bulbasaur", "charizard", "blastoise", "gengar", "alakazam"]
        
        for pokemon in common_pokemon:
            if pokemon.lower() in command.lower():
                pokemon_names.append(pokemon)
        
        if len(pokemon_names) >= 2:
            p1, p2 = pokemon_names[0], pokemon_names[1]
            print(f"   📝 Extracted: {p1.title()} vs {p2.title()}")
            
            # Simulate battle
            battle_data = {
                "name": "simulate_battle",
                "arguments": {
                    "pokemon1": {"name": p1, "level": 50},
                    "pokemon2": {"name": p2, "level": 50}
                }
            }
            
            response = make_request("POST", "/mcp/tools/call", battle_data)
            if "content" in response:
                result = json.loads(response["content"][0]["text"])
                print(f"   🏆 Result: {result['summary']}")
            else:
                print("   ❌ Battle simulation failed")
        else:
            print("   ❌ Could not extract two Pokemon names")

def main():
    """Run all tests"""
    print("🚀 Pokemon Battle MCP Server Test Suite")
    print(f"Testing server at: {SERVER_URL}")
    
    try:
        # Test if server is running
        response = requests.get(SERVER_URL, timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly")
            return
        
        print("✅ Server is running!")
        
        # Run all tests
        test_server_info()
        test_resources()
        test_tools()
        test_prompts()
        test_legacy_compatibility()
        demo_voice_integration()
        
        print_section("Test Summary")
        print("🎉 All tests completed!")
        print("\n📋 Next Steps:")
        print("1. Connect your LLM to the MCP server")
        print("2. Use the battle_narrator system prompt")
        print("3. Integrate with speech-to-text for voice commands")
        print("4. Build frontend with battle animations")
        
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running:")
        print("   python server.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
