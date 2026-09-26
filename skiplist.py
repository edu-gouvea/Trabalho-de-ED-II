import random
from models import Pokemon

class Node:
    def __init__(self, key, pokemon: Pokemon, level):
        self.key = key
        self.pokemon = pokemon
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level, p):
        self.max_level = max_level
        self.p = p
        self.header = self.create_node(self.max_level, -1, None)
        self.level = 0

    def create_node(self, lvl, key, pokemon):
        n = Node(key, pokemon, lvl)
        return n

    def random_level(self):
        lvl = 0
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def insert(self, key, pokemon):
        update = [None] * (self.max_level + 1)
        current = self.header

        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current is None or current.key != key:
            rlevel = self.random_level()

            if rlevel > self.level:
                for i in range(self.level + 1, rlevel + 1):
                    update[i] = self.header
                self.level = rlevel

            n = self.create_node(rlevel, key, pokemon)

            for i in range(rlevel + 1):
                n.forward[i] = update[i].forward[i]
                update[i].forward[i] = n

    def search(self, key):
        current = self.header
        path = []
        update = [None] * (self.max_level + 1)
        iterations = 0

        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                iterations += 1
                path.append({"level": i, "key": current.key, "pokemon_name": current.pokemon.name if current.pokemon else "header", "action": "right"})
                current = current.forward[i]
            
            iterations += 1
            path.append({"level": i, "key": current.key, "pokemon_name": current.pokemon.name if current.pokemon else "header", "action": "down"})
            update[i] = current

        prev_node = current
        current = current.forward[0]
        iterations += 1

        if current and current.key == key:
            next_node = current.forward[0]
            
            return {
                "found": True,
                "pokemon": current.pokemon.model_dump(),
                "path": path,
                "iterations": iterations,
                "prev": prev_node.pokemon.model_dump() if prev_node.pokemon else None,
                "next": next_node.pokemon.model_dump() if next_node and next_node.pokemon else None
            }

        return {"found": False, "path": path, "iterations": iterations}
