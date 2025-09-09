from flask import Flask, jsonify, request
from flask_cors import CORS
from pokemon_resource import PokemonResource
from battle_simulator import BattleSimulator
from datetime import datetime
import json
from typing import Dict, List, Any, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

poke_resource = PokemonResource()
sim = BattleSimulator()

# MCP Protocol Implementation

@app.route("/mcp/info", methods=["GET"])
def mcp_info():
    """MCP Server Information"""
    return jsonify({
        "name": "Pokemon Battle MCP Server",
        "version": "1.0.0",
        "description": "A Model Context Protocol server for Pokemon battle simulation",
        "author": "Pokemon Battle Simulator",
        "license": "MIT",
        "homepage": "http://localhost:8080",
        "protocol_version": "2024-11-05",
        "capabilities": {
            "resources": True,
            "tools": True,
            "prompts": True
        }
    })

@app.route("/mcp/resources/list", methods=["GET"])
def list_resources():
    """List all available resources"""
    return jsonify({
        "resources": [
            {
                "uri": "pokemon://data/{name}",
                "name": "Pokemon Data",
                "description": "Get detailed information about any Pokemon including stats, types, abilities, and moves",
                "mimeType": "application/json"
            },
            {
                "uri": "pokemon://battle/{pokemon1}/{pokemon2}",
                "name": "Battle Preview",
                "description": "Get battle matchup information between two Pokemon",
                "mimeType": "application/json"
            }
        ]
    })

@app.route("/mcp/resources/read", methods=["POST"])
def read_resource():
    """Read a specific resource"""
    data = request.get_json()
    uri = data.get("uri", "")
    
    if uri.startswith("pokemon://data/"):
        pokemon_name = uri.replace("pokemon://data/", "")
        pokemon_data = poke_resource.get_pokemon(pokemon_name)
        if not pokemon_data:
            return jsonify({"error": f"Pokemon '{pokemon_name}' not found"}), 404
        
        return jsonify({
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(pokemon_data, indent=2)
                }
            ]
        })
    
    elif uri.startswith("pokemon://battle/"):
        parts = uri.replace("pokemon://battle/", "").split("/")
        if len(parts) != 2:
            return jsonify({"error": "Invalid battle URI format"}), 400
        
        pokemon1, pokemon2 = parts
        p1_data = poke_resource.get_pokemon(pokemon1)
        p2_data = poke_resource.get_pokemon(pokemon2)
        
        if not p1_data or not p2_data:
            return jsonify({"error": "One or both Pokemon not found"}), 404
        
        battle_preview = {
            "matchup": f"{pokemon1.title()} vs {pokemon2.title()}",
            "pokemon1": p1_data,
            "pokemon2": p2_data,
            "type_advantages": analyze_type_advantages(p1_data, p2_data)
        }
        
        return jsonify({
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(battle_preview, indent=2)
                }
            ]
        })
    
    return jsonify({"error": "Resource not found"}), 404

@app.route("/mcp/tools/list", methods=["GET"])
def list_tools():
    """List all available tools"""
    return jsonify({
        "tools": [
            {
                "name": "simulate_battle",
                "description": "Simulate a battle between two Pokemon and return detailed battle log with winner",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pokemon1": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the first Pokemon"},
                                "level": {"type": "integer", "default": 50, "minimum": 1, "maximum": 100}
                            },
                            "required": ["name"]
                        },
                        "pokemon2": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "Name of the second Pokemon"},
                                "level": {"type": "integer", "default": 50, "minimum": 1, "maximum": 100}
                            },
                            "required": ["name"]
                        }
                    },
                    "required": ["pokemon1", "pokemon2"]
                }
            },
            {
                "name": "get_pokemon",
                "description": "Get detailed information about a specific Pokemon",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Name of the Pokemon"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "compare_pokemon",
                "description": "Compare stats and matchup between two Pokemon without simulating a battle",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pokemon1": {"type": "string", "description": "Name of the first Pokemon"},
                        "pokemon2": {"type": "string", "description": "Name of the second Pokemon"}
                    },
                    "required": ["pokemon1", "pokemon2"]
                }
            }
        ]
    })

