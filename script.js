const API_BASE = 'http://localhost:8000';

document.addEventListener('DOMContentLoaded', () => {
    loadRandomSuggestions();

    // Listen to radio changes to toggle sections
    const radios = document.querySelectorAll('input[name="algorithm"]');
    radios.forEach(r => r.addEventListener('change', toggleSections));

    // Initial toggle state
    toggleSections();
});

document.getElementById('search-btn').addEventListener('click', performSearch);
document.getElementById('search-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

function toggleSections() {
    const algorithm = document.querySelector('input[name="algorithm"]:checked').value;
    if (algorithm === 'splaytree') {
        document.getElementById('tree-section').classList.remove('hidden');
        fetchSplayTreeState();
    } else {
        document.getElementById('tree-section').classList.add('hidden');
    }
}

async function loadRandomSuggestions() {
    const container = document.getElementById('random-suggestions');
    try {
        const res = await fetch(`${API_BASE}/random`);
        if (!res.ok) throw new Error();
        const data = await res.json();

        container.innerHTML = '';
        data.forEach(p => {
            const chip = document.createElement('div');
            chip.className = 'suggestion-chip';
            chip.innerHTML = `<img src="${API_BASE}${p.image_url}" alt="${p.name}"><span>#${p.id} ${p.name}</span>`;
            chip.onclick = () => {
                document.getElementById('search-input').value = p.id;
                // Switch algorithm based on whatever is selected, or default to splay tree? Keep current
                performSearch();
            };
            container.appendChild(chip);
        });
    } catch (err) {
        container.innerHTML = '<span>Falha ao carregar sugestões</span>';
    }
}

async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    const errorMsg = document.getElementById('error-msg');
    const algorithm = document.querySelector('input[name="algorithm"]:checked').value;

    if (!query) {
        errorMsg.textContent = 'Por favor, digite um nome ou ID.';
        return;
    }

    errorMsg.textContent = '';
    hideResults();

    try {
        let id = query;
        // If not a number, fetch ID by name
        if (isNaN(query)) {
            const nameRes = await fetch(`${API_BASE}/search/name/${encodeURIComponent(query)}`);
            if (!nameRes.ok) throw new Error('Pokémon não encontrado.');
            const nameData = await nameRes.json();
            id = nameData.id;
        }

        const res = await fetch(`${API_BASE}/search/${algorithm}/${id}`);
        if (!res.ok) throw new Error('Pokémon não encontrado nas estruturas.');

        const data = await res.json();

        renderPokemon(data.pokemon, data.prev, data.next);

        document.getElementById('iterations-count').textContent = `Interações realizadas na busca: ${data.iterations}`;

        if (algorithm === 'skiplist') {
            animateSkipList(data.path, data.pokemon.id);
        } else {
            animateSplayTree(data.path, data.splay_steps, data.pokemon.id);
            // Fetch the new splay tree state to show the updated root!
            fetchSplayTreeState();
        }

    } catch (err) {
        errorMsg.textContent = err.message;
    }
}

function hideResults() {
    document.getElementById('pokemon-card-container').classList.add('hidden');
    document.getElementById('animation-container').innerHTML = '';
}

