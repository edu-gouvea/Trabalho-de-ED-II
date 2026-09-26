from models import Pokemon

class Node:
    def __init__(self, key, pokemon: Pokemon):
        self.key = key
        self.pokemon = pokemon
        self.left = None
        self.right = None
        self.parent = None

class SplayTree:
    def __init__(self):
        self.root = None
    
    def insert(self, key, pokemon):
        node = Node(key, pokemon)
        y = None
        x = self.root

        while x is not None:
            y = x
            if node.key < x.key:
                x = x.left
            else:
                x = x.right

        node.parent = y
        if y is None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node

        self.splay(node)

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        y.left = x
        x.parent = y

    def right_rotate(self, x):
        y = x.left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x

        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        y.right = x
        x.parent = y

    def splay(self, n, record_steps=None):
        while n.parent is not None:
            if n.parent.parent is None:
                if n == n.parent.left:
                    if record_steps is not None: record_steps.append({"type": "zig", "node": n.key})
                    self.right_rotate(n.parent)
                else:
                    if record_steps is not None: record_steps.append({"type": "zag", "node": n.key})
                    self.left_rotate(n.parent)
            elif n == n.parent.left and n.parent == n.parent.parent.left:
                if record_steps is not None: record_steps.append({"type": "zig-zig", "node": n.key})
                self.right_rotate(n.parent.parent)
                self.right_rotate(n.parent)
            elif n == n.parent.right and n.parent == n.parent.parent.right:
                if record_steps is not None: record_steps.append({"type": "zag-zag", "node": n.key})
                self.left_rotate(n.parent.parent)
                self.left_rotate(n.parent)
            elif n == n.parent.right and n.parent == n.parent.parent.left:
                if record_steps is not None: record_steps.append({"type": "zag-zig", "node": n.key})
                self.left_rotate(n.parent)
                self.right_rotate(n.parent)
            else:
                if record_steps is not None: record_steps.append({"type": "zig-zag", "node": n.key})
                self.right_rotate(n.parent)
                self.left_rotate(n.parent)

    def search(self, key):
        path = []
        node = self.root
        iterations = 0

        while node is not None:
            iterations += 1
            path.append({"key": node.key, "pokemon_name": node.pokemon.name})
            
            if key == node.key:
                splay_steps = []
                self.splay(node, record_steps=splay_steps)
                
                # Get prev and next
                prev_node = self.predecessor(node)
                next_node = self.successor(node)
                
                return {
                    "found": True,
                    "pokemon": node.pokemon.model_dump(),
                    "path": path,
                    "iterations": iterations,
                    "splay_steps": splay_steps,
                    "prev": prev_node.pokemon.model_dump() if prev_node else None,
                    "next": next_node.pokemon.model_dump() if next_node else None
                }
            elif key < node.key:
                node = node.left
            else:
                node = node.right

        return {"found": False, "path": path, "iterations": iterations}

    def predecessor(self, node):
        if node.left is not None:
            curr = node.left
            while curr.right is not None:
                curr = curr.right
            return curr
        curr = node
        parent = node.parent
        while parent is not None and curr == parent.left:
            curr = parent
            parent = parent.parent
        return parent

    def successor(self, node):
        if node.right is not None:
            curr = node.right
            while curr.left is not None:
                curr = curr.left
            return curr
        curr = node
        parent = node.parent
        while parent is not None and curr == parent.right:
            curr = parent
            parent = parent.parent
        return parent
