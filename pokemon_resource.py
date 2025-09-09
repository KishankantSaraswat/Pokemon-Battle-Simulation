import requests
from cachetools import TTLCache

POKEAPI_BASE = "https://pokeapi.co/api/v2"
cache = TTLCache(maxsize=1000, ttl=3600)

class PokemonResource:
    def _fetch(self, path):
        r = requests.get(f"{POKEAPI_BASE}/{path}")
        return r.json() if r.status_code == 200 else None

    def get_pokemon(self, name_or_id):
        key = str(name_or_id).lower()
        if key in cache:
            return cache[key]

        # fetch pokemon
        p = self._fetch(f"pokemon/{key}")
        if not p:
            return None

        species = self._fetch(f"pokemon-species/{p['id']}")
        # Build simple normalized object
        obj = {
            "id": p["id"],
            "name": p["name"],
            "types": [t["type"]["name"] for t in p["types"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in p["stats"]},
            "abilities": [a["ability"]["name"] for a in p["abilities"]],
            "moves": [m["move"]["name"] for m in p["moves"]],
            "sprites": p["sprites"],
            "species": species and species.get("evolution_chain")
        }
        cache[key] = obj
        return obj
