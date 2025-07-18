// Global state variables
let availableTables = [];
let graphData = { nodes: [], edges: [] };
let network = null;
let tomSelectGroup = null;
let tomSelectItem = null;

// --- TAB SWITCHING LOGIC ---
function openTab(evt, tabName) {
    let i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) tabContent[i].style.display = "none";
    tabLinks = document.getElementsByClassName("tab-link");
    for (i = 0; i < tabLinks.length; i++) tabLinks[i].className = tabLinks[i].className.replace(" active", "");
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// --- DATA EXPLORER LOGIC ---
function handleShowTableClick() {
    const selectedTableName = document.getElementById('table-selector').value;
    fetch(`/api/table/${selectedTableName}`)
        .then(response => response.json())
        .then(data => {
            const columnNames = (data && data.length > 0) ? Object.keys(data[0]) : [];
            const tableColumns = columnNames.map(colName => ({
                title: colName,
                data: colName,
                render: (d) => (typeof d === 'object' && d !== null) ? (d.name || d.short_name || d.id || '') : d
            }));
            document.getElementById('table-title').textContent = `Data for: ${selectedTableName}`;
            renderTable(data || [], tableColumns);
        })
        .catch(error => console.error(`Error fetching data for ${selectedTableName}:`, error));
}

function renderTable(data, columns) {
    if ($.fn.DataTable.isDataTable('#results-table')) {
        $('#results-table').DataTable().destroy();
    }
    $('#results-table').empty();
    $('#results-table').DataTable({ data, columns, responsive: true, paging: true, searching: true, info: true });
}

function populateTableSelection(tableNames) {
    const selector = document.getElementById('table-selector');
    selector.innerHTML = '';
    tableNames.forEach(tableName => selector.innerHTML += `<option value="${tableName}">${tableName}</option>`);
}

function initializeDataExplorer() {
    document.getElementById('show-table-btn').addEventListener('click', handleShowTableClick);
    handleShowTableClick();
}

// --- KNOWLEDGE GRAPH LOGIC ---

function initializeKnowledgeGraph() {
    fetch('/api/graph-data')
        .then(response => response.json())
        .then(data => {
            graphData = data;
            setupGraphSelectors();
            document.getElementById('show-graph-btn').addEventListener('click', drawKnowledgeGraph);
        })
        .catch(error => console.error("❌ Error loading graph data:", error));
}

function setupGraphSelectors() {
    const groupedNodes = graphData.nodes.reduce((acc, node) => {
        const group = node.group || 'unknown';
        if (!acc[group]) acc[group] = [];
        acc[group].push({ value: node.id, text: node.label });
        return acc;
    }, {});

    tomSelectGroup = new TomSelect('#graph-group-selector', {
        options: [
            { value: 'all', text: 'Show Full Graph' },
            ...Object.keys(groupedNodes).map(g => ({ value: `group_${g}`, text: `All ${g.replace('_', ' ')}s` }))
        ],
        onChange: (value) => {
            tomSelectItem.clear();
            tomSelectItem.clearOptions();
            if (value && !value.startsWith('group_') && value !== 'all') {
                const groupName = value;
                const items = groupedNodes[groupName] || [];
                items.sort((a,b) => a.text.localeCompare(b.text));
                tomSelectItem.addOptions(items);
                tomSelectItem.enable();
            } else {
                tomSelectItem.disable();
            }
        }
    });
    
    Object.keys(groupedNodes).forEach(groupName => {
        const capitalized = (groupName.charAt(0).toUpperCase() + groupName.slice(1)).replace('_', ' ');
        tomSelectGroup.addOption({ value: groupName, text: capitalized + 's' });
    });

    tomSelectItem = new TomSelect('#graph-item-selector', {
        placeholder: 'Select a specific item...',
    });
    tomSelectItem.disable();
}