@app.route("/mcp/tools/call", methods=["POST"])
def call_tool():
    """Call a specific tool"""
    data = request.get_json()
    tool_name = data.get("name")
    arguments = data.get("arguments", {})
    
    if tool_name == "simulate_battle":
        p1 = arguments.get("pokemon1")
        p2 = arguments.get("pokemon2")
        
        if not p1 or not p2:
            return jsonify({"error": "Both pokemon1 and pokemon2 are required"}), 400
        
        # Fetch full pokemon data
        full1 = poke_resource.get_pokemon(p1["name"])
        full2 = poke_resource.get_pokemon(p2["name"])
        
        if not full1 or not full2:
            return jsonify({"error": "One or both Pokemon not found"}), 404
        
        # Simulate battle
        battle_result = sim.simulate(full1, full2, p1.get("level", 50), p2.get("level", 50))
        
        # Enhanced battle result with summary
        enhanced_result = {
            **battle_result,
            "summary": f"{battle_result['winner']} wins after {battle_result['turns']} turns!",
            "participants": {
                "pokemon1": {"name": full1["name"], "types": full1["types"], "level": p1.get("level", 50)},
                "pokemon2": {"name": full2["name"], "types": full2["types"], "level": p2.get("level", 50)}
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(enhanced_result, indent=2)
                }
            ]
        })
    
    elif tool_name == "get_pokemon":
        pokemon_name = arguments.get("name")
        if not pokemon_name:
            return jsonify({"error": "Pokemon name is required"}), 400
        
        pokemon_data = poke_resource.get_pokemon(pokemon_name)
        if not pokemon_data:
            return jsonify({"error": f"Pokemon '{pokemon_name}' not found"}), 404
        
        return jsonify({
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(pokemon_data, indent=2)
                }
            ]
        })
    
    elif tool_name == "compare_pokemon":
        pokemon1 = arguments.get("pokemon1")
        pokemon2 = arguments.get("pokemon2")
        
        if not pokemon1 or not pokemon2:
            return jsonify({"error": "Both pokemon1 and pokemon2 names are required"}), 400
        
        p1_data = poke_resource.get_pokemon(pokemon1)
        p2_data = poke_resource.get_pokemon(pokemon2)
        
        if not p1_data or not p2_data:
            return jsonify({"error": "One or both Pokemon not found"}), 404
        
        comparison = {
            "pokemon1": {
                "name": p1_data["name"],
                "types": p1_data["types"],
                "stats": p1_data["stats"]
            },
            "pokemon2": {
                "name": p2_data["name"],
                "types": p2_data["types"],
                "stats": p2_data["stats"]
            },
            "stat_comparison": compare_stats(p1_data["stats"], p2_data["stats"]),
            "type_advantages": analyze_type_advantages(p1_data, p2_data)
        }
        
        return jsonify({
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(comparison, indent=2)
                }
            ]
        })
    
    return jsonify({"error": f"Unknown tool: {tool_name}"}), 400

@app.route("/mcp/prompts/list", methods=["GET"])
def list_prompts():
    """List available prompt templates"""
    return jsonify({
        "prompts": [
            {
                "name": "battle_narrator",
                "description": "System prompt for Pokemon battle narration",
                "arguments": []
            },
            {
                "name": "pokemon_expert",
                "description": "System prompt for Pokemon knowledge expert",
                "arguments": []
            }
        ]
    })

