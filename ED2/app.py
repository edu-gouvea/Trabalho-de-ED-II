import streamlit as st
# Importa a classe TaxonomyTree do arquivo que criamos anteriormente
from core_arvore import TaxonomyTree 

# 1. Configuração inicial da página
st.set_page_config(page_title="Estrutura de Dados: Répteis", page_icon="🦎", layout="centered")

# 2. Gerenciamento de Estado (MUITO IMPORTANTE)
# O decorador @st.cache_resource impede que o Streamlit leia o CSV e monte 
# a árvore inteira de novo toda vez que o usuário clicar em um botão.
@st.cache_resource
def load_data():
    tree = TaxonomyTree()
    tree.build_tree_from_csv("reptile_checklist_2026_06.csv")
    return tree

# Carrega os dados
with st.spinner("Estruturando dados na árvore..."):
    tree = load_data()

st.title("🦎 Explorador Taxonômico")
st.markdown("**Trabalho de Estrutura de Dados** - Navegação utilizando Árvore N-ária e Tabela Hash.")

st.divider()

# ==========================================
# SEÇÃO 1: Busca O(1) usando a Tabela Hash
# ==========================================
st.header("🔍 Busca Rápida por Espécie")
st.write("Utiliza a tabela hash para encontrar nós em tempo constante.")

# Barra de pesquisa
search_query = st.text_input("Digite o nome científico da espécie (ex: Ablepharus alaicus):")

if search_query:
    resultado = tree.search_species(search_query)
    
    if resultado:
        st.success(f"Espécie encontrada: {resultado.name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Caminho na Árvore:")
            # Usa o método de backtracking que criamos no nó
            path = resultado.get_path_to_root()
            for step in path:
                st.write(f"⬆️ {step}")
                
        with col2:
            st.subheader("Subespécies (Filhos):")
            if resultado.children:
                for sub in resultado.children.values():
                    st.write(f"🌿 {sub.name}")
            else:
                st.info("Nenhum nó filho registrado.")
    else:
        st.error("Espécie não encontrada. Verifique a grafia.")

st.divider()

# ==========================================
# SEÇÃO 2: Navegação Visual pela Árvore
# ==========================================
st.header("🌳 Navegação Hierárquica")
st.write("Explore a estrutura da árvore n-ária expandindo os nós.")

# Itera sobre as Ordens (primeiro nível da árvore após a raiz)
for order_name, order_node in tree.root.children.items():
    
    # st.expander cria uma "gaveta" clicável
    with st.expander(f"Ordem: {order_name} ({len(order_node.children)} famílias)"):
        
        # Como exibir todas as espécies de uma vez pode travar a tela, 
        # colocamos um seletor para o usuário escolher a Família (o nível seguinte)
        familias = list(order_node.children.keys())
        familia_selecionada = st.selectbox(
            f"Selecione uma família da ordem {order_name}:", 
            ["-- Escolha --"] + familias,
            key=f"select_{order_name}" # Chave única para o componente não dar conflito
        )
        
        if familia_selecionada != "-- Escolha --":
            familia_node = order_node.children[familia_selecionada]
            st.write(f"**Total de espécies:** {len(familia_node.children)}")
            
            # Mostra as espécies como uma lista em um dataframe simples
            especies_lista = list(familia_node.children.keys())
            st.dataframe(especies_lista, column_config={"value": "Nome da Espécie"}, use_container_width=True)