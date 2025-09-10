import requests
from cachetools import TTLCache

# pokeapi stuff
API_URL = "https://pokeapi.co/api/v2"
cache = TTLCache(maxsize=1000, ttl=3600)  # cache for 1 hour

class PokemonResource:
    def _get_data(self, url):
        # simple fetch function
        try:
            resp = requests.get(f"{API_URL}/{url}")
            return resp.json() if resp.status_code == 200 else None
        except:
            return None  # if api is down or something

    def get_pokemon(self, name):
        key = str(name).lower()
        # check cache first
        if key in cache:
            return cache[key]

        # get pokemon data
        poke = self._get_data(f"pokemon/{key}")
        if not poke:
            return None

        species_data = self._get_data(f"pokemon-species/{poke['id']}")
        # make a simple object with what we need
        result = {
            "id": poke["id"],
            "name": poke["name"],
            "types": [t["type"]["name"] for t in poke["types"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]},
            "abilities": [a["ability"]["name"] for a in poke["abilities"]],
            "moves": [m["move"]["name"] for m in poke["moves"]], # all the moves
            "sprites": poke["sprites"],
            "species": species_data and species_data.get("evolution_chain")
        }
        cache[key] = result
        return result