function renderPokemon(pokemon, prev, next) {
    // Main card
    document.getElementById('pokemon-img').src = `${API_BASE}${pokemon.image_url}`;
    document.getElementById('pokemon-id').textContent = `#${String(pokemon.id).padStart(3, '0')}`;
    document.getElementById('pokemon-name').textContent = pokemon.name;

    const typesContainer = document.getElementById('pokemon-types');
    typesContainer.innerHTML = `<span class="type-badge type-${pokemon.type1.toLowerCase()}">${pokemon.type1}</span>`;
    if (pokemon.type2) {
        typesContainer.innerHTML += `<span class="type-badge type-${pokemon.type2.toLowerCase()}">${pokemon.type2}</span>`;
    }

    const evoContainer = document.getElementById('pokemon-evolution');
    if (pokemon.evolution) {
        evoContainer.classList.remove('hidden');
        document.getElementById('evo-name').textContent = pokemon.evolution;
    } else {
        evoContainer.classList.add('hidden');
    }

    // Neighbors
    const prevCard = document.getElementById('prev-pokemon');
    if (prev) {
        prevCard.innerHTML = `
            <span>#${String(prev.id).padStart(3, '0')}</span>
            <img src="${API_BASE}${prev.image_url}" alt="${prev.name}">
            <h4>${prev.name}</h4>
        `;
        prevCard.classList.remove('hidden');
        prevCard.onclick = () => {
            document.getElementById('search-input').value = prev.id;
            performSearch();
        };
    } else {
        prevCard.classList.add('hidden');
    }

    const nextCard = document.getElementById('next-pokemon');
    if (next) {
        nextCard.innerHTML = `
            <span>#${String(next.id).padStart(3, '0')}</span>
            <img src="${API_BASE}${next.image_url}" alt="${next.name}">
            <h4>${next.name}</h4>
        `;
        nextCard.classList.remove('hidden');
        nextCard.onclick = () => {
            document.getElementById('search-input').value = next.id;
            performSearch();
        };
    } else {
        nextCard.classList.add('hidden');
    }

    // Show
    document.getElementById('pokemon-card-container').classList.remove('hidden');
}

async function animateSkipList(path, targetId) {
    const container = document.getElementById('animation-container');
    container.innerHTML = '<div style="width: 100%; text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; position: absolute; top: 0;">Saltos e quedas de níveis (Nível | ID - Nome)</div>';
    container.style.paddingTop = '3rem';

    for (let i = 0; i < path.length; i++) {
        const step = path[i];

        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'anim-node';
        if (step.key === targetId && i === path.length - 1) {
            nodeDiv.classList.add('target');
        }

        let label = step.key === -1 ? "HEADER" : `#${step.key} ${step.pokemon_name}`;
        nodeDiv.innerHTML = `<div>L${step.level}</div><strong>${label}</strong>`;

        container.appendChild(nodeDiv);

        // trigger reflow
        void nodeDiv.offsetWidth;
        nodeDiv.classList.add('show');

        if (i < path.length - 1) {
            const arrowDiv = document.createElement('div');
            arrowDiv.className = 'anim-arrow';
            // Se a ação foi "down" (descer de nível no mesmo nó), a seta aponta para baixo ou exibe "Desce"
            if (step.action === 'down') {
                arrowDiv.innerHTML = '↓';
                arrowDiv.style.color = 'var(--primary)';
            } else {
                arrowDiv.innerHTML = '→';
            }
            container.appendChild(arrowDiv);
            void arrowDiv.offsetWidth;
            arrowDiv.classList.add('show');
        }

        await new Promise(r => setTimeout(r, 150));
    }
}

