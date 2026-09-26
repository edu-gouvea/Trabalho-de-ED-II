import csv
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from models import Pokemon
from skiplist import SkipList
from splaytree import SplayTree

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory="images"), name="images")

skip_list = SkipList(max_level=10, p=0.5)
splay_tree = SplayTree()

def load_data():
    with open('pokemon.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            pokedex_id = i + 1
            name = row.get("Name", "")
            type1 = row.get("Type1", "")
            type2 = row.get("Type2", "") if row.get("Type2") else None
            evolution = row.get("Evolution", "") if row.get("Evolution") else None
            
            # Find image
            img_filename = f"{name.lower()}.png"
            img_path = f"/images/{img_filename}"
            if not os.path.exists(os.path.join("images", img_filename)):
                # If image doesn't exist, we can use a placeholder or None.
                # Assuming the image is formatted properly or handle missing later.
                # Since images have hyphens for forms sometimes, let's keep it simple.
                pass
            
            pokemon = Pokemon(
                id=pokedex_id,
                name=name,
                type1=type1,
                type2=type2,
                evolution=evolution,
                image_url=img_path
            )
            
            skip_list.insert(pokedex_id, pokemon)
            splay_tree.insert(pokedex_id, pokemon)

@app.on_event("startup")
async def startup_event():
    load_data()

@app.get("/search/skiplist/{pokemon_id}")
def search_skiplist(pokemon_id: int):
    result = skip_list.search(pokemon_id)
    if not result["found"]:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return result

@app.get("/search/splaytree/{pokemon_id}")
def search_splaytree(pokemon_id: int):
    result = splay_tree.search(pokemon_id)
    if not result["found"]:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return result

# We also need a route to get a pokemon by name to find its ID easily from the frontend search bar
@app.get("/search/name/{pokemon_name}")
def search_name(pokemon_name: str):
    # Linear search just for the frontend helper
    pokemon_name = pokemon_name.lower()
    with open('pokemon.csv', mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if row.get("Name", "").lower() == pokemon_name:
                return {"id": i + 1}
    raise HTTPException(status_code=404, detail="Pokemon not found")

import random as rand

@app.get("/random")
def get_random_pokemons():
    # Get 5 random pokemons from skiplist (since it's easily traversable or we can just pick random IDs)
    random_ids = rand.sample(range(1, 810), 5) # Assuming 809 pokemon in CSV
    result = []
    for pid in random_ids:
        # Since we just want simple data, we can search in skiplist
        search_res = skip_list.search(pid)
        if search_res["found"]:
            p = search_res["pokemon"]
            result.append({"id": p["id"], "name": p["name"], "image_url": p["image_url"]})
    return result

@app.get("/splaytree/state")
def get_splaytree_state():
    def node_to_dict(node, current_depth, max_depth):
        if node is None:
            return None
        res = {
            "id": node.key,
            "name": node.pokemon.name,
            "image_url": node.pokemon.image_url,
            "left": None,
            "right": None
        }
        if current_depth < max_depth:
            res["left"] = node_to_dict(node.left, current_depth + 1, max_depth)
            res["right"] = node_to_dict(node.right, current_depth + 1, max_depth)
        return res
        
    return node_to_dict(splay_tree.root, 0, 2)
