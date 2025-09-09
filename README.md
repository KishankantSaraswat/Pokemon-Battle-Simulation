# Pokémon Battle MCP Server 🔥⚡🌿

A comprehensive **Model Context Protocol (MCP)** server for Pokémon battle simulation. This server allows LLMs to access Pokémon data and simulate battles through standardized MCP interfaces.

## 🎯 Project Overview

This MCP server enables:
- **Speech-to-Text Integration**: Extract Pokémon names from voice commands
- **RESTful API**: Access Pokémon data and battle simulation
- **LLM Integration**: Battle narration and analysis through standardized MCP protocol
- **Real-time Battle Simulation**: Turn-based combat with type effectiveness

## 🏗️ Architecture

```
User Speech → STT → Pokémon Names → MCP Server → Battle Simulation → LLM → Narrative
```

### Components:
1. **MCP Server** (`server.py`) - Main protocol implementation
2. **Pokémon Resource** (`pokemon_resource.py`) - Data fetching from PokéAPI
3. **Battle Simulator** (`battle_simulator.py`) - Combat mechanics
4. **Frontend Integration** - Visual battle display

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start MCP Server
```bash
python server.py
```
Server runs on `http://localhost:8080`

### 3. Test the Server
```bash
curl http://localhost:8080/mcp/info
```

## 📋 MCP Endpoints

### Server Information
- `GET /mcp/info` - Server capabilities and version
- `GET /` - Status and endpoint overview

### Resources (Data Access)
- `GET /mcp/resources/list` - List available resources
- `POST /mcp/resources/read` - Read specific resource

**Resource URIs:**
- `pokemon://data/{name}` - Get Pokémon data
- `pokemon://battle/{pokemon1}/{pokemon2}` - Battle preview

### Tools (Actions)
- `GET /mcp/tools/list` - List available tools
- `POST /mcp/tools/call` - Execute tool

**Available Tools:**
1. `simulate_battle` - Full battle simulation
2. `get_pokemon` - Pokémon information lookup
3. `compare_pokemon` - Stat comparison

### Prompts (LLM Integration)
- `GET /mcp/prompts/list` - List system prompts
- `POST /mcp/prompts/get` - Get specific prompt

**System Prompts:**
1. `battle_narrator` - Engaging battle commentary
2. `pokemon_expert` - Knowledge and analysis

## 🎮 Usage Examples

### 1. Get Pokémon Data
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_pokemon",
    "arguments": {"name": "pikachu"}
  }'
```

### 2. Simulate Battle
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "simulate_battle",
    "arguments": {
      "pokemon1": {"name": "pikachu", "level": 50},
      "pokemon2": {"name": "bulbasaur", "level": 50}
    }
  }'
```

### 3. Compare Pokémon
```bash
curl -X POST http://localhost:8080/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "compare_pokemon",
    "arguments": {
      "pokemon1": "charizard",
      "pokemon2": "blastoise"
    }
  }'
```

## 🎯 LLM System Prompt

Use this prompt to integrate with your LLM:

```
You are a Pokémon battle simulator and narrator. You have access to detailed Pokémon data and battle simulation tools through MCP.

When a user requests a battle:
1. Use the 'simulate_battle' tool to run the simulation
2. Parse the battle log and create engaging commentary
3. Highlight key moments, type advantages, and critical hits
4. Announce the winner with battle statistics

Available MCP Tools:
- simulate_battle(pokemon1, pokemon2) - Run full battle simulation
- get_pokemon(name) - Get Pokémon details
- compare_pokemon(pokemon1, pokemon2) - Compare stats and matchups

Make battles exciting and informative!
```

## 🔧 Configuration

### MCP Server Config (`mcp_config.json`)
- Server host and port settings
- Capability definitions
- Resource and tool schemas
- System prompt templates

### Battle Mechanics
- Type effectiveness system
- Damage calculation with STAB, critical hits
- Status conditions (burn, poison, paralysis)
- Turn-based combat with speed priority

## 📊 Battle System Features

### ⚔️ Combat Mechanics
- **Damage Formula**: Based on official Pokémon formulas
- **Type Effectiveness**: Super effective, not very effective, no effect
- **STAB Bonus**: Same Type Attack Bonus (1.5x)
- **Critical Hits**: Random critical hit chance
- **Status Effects**: Burn, poison, paralysis

### 📈 Advanced Features
- **Speed Priority**: Faster Pokémon attacks first
- **Random Factors**: Damage variance for realism
- **Battle Logs**: Detailed turn-by-turn recording
- **Winner Determination**: HP-based victory conditions

## 🌐 Integration with Frontend

### Expected Frontend Features:
1. **Voice Input**: Speech recognition for Pokémon names
2. **Visual Display**: Pokémon sprites and animations
3. **Battle Log**: Real-time battle progression
4. **Winner Banner**: Victory announcement
5. **Stats Display**: HP, damage, effectiveness indicators

### API Integration:
```javascript
// Example frontend integration
const simulateBattle = async (pokemon1, pokemon2) => {
  const response = await fetch('http://localhost:8080/mcp/tools/call', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      name: 'simulate_battle',
      arguments: {
        pokemon1: {name: pokemon1, level: 50},
        pokemon2: {name: pokemon2, level: 50}
      }
    })
  });
  return response.json();
};
```

## 🔄 Legacy Compatibility

The server maintains backward compatibility with existing endpoints:
- `/resources/pokemon/<name>` - Direct Pokémon data access
- `/tools/simulate_battle` - Legacy battle simulation

## 🛠️ Development

### Project Structure:
```
Pokemon Simulation/
├── server.py              # Main MCP server
├── pokemon_resource.py    # Pokémon data fetching
├── battle_simulator.py    # Battle mechanics
├── mcp_config.json       # Server configuration
├── requirements.txt      # Dependencies
├── README.md            # This file
├── backend/             # Alternative backend implementation
└── frontend/            # Web interface (if applicable)
```

### Testing:
1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test MCP protocol compliance
3. **Battle Simulation**: Verify combat mechanics
4. **API Endpoints**: Test all REST endpoints

## 📝 TODO / Future Enhancements

- [ ] Expand type effectiveness chart (currently simplified)
- [ ] Add more status conditions and abilities
- [ ] Implement move selection strategies
- [ ] Add Pokémon evolution chains
- [ ] Create battle replay system
- [ ] Add multiplayer battle support
- [ ] Implement tournament brackets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## 📜 License

MIT License - Feel free to use and modify!

---

**Ready to battle!** 🔥⚡🌿 Your MCP server is now equipped to handle Pokémon battles with full LLM integration!
