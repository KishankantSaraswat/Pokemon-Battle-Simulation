import streamlit as st
import requests
import json
import time
import re
import random
from PIL import Image
from io import BytesIO

# voice stuff - might not work on all systems
try:
    import speech_recognition as sr
    import pydub
    import pyttsx3
    voice_works = True
except ImportError:
    voice_works = False
    st.warning("Voice not available - install speech libs if you want it")

VOICE_AVAILABLE = voice_works

st.set_page_config(
    page_title="Pokemon Battle Thing",
    page_icon="⚔️",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# server config
server_url = "http://localhost:8080"
backend_url = "http://127.0.0.1:5000"  # backup
json_headers = {"Content-Type": "application/json"}

# pokemon names - got this list online somewhere
pokemon_list = [
    # gen 1 stuff
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise", "caterpie", "metapod", "butterfree",
    "weedle", "kakuna", "beedrill", "pidgey", "pidgeotto", "pidgeot",
    "rattata", "raticate", "spearow", "fearow", "ekans", "arbok",
    "pikachu", "raichu", "sandshrew", "sandslash", "nidoran-f", "nidorina",
    "nidoqueen", "nidoran-m", "nidorino", "nidoking", "clefairy", "clefable",
    "vulpix", "ninetales", "jigglypuff", "wigglytuff", "zubat", "golbat",
    "oddish", "gloom", "vileplume", "paras", "parasect", "venonat",
    "venomoth", "diglett", "dugtrio", "meowth", "persian", "psyduck",
    "golduck", "mankey", "primeape", "growlithe", "arcanine", "poliwag",
    "poliwhirl", "poliwrath", "abra", "kadabra", "alakazam", "machop",
    "machoke", "machamp", "bellsprout", "weepinbell", "victreebel", "tentacool",
    "tentacruel", "geodude", "graveler", "golem", "ponyta", "rapidash",
    "slowpoke", "slowbro", "magnemite", "magneton", "farfetchd", "doduo",
    "dodrio", "seel", "dewgong", "grimer", "muk", "shellder",
    "cloyster", "gastly", "haunter", "gengar", "onix", "drowzee",
    "hypno", "krabby", "kingler", "voltorb", "electrode", "exeggcute",
    "exeggutor", "cubone", "marowak", "hitmonlee", "hitmonchan", "lickitung",
    "koffing", "weezing", "rhyhorn", "rhydon", "chansey", "tangela",
    "kangaskhan", "horsea", "seadra", "goldeen", "seaking", "staryu",
    "starmie", "mr-mime", "scyther", "jynx", "electabuzz", "magmar",
    "pinsir", "tauros", "magikarp", "gyarados", "lapras", "ditto",
    "eevee", "vaporeon", "jolteon", "flareon", "porygon", "omanyte",
    "omastar", "kabuto", "kabutops", "aerodactyl", "snorlax", "articuno",
    "zapdos", "moltres", "dratini", "dragonair", "dragonite", "mewtwo", "mew",
    
    # Generation 2 (Johto) - Popular ones
    "chikorita", "bayleef", "meganium", "cyndaquil", "quilava", "typhlosion",
    "totodile", "croconaw", "feraligatr", "crobat", "lanturn", "togetic",
    "ampharos", "umbreon", "espeon", "slowking", "forretress", "steelix",
    "scizor", "heracross", "corsola", "skarmory", "kingdra", "donphan",
    "porygon2", "tyrogue", "hitmontop", "smoochum", "elekid", "magby",
    "miltank", "blissey", "raikou", "entei", "suicune", "larvitar",
    "pupitar", "tyranitar", "lugia", "ho-oh", "celebi",
    
    # Generation 3 (Hoenn) - Popular ones  
    "treecko", "grovyle", "sceptile", "torchic", "combusken", "blaziken",
    "mudkip", "marshtomp", "swampert", "gardevoir", "slaking", "aggron",
    "meditite", "medicham", "manectric", "plusle", "minun", "flygon",
    "altaria", "lunatone", "solrock", "whiscash", "crawdaunt", "claydol",
    "cradily", "armaldo", "milotic", "absol", "salamence", "metagross",
    "regirock", "regice", "registeel", "latios", "latias", "kyogre",
    "groudon", "rayquaza", "jirachi", "deoxys"
]

# Popular Pokemon for quick suggestions
POPULAR_POKEMON = [
    "pikachu", "charizard", "blastoise", "venusaur", "mewtwo", "mew",
    "gengar", "alakazam", "machamp", "dragonite", "snorlax", "lapras",
    "gyarados", "eevee", "lucario", "garchomp", "rayquaza", "metagross",
    "salamence", "tyranitar", "lugia", "ho-oh", "kyogre", "groudon"
]

# Voice Recognition Functions
def extract_pokemon_names(text):
    # find pokemon names in text
    text = text.lower()
    found = []
    
    for name in pokemon_list:
        if name.lower() in text:
            found.append(name)
    
    return found

def listen_for_voice():
    # voice recognition - basic error handling
    if not voice_works:
        return None, "No voice support"
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... say pokemon names")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
        
        text = r.recognize_google(audio)
        pokemon_names = extract_pokemon_names(text)
        return pokemon_names, text
    except:
        # just catch everything - dont care about specific errors
        return None, "Didnt work"

# MCP Server Functions
def call_server(tool, args):
    # call the mcp server - simple version
    data = {"name": tool, "arguments": args}
    
    try:
        resp = requests.post(f"{server_url}/mcp/tools/call", headers=json_headers, json=data, timeout=10)
        return resp.json()
    except:
        return {"error": "server call failed"}

def call_mcp_tool(tool_name, args):
    return call_server(tool_name, args)

def get_pokemon_data(name):
    # get pokemon info from server
    response = call_server("get_pokemon", {"name": name})
    
    if "content" in response:
        try:
            return json.loads(response["content"][0]["text"])
        except:
            pass
    
        # try backup server
    try:
        resp = requests.get(f"{backend_url}/pokemon/{name.lower()}")
        if resp.status_code == 200:
            return resp.json()
    except:
        pass  # oh well
    
    return None

def search_pokemon(query, pokemon_list):
    """Search Pokemon by name with fuzzy matching"""
    if not query:
        return pokemon_list[:20]  # Return first 20 if no query
    
    query = query.lower()
    matches = []
    
    # Exact matches first
    for pokemon in pokemon_list:
        if pokemon.lower() == query:
            matches.append(pokemon)
    
    # Starts with query
    for pokemon in pokemon_list:
        if pokemon.lower().startswith(query) and pokemon not in matches:
            matches.append(pokemon)
    
    # Contains query
    for pokemon in pokemon_list:
        if query in pokemon.lower() and pokemon not in matches:
            matches.append(pokemon)
    
    return matches[:15]  # Limit to 15 results

def get_pokemon_preview(pokemon_name):
    """Get a quick preview of Pokemon stats"""
    if not pokemon_name:
        return None
    
    try:
        pokemon_data = get_pokemon_data(pokemon_name)
        if pokemon_data:
            return {
                'name': pokemon_data['name'].title(),
                'types': pokemon_data.get('types', []),
                'hp': pokemon_data.get('stats', {}).get('hp', 0),
                'attack': pokemon_data.get('stats', {}).get('attack', 0),
                'id': pokemon_data.get('id', 0)
            }
    except:
        pass
    return None

def get_battle_narrative(battle_result):
    """Generate battle narrative using simulated LLM (replace with real LLM integration)"""
    winner = battle_result.get('winner', 'Unknown')
    turns = battle_result.get('turns', 0)
    participants = battle_result.get('participants', {})
    
    narratives = [
        f"🔥 **EPIC BATTLE REPORT** 🔥",
        f"In an intense {turns}-turn battle between {participants.get('pokemon1', {}).get('name', 'Fighter 1')} and {participants.get('pokemon2', {}).get('name', 'Fighter 2')}...",
        f"🏆 **{winner.upper()}** emerges victorious!",
        f"What an incredible display of Pokemon prowess!"
    ]
    
    return "\n".join(narratives)

def get_pokemon_image(pokemon_data):
    """Get Pokemon image from sprites"""
    try:
        if 'sprites' in pokemon_data:
            # Try different sprite sources
            sprite_urls = [
                pokemon_data['sprites'].get('other', {}).get('official-artwork', {}).get('front_default'),
                pokemon_data['sprites'].get('front_default'),
                pokemon_data['sprites'].get('other', {}).get('dream_world', {}).get('front_default'),
                pokemon_data['sprites'].get('other', {}).get('home', {}).get('front_default')
            ]
            
            for url in sprite_urls:
                if url:
                    try:
                        response = requests.get(url, timeout=5)
                        if response.status_code == 200:
                            return Image.open(BytesIO(response.content))
                    except:
                        continue
        return None
    except:
        return None

def simulate_battle_mcp(poke1, poke2, level1=50, level2=50):
    """Simulate battle using MCP server"""
    arguments = {
        "pokemon1": {"name": poke1, "level": level1},
        "pokemon2": {"name": poke2, "level": level2}
    }
    
    response = call_mcp_tool("simulate_battle", arguments)
    
    if "content" in response:
        try:
            return json.loads(response["content"][0]["text"])
        except Exception as e:
            st.error(f"MCP response parsing error: {e}")
            return None
    
    if "error" in response:
        st.error(f"MCP Error: {response['error']}")
    
    return None

def simulate_battle_legacy(poke1, poke2):
    """Fallback to legacy backend battle simulation"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/simulate-battle",
            params={'poke1': poke1, 'poke2': poke2},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Legacy battle simulation error: {str(e)}")
        return None

def simulate_battle(poke1, poke2, level1=50, level2=50):
    """Main battle simulation function with MCP and fallback"""
    # Try MCP server first
    result = simulate_battle_mcp(poke1, poke2, level1, level2)
    
    if result:
        return result
    
    # Fallback to legacy backend
    st.warning("MCP server unavailable, using legacy backend...")
    return simulate_battle_legacy(poke1, poke2)

# App Header
st.title("🎤 Voice-Enabled Pokémon Battle Simulator")
st.subheader("⚔️ Powered by MCP Server & AI Narration")

# Sidebar for controls and settings
st.sidebar.title("🎮 Battle Controls")

# Voice input section
st.sidebar.subheader("🎤 Voice Commands")
if VOICE_AVAILABLE:
    if st.sidebar.button("🎤 Listen for Battle Command", type="primary"):
        with st.spinner("Listening for your command..."):
            pokemon_names, voice_text = listen_for_voice_command()
            
            if pokemon_names and len(pokemon_names) >= 2:
                st.session_state.pokemon1_name = pokemon_names[0]
                st.session_state.pokemon2_name = pokemon_names[1]
                st.sidebar.success(f"📢 Heard: '{voice_text}'")
                st.sidebar.info(f"Extracted: {pokemon_names[0].title()} vs {pokemon_names[1].title()}")
            elif pokemon_names:
                st.sidebar.warning(f"Only found: {', '.join(pokemon_names)}. Need 2 Pokemon for battle!")
            else:
                st.sidebar.error(f"Voice recognition issue: {voice_text}")
else:
    st.sidebar.warning("⚠️ Voice features disabled. Install speech packages.")

# Pokemon Selection Section
st.sidebar.subheader("🔍 Pokemon Selection")

# Tab for different selection methods
selection_method = st.sidebar.radio(
    "Selection Method:",
    ["🔤 Search & Select", "⌨️ Manual Input", "🎯 Popular Pokemon"],
    index=0
)

if selection_method == "🔤 Search & Select":
    # Pokemon 1 Search
    st.sidebar.write("**First Pokemon:**")
    search_query_1 = st.sidebar.text_input(
        "Search Pokemon 1:", 
        placeholder="Type to search... (e.g., pika, char, gen)",
        key="search_1"
    )
    
    if search_query_1:
        search_results_1 = search_pokemon(search_query_1, POKEMON_NAMES)
        if search_results_1:
            selected_pokemon_1 = st.sidebar.selectbox(
                "Choose Pokemon 1:",
                search_results_1,
                format_func=lambda x: x.replace('-', ' ').title(),
                key="select_1"
            )
            if selected_pokemon_1:
                st.session_state.pokemon1_name = selected_pokemon_1
                
                # Show preview
                preview_1 = get_pokemon_preview(selected_pokemon_1)
                if preview_1:
                    st.sidebar.success(f"✅ Selected: {preview_1['name']}")
                    st.sidebar.caption(f"Types: {', '.join(preview_1['types'])} | HP: {preview_1['hp']}")
        else:
            st.sidebar.warning("No Pokemon found matching your search.")
    
    st.sidebar.write("---")
    
    # Pokemon 2 Search
    st.sidebar.write("**Second Pokemon:**")
    search_query_2 = st.sidebar.text_input(
        "Search Pokemon 2:", 
        placeholder="Type to search... (e.g., blas, venu, drago)",
        key="search_2"
    )
    
    if search_query_2:
        search_results_2 = search_pokemon(search_query_2, POKEMON_NAMES)
        if search_results_2:
            selected_pokemon_2 = st.sidebar.selectbox(
                "Choose Pokemon 2:",
                search_results_2,
                format_func=lambda x: x.replace('-', ' ').title(),
                key="select_2"
            )
            if selected_pokemon_2:
                st.session_state.pokemon2_name = selected_pokemon_2
                
                # Show preview
                preview_2 = get_pokemon_preview(selected_pokemon_2)
                if preview_2:
                    st.sidebar.success(f"✅ Selected: {preview_2['name']}")
                    st.sidebar.caption(f"Types: {', '.join(preview_2['types'])} | HP: {preview_2['hp']}")
        else:
            st.sidebar.warning("No Pokemon found matching your search.")
            
    pokemon1_name = st.session_state.get('pokemon1_name', '')
    pokemon2_name = st.session_state.get('pokemon2_name', '')

elif selection_method == "⌨️ Manual Input":
    # Traditional manual input
    pokemon1_name = st.sidebar.text_input(
        "First Pokémon", 
        value=st.session_state.get('pokemon1_name', ''),
        placeholder="e.g., pikachu, charizard",
        key="manual_pokemon1"
    )
    pokemon2_name = st.sidebar.text_input(
        "Second Pokémon", 
        value=st.session_state.get('pokemon2_name', ''),
        placeholder="e.g., blastoise, gengar",
        key="manual_pokemon2"
    )
    
    # Update session state
    if pokemon1_name:
        st.session_state.pokemon1_name = pokemon1_name
    if pokemon2_name:
        st.session_state.pokemon2_name = pokemon2_name

elif selection_method == "🎯 Popular Pokemon":
    # Popular Pokemon selection
    st.sidebar.write("**Choose from Popular Pokemon:**")
    
    # Split popular Pokemon into two columns
    pop_col1, pop_col2 = st.sidebar.columns(2)
    
    with pop_col1:
        st.write("**Pokemon 1:**")
        for i, pokemon in enumerate(POPULAR_POKEMON[:12]):
            if st.button(pokemon.title(), key=f"pop1_{i}", use_container_width=True):
                st.session_state.pokemon1_name = pokemon
                st.rerun()
    
    with pop_col2:
        st.write("**Pokemon 2:**")
        for i, pokemon in enumerate(POPULAR_POKEMON[:12]):
            if st.button(pokemon.title(), key=f"pop2_{i}", use_container_width=True):
                st.session_state.pokemon2_name = pokemon
                st.rerun()
    
    pokemon1_name = st.session_state.get('pokemon1_name', '')
    pokemon2_name = st.session_state.get('pokemon2_name', '')

# Current Selection Display
if st.session_state.get('pokemon1_name') or st.session_state.get('pokemon2_name'):
    st.sidebar.subheader("🎯 Current Selection")
    
    if st.session_state.get('pokemon1_name'):
        st.sidebar.success(f"🔴 Pokemon 1: {st.session_state.pokemon1_name.title()}")
    else:
        st.sidebar.error("🔴 Pokemon 1: Not selected")
    
    if st.session_state.get('pokemon2_name'):
        st.sidebar.success(f"🔵 Pokemon 2: {st.session_state.pokemon2_name.title()}")
    else:
        st.sidebar.error("🔵 Pokemon 2: Not selected")
    
    # Clear selection button
    if st.sidebar.button("🗋 Clear Selection", use_container_width=True):
        st.session_state.pokemon1_name = ''
        st.session_state.pokemon2_name = ''
        st.rerun()

# Battle settings
st.sidebar.subheader("⚙️ Battle Settings")
level1 = st.sidebar.slider("Pokémon 1 Level", 1, 100, 50)
level2 = st.sidebar.slider("Pokémon 2 Level", 1, 100, 50)
auto_narration = st.sidebar.checkbox("🤖 AI Battle Narration", True)

# Update session state
if pokemon1_name:
    st.session_state.pokemon1_name = pokemon1_name
if pokemon2_name:
    st.session_state.pokemon2_name = pokemon2_name

# Main battle interface
col1, col2, col3 = st.columns([1, 0.2, 1])

# Pokemon 1 Display
with col1:
    if st.session_state.get('pokemon1_name'):
        pokemon1_data = get_pokemon_data(st.session_state.pokemon1_name)
        if pokemon1_data:
            st.subheader(f"🔴 {pokemon1_data['name'].title()}")
            
            # Pokemon image
            image = get_pokemon_image(pokemon1_data)
            if image:
                st.image(image, width=250)
            
            # Stats display
            stats = pokemon1_data.get('stats', {})
            st.write(f"**Types:** {', '.join(pokemon1_data.get('types', []))}")
            
            # Stats in columns
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("HP", stats.get('hp', 0))
                st.metric("Attack", stats.get('attack', 0))
                st.metric("Defense", stats.get('defense', 0))
            with stat_col2:
                st.metric("Speed", stats.get('speed', 0))
                st.metric("Sp. Attack", stats.get('special-attack', 0))
                st.metric("Sp. Defense", stats.get('special-defense', 0))
        else:
            st.error(f"Could not find Pokémon: {st.session_state.pokemon1_name}")
    else:
        st.info("🔍 Select your first Pokémon")

# VS Section
with col2:
    st.markdown("<h1 style='text-align: center; color: red;'>VS</h1>", unsafe_allow_html=True)
    if st.button("⚔️ START BATTLE!", type="primary", use_container_width=True):
        st.session_state.battle_initiated = True

# Pokemon 2 Display
with col3:
    if st.session_state.get('pokemon2_name'):
        pokemon2_data = get_pokemon_data(st.session_state.pokemon2_name)
        if pokemon2_data:
            st.subheader(f"🔵 {pokemon2_data['name'].title()}")
            
            # Pokemon image
            image = get_pokemon_image(pokemon2_data)
            if image:
                st.image(image, width=250)
            
            # Stats display
            stats = pokemon2_data.get('stats', {})
            st.write(f"**Types:** {', '.join(pokemon2_data.get('types', []))}")
            
            # Stats in columns
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.metric("HP", stats.get('hp', 0))
                st.metric("Attack", stats.get('attack', 0))
                st.metric("Defense", stats.get('defense', 0))
            with stat_col2:
                st.metric("Speed", stats.get('speed', 0))
                st.metric("Sp. Attack", stats.get('special-attack', 0))
                st.metric("Sp. Defense", stats.get('special-defense', 0))
        else:
            st.error(f"Could not find Pokémon: {st.session_state.pokemon2_name}")
    else:
        st.info("🔍 Select your second Pokémon")

# Battle Results Section
if st.session_state.get('battle_initiated'):
    p1_name = st.session_state.get('pokemon1_name')
    p2_name = st.session_state.get('pokemon2_name')
    
    if not (p1_name and p2_name):
        st.error("⚠️ Please select both Pokémon before starting battle!")
        st.session_state.battle_initiated = False
    else:
        st.divider()
        st.header("⚔️ **BATTLE IN PROGRESS** ⚔️")
        
        with st.spinner(f"Simulating epic battle between {p1_name.title()} and {p2_name.title()}..."):
            battle_result = simulate_battle(p1_name, p2_name, level1, level2)
            
            if battle_result:
                # Winner announcement
                winner = battle_result.get('winner', 'Unknown')
                if winner.lower() != 'draw':
                    st.success(f"🏆 **VICTORY!** {winner.upper()} WINS!")
                else:
                    st.info("🤝 **DRAW!** Both Pokémon fought valiantly!")
                
                # Battle summary in columns
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.metric(
                        label="📊 Battle Duration",
                        value=f"{battle_result.get('turns', 0)} Turns"
                    )
                
                with result_col2:
                    participants = battle_result.get('participants', {})
                    p1_info = participants.get('pokemon1', {})
                    p2_info = participants.get('pokemon2', {})
                    st.metric(
                        label="⚔️ Combatants",
                        value=f"Level {p1_info.get('level', '?')} vs Level {p2_info.get('level', '?')}"
                    )
                
                with result_col3:
                    battle_log = battle_result.get('log', [])
                    critical_hits = sum(1 for entry in battle_log if entry.get('damage', 0) > 0)
                    st.metric(
                        label="✨ Total Attacks",
                        value=f"{critical_hits} Moves"
                    )
                
                # AI Battle Narration
                if auto_narration:
                    st.subheader("🤖 AI Battle Commentary")
                    with st.container():
                        narrative = get_battle_narrative(battle_result)
                        st.markdown(narrative)
                        
                        # Add some battle highlights
                        log = battle_result.get('log', [])
                        if log:
                            high_damage_attacks = [entry for entry in log if entry.get('damage', 0) > 50]
                            if high_damage_attacks:
                                st.info(f"💥 **Most Powerful Attack:** {max(high_damage_attacks, key=lambda x: x.get('damage', 0)).get('damage', 0)} damage!")
                
                # Enhanced Battle Log with Move Details
                with st.expander("📄 View Detailed Battle Log", expanded=False):
                    if battle_log:
                        # Display movesets first
                        movesets = battle_result.get('movesets', {})
                        if movesets:
                            st.subheader("🎯 Pokemon Movesets")
                            moveset_col1, moveset_col2 = st.columns(2)
                            
                            poke_names = list(movesets.keys())
                            if len(poke_names) >= 2:
                                with moveset_col1:
                                    st.write(f"**{poke_names[0]}:**")
                                    for move in movesets[poke_names[0]]:
                                        st.write(f"• {move}")
                                
                                with moveset_col2:
                                    st.write(f"**{poke_names[1]}:**")
                                    for move in movesets[poke_names[1]]:
                                        st.write(f"• {move}")
                            st.divider()
                        
                        # Battle log entries
                        st.subheader("⚔️ Turn-by-Turn Battle Log")
                        for i, entry in enumerate(battle_log):
                            turn = entry.get('turn', i+1)
                            actor = entry.get('actor', 'Unknown')
                            move = entry.get('move', 'Attack')
                            damage = entry.get('damage', 0)
                            target_hp = entry.get('target_hp', 0)
                            action = entry.get('action', 'attack')
                            
                            # Special actions (paralyzed, missed, etc.)
                            if action == 'paralyzed':
                                st.info(f"🐌 **Turn {turn}:** {actor} is paralyzed and can't move!")
                                continue
                            elif action == 'missed':
                                st.warning(f"🎯 **Turn {turn}:** {actor}'s {move} missed!")
                                continue
                            elif 'poison' in action:
                                st.error(f"🐍 **Turn {turn}:** {actor} takes {damage} poison damage! (HP: {target_hp})")
                                continue
                            elif 'burn' in action:
                                st.error(f"🔥 **Turn {turn}:** {actor} takes {damage} burn damage! (HP: {target_hp})")
                                continue
                            elif action == 'heal':
                                heal_amount = abs(damage)  # Damage is negative for healing
                                st.success(f"💖 **Turn {turn}:** {actor} used {move} and restored {heal_amount} HP! (HP: {target_hp})")
                                continue
                            
                            # Regular attack moves
                            move_type = entry.get('move_type', '')
                            power = entry.get('power', 0)
                            category = entry.get('category', 'Physical')
                            effectiveness = entry.get('effectiveness', 1.0)
                            critical = entry.get('critical', False)
                            stab = entry.get('stab', False)
                            
                            # Build move description
                            move_desc = f"**{move}**"
                            if move_type:
                                move_desc += f" ({move_type}-type, {category})"
                            if power > 0:
                                move_desc += f" [Power: {power}]"
                            
                            # Build damage description with modifiers
                            damage_desc = f"{damage} damage"
                            modifiers = []
                            
                            if critical:
                                modifiers.append("✨ Critical Hit!")
                            if stab:
                                modifiers.append("💪 STAB")
                            if effectiveness > 1:
                                modifiers.append("⚡ Super Effective!")
                            elif effectiveness < 1 and effectiveness > 0:
                                modifiers.append("🛡️ Not Very Effective...")
                            elif effectiveness == 0:
                                modifiers.append("🚫 No Effect!")
                            
                            if modifiers:
                                damage_desc += f" ({', '.join(modifiers)})"
                            
                            # Color code based on damage and effectiveness
                            if damage > 60 or critical:
                                st.error(f"💥 **Turn {turn}:** {actor} used {move_desc} - {damage_desc} (Target HP: {target_hp})")
                            elif damage > 30 or effectiveness > 1:
                                st.warning(f"⚡ **Turn {turn}:** {actor} used {move_desc} - {damage_desc} (Target HP: {target_hp})")
                            elif damage == 0:
                                st.info(f"🚫 **Turn {turn}:** {actor} used {move_desc} - No damage! (Target HP: {target_hp})")
                            else:
                                st.info(f"💫 **Turn {turn}:** {actor} used {move_desc} - {damage_desc} (Target HP: {target_hp})")
                    else:
                        st.write("No detailed battle log available")
                
                # Reset battle state
                if st.button("🔄 Battle Again!", type="secondary"):
                    st.session_state.battle_initiated = False
                    st.rerun()
                    
            else:
                st.error("😱 Battle simulation failed! Please check MCP server and try again.")
                st.session_state.battle_initiated = False

# Enhanced Quick Battle Suggestions
if not st.session_state.get('battle_initiated'):
    st.divider()
    st.subheader("🎯 Quick Battle Arena")
    
    # Battle categories
    battle_tabs = st.tabs(["🔥 Legendary", "⚡ Classic", "🎆 Starter", "🔮 Random"])
    
    with battle_tabs[0]:  # Legendary battles
        st.write("**Epic Legendary Showdowns:**")
        legendary_battles = [
            ("Mewtwo", "Mew"),
            ("Lugia", "Ho-oh"),
            ("Kyogre", "Groudon"),
            ("Rayquaza", "Deoxys"),
            ("Dialga", "Palkia"),
            ("Arceus", "Giratina")
        ]
        
        leg_col1, leg_col2, leg_col3 = st.columns(3)
        for i, (p1, p2) in enumerate(legendary_battles[:6]):
            col = [leg_col1, leg_col2, leg_col3][i % 3]
            with col:
                if st.button(f"🔥 {p1} vs {p2}", key=f"leg_{i}", use_container_width=True):
                    st.session_state.pokemon1_name = p1.lower()
                    st.session_state.pokemon2_name = p2.lower()
                    st.rerun()
    
    with battle_tabs[1]:  # Classic battles
        st.write("**Classic Pokemon Rivalries:**")
        classic_battles = [
            ("Pikachu", "Charizard"),
            ("Gengar", "Alakazam"),
            ("Machamp", "Golem"),
            ("Dragonite", "Gyarados"),
            ("Snorlax", "Lapras"),
            ("Scyther", "Pinsir")
        ]
        
        cls_col1, cls_col2, cls_col3 = st.columns(3)
        for i, (p1, p2) in enumerate(classic_battles[:6]):
            col = [cls_col1, cls_col2, cls_col3][i % 3]
            with col:
                if st.button(f"⚡ {p1} vs {p2}", key=f"cls_{i}", use_container_width=True):
                    st.session_state.pokemon1_name = p1.lower()
                    st.session_state.pokemon2_name = p2.lower()
                    st.rerun()
    
    with battle_tabs[2]:  # Starter battles
        st.write("**Starter Pokemon Battles:**")
        starter_battles = [
            ("Charizard", "Blastoise"),
            ("Blastoise", "Venusaur"),
            ("Venusaur", "Charizard"),
            ("Typhlosion", "Feraligatr"),
            ("Feraligatr", "Meganium"),
            ("Meganium", "Typhlosion")
        ]
        
        str_col1, str_col2, str_col3 = st.columns(3)
        for i, (p1, p2) in enumerate(starter_battles[:6]):
            col = [str_col1, str_col2, str_col3][i % 3]
            with col:
                if st.button(f"🎆 {p1} vs {p2}", key=f"str_{i}", use_container_width=True):
                    st.session_state.pokemon1_name = p1.lower()
                    st.session_state.pokemon2_name = p2.lower()
                    st.rerun()
    
    with battle_tabs[3]:  # Random battles
        st.write("**Generate Random Battle:**")
        if st.button("🔮 Generate Random Battle", type="secondary", use_container_width=True):
            import random
            random_pokemon = random.sample(POPULAR_POKEMON, 2)
            st.session_state.pokemon1_name = random_pokemon[0]
            st.session_state.pokemon2_name = random_pokemon[1]
            st.success(f"Random Battle: {random_pokemon[0].title()} vs {random_pokemon[1].title()}!")
            st.rerun()
        
        st.info("🎲 Click to get a surprise battle matchup!")

# Server Status Check
st.sidebar.divider()
st.sidebar.subheader("📊 Server Status")

try:
    mcp_response = requests.get(f"{MCP_SERVER_URL}/mcp/info", timeout=3)
    if mcp_response.status_code == 200:
        st.sidebar.success("✅ MCP Server Online")
        server_info = mcp_response.json()
        st.sidebar.caption(f"Version: {server_info.get('version', 'Unknown')}")
    else:
        st.sidebar.error("❌ MCP Server Error")
except:
    st.sidebar.error("❌ MCP Server Offline")
    st.sidebar.caption("Start with: python start_server.py")

# About Section
st.sidebar.divider()
st.sidebar.title("📝 About")
st.sidebar.info("""
**🎤 Voice-Enabled Pokémon Battle Simulator**

🎆 **Features:**
- 🎤 Voice command recognition
- ⚔️ Real-time battle simulation  
- 🤖 AI-powered battle narration
- 📊 Advanced battle analytics
- 🎮 Interactive battle interface

🚀 **Powered by:**
- MCP (Model Context Protocol) Server
- PokéAPI for real-time data
- Advanced battle mechanics
- Streamlit web interface

**Usage:**
1. Use voice commands or manual input
2. Select two Pokémon for battle
3. Adjust levels and settings
4. Start epic battles!
""")

# Pokemon Search Tips
st.sidebar.subheader("💡 Search Tips")
st.sidebar.info("""
**Search Examples:**
• **Partial names:** "pika" → Pikachu
• **Types:** "char" → Charizard, Charmander
• **Generations:** "mew" → Mewtwo, Mew
• **Evolution:** "drago" → Dragonite

**Available Generations:**
• Gen 1: Kanto (1-151)
• Gen 2: Johto (Popular ones)
• Gen 3: Hoenn (Popular ones)
""")

# Voice Instructions
if VOICE_AVAILABLE:
    st.sidebar.subheader("🎤 Voice Commands")
    st.sidebar.info("""
    **Try saying:**
    - "Battle Pikachu against Charizard"
    - "Let's fight Gengar vs Alakazam"
    - "Show me Snorlax vs Machamp"
    - "Epic battle Dragonite versus Mewtwo"
    """)

# Debug Info
with st.sidebar.expander("🔧 Debug Info", expanded=False):
    st.write("**Session State:**")
    st.json({
        "pokemon1_name": st.session_state.get('pokemon1_name', 'None'),
        "pokemon2_name": st.session_state.get('pokemon2_name', 'None'),
        "battle_initiated": st.session_state.get('battle_initiated', False),
        "voice_available": VOICE_AVAILABLE
    })
    
    st.write("**Server URLs:**")
    st.code(f"MCP Server: {server_url}")
    st.code(f"Backend: {backend_url}")