function drawKnowledgeGraph() {
    const groupSelection = tomSelectGroup.getValue();
    const itemSelection = tomSelectItem.getValue();
    const selection = itemSelection || groupSelection;

    let displayData = { nodes: [], edges: [] };
    let focusGroup = null;

    if (!selection || selection === 'all') {
        displayData = { ...graphData };
    } else if (selection.startsWith('group_')) {
        const groupName = selection.split('_')[1];
        focusGroup = groupName;
        
        const groupNodeIds = new Set(graphData.nodes.filter(n => n.group === groupName).map(n => n.id));
        const connectedNodeIds = new Set(groupNodeIds);
        graphData.edges.forEach(edge => {
            if (groupNodeIds.has(edge.from)) connectedNodeIds.add(edge.to);
            if (groupNodeIds.has(edge.to)) connectedNodeIds.add(edge.from);
        });
        displayData.nodes = graphData.nodes.filter(node => connectedNodeIds.has(node.id));
        displayData.edges = graphData.edges.filter(edge => connectedNodeIds.has(edge.from) && connectedNodeIds.has(edge.to));
    } else {
        const focusNodeId = selection;
        const focusNode = graphData.nodes.find(n => n.id === focusNodeId);
        if (focusNode) focusGroup = focusNode.group;
        
        const connectedNodeIds = new Set([focusNodeId]);
        graphData.edges.forEach(edge => {
            if (edge.from === focusNodeId) connectedNodeIds.add(edge.to);
            if (edge.to === focusNodeId) connectedNodeIds.add(edge.from);
        });
        displayData.nodes = graphData.nodes.filter(node => connectedNodeIds.has(node.id));
        displayData.edges = graphData.edges.filter(edge => connectedNodeIds.has(edge.from) && connectedNodeIds.has(edge.to));
    }

    if (focusGroup) {
        displayData.nodes = JSON.parse(JSON.stringify(displayData.nodes));
        displayData.nodes.forEach(node => {
            if (node.group === focusGroup) {
                node.shape = 'star';
                node.size = 16;
            }
        });
    }

    const container = document.getElementById('knowledge-graph-canvas');
    const options = {
        nodes: {
            shape: 'dot',
            size: 10,
            font: { size: 12, color: '#555', vadjust: 15 },
            borderWidth: 2
        },
        edges: {
            width: 0.5,
            color: { color: '#cccccc', highlight: '#4a69bd' }
        },
        physics: {
            solver: 'forceAtlas2Based',
            forceAtlas2Based: { gravitationalConstant: -50, centralGravity: 0.01, springLength: 200, springConstant: 0.08, avoidOverlap: 0.5 },
            maxVelocity: 50,
            minVelocity: 0.1,
            stabilization: { iterations: 150 }
        },
        interaction: { hover: true, tooltipDelay: 200 },
        groups: {
            practice: { color: { border: '#f0ad4e', background: '#f0ad4e'} },
            stakeholder: { color: { border: '#5bc0de', background: '#5bc0de'} },
            concern: { color: { border: '#d9534f', background: '#d9534f'} },
            target: { color: { border: '#5cb85c', background: '#5cb85c'} },
            goal: { color: { border: '#337ab7', background: '#337ab7'} },
            objective: { color: { border: '#34495e', background: '#34495e'} },
            action: { color: { border: '#9b59b6', background: '#9b59b6'} },
            stakeholdergroup: { color: { border: '#1abc9c', background: '#1abc9c'} },
            mining_indicator: { color: { border: '#777777', background: '#777777'} },
            sdg_indicator: { color: { border: '#2ecc71', background: '#2ecc71'} }
        }
    };

    network = new vis.Network(container, displayData, options);

    network.on('click', function(params) {
        const infoPanel = document.getElementById('graph-info-panel');
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = graphData.nodes.find(n => n.id === nodeId);
            if (node) {
                let html = `<h4>${node.label}</h4>`;
                html += `<p><strong>Type:</strong> ${node.group.replace('_', ' ')}</p>`;
                html += `<p><strong>ID:</strong> ${node.id}</p>`;
                
                const connections = graphData.edges
                    .map(edge => {
                        if (edge.from === nodeId) return graphData.nodes.find(n => n.id === edge.to);
                        if (edge.to === nodeId) return graphData.nodes.find(n => n.id === edge.from);
                        return null;
                    })
                    .filter(Boolean);
                const connectionsByType = connections.reduce((acc, n) => {
                    if (!acc[n.group]) acc[n.group] = [];
                    acc[n.group].push(n);
                    return acc;
                }, {});
                if (Object.keys(connectionsByType).length > 0) {
                    html += `<p><strong>Connections:</strong></p>`;
                    for (const group in connectionsByType) {
                        const capitalized = (group.charAt(0).toUpperCase() + group.slice(1)).replace('_', ' ');
                        html += `<details class="connection-group"><summary>${capitalized}s (${connectionsByType[group].length})</summary><ul>`;
                        connectionsByType[group].forEach(cn => {
                            html += `<li>(<em>${cn.id}</em>) ${cn.label}</li>`;
                        });
                        html += `</ul></details>`;
                    }
                }
                infoPanel.innerHTML = html;
            }
        } else {
            infoPanel.innerHTML = '<h4>Node Information</h4><p>Click on a node to see its details here.</p>';
        }
    });
}

// --- INITIAL PAGE LOAD ---
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/tables')
        .then(response => response.json())
        .then(tableNames => {
            availableTables = tableNames;
            populateTableSelection(tableNames);
            initializeDataExplorer();
        })
        .catch(error => console.error("❌ Error loading table list:", error));

    initializeKnowledgeGraph();
});