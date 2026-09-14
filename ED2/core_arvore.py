import pandas as pd

class TaxaNode:
    """Representa um nó na árvore n-ária taxônomica."""
    def __init__(self, name, rank, parent=None):
        self.name = name
        self.rank = rank        # Ex: 'Order', 'Family', 'Species'
        self.parent = parent    # Referência ao nó pai (facilita o backtracking)
        self.children = {}      # Dicionário O(1) para armazenar os filhos
        
    def get_path_to_root(self):
        """Retorna a linhagem completa do nó atual até a raiz."""
        path = []
        current = self
        while current is not None:
            path.append(f"{current.rank}: {current.name}")
            current = current.parent
        return path[::-1] # Inverte para mostrar da raiz até o nó

class TaxonomyTree:
    """Gerencia a árvore de taxonomia e os índices de busca."""
    def __init__(self):
        # A raiz da nossa árvore
        self.root = TaxaNode("Reptilia", "Class")
        # Tabela Hash para busca de espécies em O(1)
        self.species_index = {}

    def insert_record(self, order_name, family_name, species_name, subspecies_names):
        """Insere uma linha do dataset na estrutura da árvore."""
        
        # 1. Tratamento e inserção da Ordem
        order_name = "Desconhecida" if pd.isna(order_name) else str(order_name).strip()
        if order_name not in self.root.children:
            self.root.children[order_name] = TaxaNode(order_name, "Order", self.root)
        order_node = self.root.children[order_name]

        # 2. Tratamento e inserção da Família
        family_name = "Desconhecida" if pd.isna(family_name) else str(family_name).strip()
        if family_name not in order_node.children:
            order_node.children[family_name] = TaxaNode(family_name, "Family", order_node)
        family_node = order_node.children[family_name]

        # 3. Tratamento e inserção da Espécie
        species_name = str(species_name).strip()
        if species_name not in family_node.children:
            species_node = TaxaNode(species_name, "Species", family_node)
            family_node.children[species_name] = species_node
            # Adiciona ao índice de busca rápida O(1)
            self.species_index[species_name.lower()] = species_node
        else:
            species_node = family_node.children[species_name]

        # 4. Tratamento das Subespécies (pode haver múltiplas por linha, separadas por \n)
        if pd.notna(subspecies_names):
            # O dataset parece ter subespécies separadas por quebra de linha
            for sub in str(subspecies_names).split('\n'):
                sub = sub.strip()
                if sub and sub not in species_node.children:
                    sub_node = TaxaNode(sub, "Subspecies", species_node)
                    species_node.children[sub] = sub_node
                    
    def build_tree_from_csv(self, filepath):
        """Lê o arquivo CSV e popula a estrutura de dados."""
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            self.insert_record(
                row['order'], 
                row['Family'], 
                row['Species'], 
                row['Subspecies']
            )
            
    def search_species(self, name):
        """Busca uma espécie em O(1) usando a Tabela Hash."""
        return self.species_index.get(name.lower())


if __name__ == "__main__":
    print("Construindo a árvore taxônomica...")
    tree = TaxonomyTree()
    # Certifique-se de que o CSV está na mesma pasta
    tree.build_tree_from_csv("reptile_checklist_2026_06.csv")
    
    print(f"Total de espécies indexadas: {len(tree.species_index)}")
    
    # Testando a busca O(1) e o backtracking para achar os pais
    especie_teste = "Ablepharus"
    resultado = tree.search_species(especie_teste)
    
    if resultado:
        print(f"\nEspécie '{especie_teste}' encontrada!")
        print("Caminho taxônomico:")
        for linhagem in resultado.get_path_to_root():
            print(f" -> {linhagem}")
            
        print("\nSubespécies encontradas:")
        for sub in resultado.children.values():
            print(f" - {sub.name}")
    else:
        print("\nEspécie não encontrada.")