@app.route("/mcp/prompts/get", methods=["POST"])
def get_prompt():
    """Get a specific prompt template"""
    data = request.get_json()
    prompt_name = data.get("name")
    
    prompts = {
        "battle_narrator": {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": """You are a Pokemon battle simulator and narrator. You have access to detailed Pokemon data and battle simulation tools.

When a user asks for a battle between Pokemon:
1. Use the 'simulate_battle' tool to run the battle simulation
2. Parse the battle log and create an engaging narrative
3. Highlight key moments like critical hits, type advantages, and the final outcome
4. Present the winner clearly with battle statistics

Always provide:
- Winner announcement
- Battle summary with key highlights
- Turn count and significant moments
- Type effectiveness impacts

Make the battle exciting and engaging for the user!"""
                    }
                }
            ]
        },
        "pokemon_expert": {
            "messages": [
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": """You are a Pokemon expert with access to comprehensive Pokemon data through MCP tools.

You can:
- Get detailed information about any Pokemon using the 'get_pokemon' tool
- Compare Pokemon stats and matchups using the 'compare_pokemon' tool
- Simulate battles between Pokemon using the 'simulate_battle' tool

Provide accurate, detailed information about Pokemon including their stats, types, abilities, moves, and battle potential. When comparing Pokemon, consider type advantages, stat distributions, and strategic implications."""
                    }
                }
            ]
        }
    }
    
    if prompt_name in prompts:
        return jsonify(prompts[prompt_name])
    
    return jsonify({"error": f"Prompt '{prompt_name}' not found"}), 404

# Legacy endpoints for backward compatibility
@app.route("/resources/pokemon/<name>", methods=["GET"])
def get_pokemon_legacy(name):
    """Legacy endpoint for Pokemon data"""
    data = poke_resource.get_pokemon(name)
    if not data:
        return jsonify({"error": "not found"}), 404
    return jsonify(data)

@app.route("/tools/simulate_battle", methods=["POST"])
def simulate_battle_legacy():
    """Legacy endpoint for battle simulation"""
    payload = request.json or {}
    p1 = payload.get("pokemon1")
    p2 = payload.get("pokemon2")
    
    if not p1 or not p2:
        return jsonify({"error": "pokemon1 and pokemon2 required"}), 400

    full1 = poke_resource.get_pokemon(p1["name"])
    full2 = poke_resource.get_pokemon(p2["name"])
    
    if not full1 or not full2:
        return jsonify({"error": "one or both pokemon not found"}), 404

    log = sim.simulate(full1, full2, p1.get("level", 50), p2.get("level", 50))
    return jsonify(log)

# Helper functions
def analyze_type_advantages(p1_data: Dict, p2_data: Dict) -> Dict:
    """Analyze type advantages between two Pokemon"""
    from battle_simulator import TYPE_CHART
    
    p1_advantages = []
    p2_advantages = []
    
    for p1_type in p1_data["types"]:
        for p2_type in p2_data["types"]:
            if p1_type in TYPE_CHART and p2_type in TYPE_CHART[p1_type]:
                effectiveness = TYPE_CHART[p1_type][p2_type]
                if effectiveness > 1:
                    p1_advantages.append(f"{p1_type} is super effective against {p2_type}")
                elif effectiveness < 1:
                    p1_advantages.append(f"{p1_type} is not very effective against {p2_type}")
    
    for p2_type in p2_data["types"]:
        for p1_type in p1_data["types"]:
            if p2_type in TYPE_CHART and p1_type in TYPE_CHART[p2_type]:
                effectiveness = TYPE_CHART[p2_type][p1_type]
                if effectiveness > 1:
                    p2_advantages.append(f"{p2_type} is super effective against {p1_type}")
                elif effectiveness < 1:
                    p2_advantages.append(f"{p2_type} is not very effective against {p1_type}")
    
    return {
        f"{p1_data['name']}_advantages": p1_advantages,
        f"{p2_data['name']}_advantages": p2_advantages
    }

def compare_stats(stats1: Dict, stats2: Dict) -> Dict:
    """Compare stats between two Pokemon"""
    comparison = {}
    for stat in stats1:
        if stat in stats2:
            diff = stats1[stat] - stats2[stat]
            if diff > 0:
                comparison[stat] = f"Pokemon 1 +{diff}"
            elif diff < 0:
                comparison[stat] = f"Pokemon 2 +{abs(diff)}"
            else:
                comparison[stat] = "Tied"
    return comparison

@app.route("/")
def index():
    """MCP Server status and information"""
    return jsonify({
        "name": "Pokemon Battle MCP Server",
        "version": "1.0.0",
        "status": "running",
        "mcp_endpoints": {
            "info": "/mcp/info",
            "resources": "/mcp/resources/list",
            "tools": "/mcp/tools/list",
            "prompts": "/mcp/prompts/list"
        },
        "legacy_endpoints": {
            "pokemon_data": "/resources/pokemon/<name>",
            "battle_simulation": "/tools/simulate_battle"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