async function animateSplayTree(path, splaySteps, targetId) {
    const container = document.getElementById('animation-container');
    container.innerHTML = '<div style="width: 100%; text-align: center; color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem; position: absolute; top: 0;">Busca na BST e Rotações (Splaying)</div>';
    container.style.paddingTop = '3rem';

    const pathContainer = document.createElement('div');
    pathContainer.style.display = 'flex';
    pathContainer.style.alignItems = 'center';
    pathContainer.style.overflowX = 'auto';
    pathContainer.style.width = '100%';
    pathContainer.style.marginBottom = '2rem';
    container.appendChild(pathContainer);

    // Limit max path shown
    let displayPath = path;
    if (path.length > 40) {
        displayPath = path.slice(0, 10).concat(
            [{ key: '...', pokemon_name: `omitindo ${path.length - 20} nós` }],
            path.slice(-10)
        );
    }

    const pathDelay = displayPath.length > 15 ? 50 : 150;

    for (let i = 0; i < displayPath.length; i++) {
        const step = displayPath[i];

        const nodeDiv = document.createElement('div');
        nodeDiv.className = 'anim-node';
        if (step.key === targetId && i === displayPath.length - 1) {
            nodeDiv.classList.add('target');
        }

        nodeDiv.innerHTML = `<div>Node</div><strong>${step.key === '...' ? '...' : '#' + step.key} ${step.pokemon_name}</strong>`;

        pathContainer.appendChild(nodeDiv);

        void nodeDiv.offsetWidth;
        nodeDiv.classList.add('show');

        if (i < displayPath.length - 1) {
            const arrowDiv = document.createElement('div');
            arrowDiv.className = 'anim-arrow';
            arrowDiv.innerHTML = '→';
            pathContainer.appendChild(arrowDiv);
            void arrowDiv.offsetWidth;
            arrowDiv.classList.add('show');
        }

        await new Promise(r => setTimeout(r, pathDelay));
    }

    if (splaySteps && splaySteps.length > 0) {
        const splayContainer = document.createElement('div');
        splayContainer.style.width = '100%';
        splayContainer.style.display = 'flex';
        splayContainer.style.flexDirection = 'column';
        splayContainer.style.alignItems = 'center';
        container.appendChild(splayContainer);

        // Limit max steps shown to avoid browser lag
        const maxStepsToShow = 30;
        let displaySteps = splaySteps;
        if (splaySteps.length > maxStepsToShow) {
            displaySteps = splaySteps.slice(0, 5).concat(
                [{ type: '...', node: '... omitindo ' + (splaySteps.length - 10) + ' passos ...' }],
                splaySteps.slice(-5)
            );
        }

        const delay = displaySteps.length > 10 ? 100 : 300;

        for (let i = 0; i < displaySteps.length; i++) {
            const step = displaySteps[i];
            const stepDiv = document.createElement('div');
            stepDiv.className = 'splay-step';
            stepDiv.style.opacity = '0';
            stepDiv.innerHTML = `Rotação: <strong>${step.type.toUpperCase()}</strong> no nó #${step.node}`;
            splayContainer.appendChild(stepDiv);

            void stepDiv.offsetWidth;
            stepDiv.style.opacity = '1';

            await new Promise(r => setTimeout(r, delay));
        }

        const finalDiv = document.createElement('div');
        finalDiv.className = 'splay-step';
        finalDiv.style.opacity = '0';
        finalDiv.innerHTML = `<strong style="color: var(--primary);">Nó #${targetId} promovido à raiz!</strong>`;
        splayContainer.appendChild(finalDiv);
        void finalDiv.offsetWidth;
        finalDiv.style.opacity = '1';
    }
}

// --- Splay Tree State Visualizer ---
async function fetchSplayTreeState() {
    try {
        const res = await fetch(`${API_BASE}/splaytree/state`);
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('tree-container');
        container.innerHTML = '';
        if (data) {
            container.appendChild(buildTreeNode(data));
        } else {
            container.innerHTML = '<p>Árvore vazia</p>';
        }
    } catch (err) {
        console.error("Erro ao buscar estado da splay tree", err);
    }
}

function buildTreeNode(node) {
    const wrapper = document.createElement('div');
    wrapper.className = 'tree-node-wrapper';

    // The node itself
    const nodeEl = document.createElement('div');
    nodeEl.className = 'tree-node';
    nodeEl.innerHTML = `<img src="${API_BASE}${node.image_url}" alt="${node.name}"><span>#${node.id}</span>`;
    wrapper.appendChild(nodeEl);

    // Children
    if (node.left || node.right) {
        const childrenDiv = document.createElement('div');
        childrenDiv.className = 'tree-children';
        if (node.left && node.right) {
            childrenDiv.classList.add('has-siblings');
        }

        if (node.left) {
            childrenDiv.appendChild(buildTreeNode(node.left));
        } else if (node.right) {
            // Placeholder for left
            const ph = document.createElement('div');
            ph.className = 'tree-node-wrapper';
            ph.style.visibility = 'hidden';
            ph.innerHTML = '<div class="tree-node"></div>';
            childrenDiv.appendChild(ph);
        }

        if (node.right) {
            childrenDiv.appendChild(buildTreeNode(node.right));
        } else if (node.left) {
            // Placeholder for right
            const ph = document.createElement('div');
            ph.className = 'tree-node-wrapper';
            ph.style.visibility = 'hidden';
            ph.innerHTML = '<div class="tree-node"></div>';
            childrenDiv.appendChild(ph);
        }

        wrapper.appendChild(childrenDiv);
    }

    return wrapper;
}
