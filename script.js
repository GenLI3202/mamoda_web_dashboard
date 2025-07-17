// This variable will hold our table names once loaded from the API.
let availableTables = [];
// This variable will hold the complete graph data (nodes and edges).
let graphData = { nodes: [], edges: [] };
// This variable will hold the vis.js network instance.
let network = null;

// --- TAB SWITCHING LOGIC ---
function openTab(evt, tabName) {
    let i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }
    tabLinks = document.getElementsByClassName("tab-link");
    for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].className = tabLinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// --- DATA EXPLORER LOGIC ---
function handleShowTableClick() {
    const selector = document.getElementById('table-selector');
    const selectedTableName = selector.value;
    
    fetch(`/api/table/${selectedTableName}`)
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                renderTable([], []);
                document.getElementById('table-title').textContent = `No data found for: ${selectedTableName}`;
                return;
            }
            const columnNames = Object.keys(data[0]);
            const tableColumns = columnNames.map(colName => ({
                title: colName,
                data: colName,
                render: (data, type, row) => (type === 'display' && typeof data === 'object' && data !== null) ? (data.name || data.short_name || data.id || '') : data
            }));
            document.getElementById('table-title').textContent = `Data for: ${selectedTableName}`;
            renderTable(data, tableColumns);
        })
        .catch(error => console.error(`Error fetching data for ${selectedTableName}:`, error));
}

function renderTable(data, columns) {
    if ($.fn.DataTable.isDataTable('#results-table')) {
        $('#results-table').DataTable().destroy();
    }
    $('#results-table').empty();
    $('#results-table').DataTable({
        data: data,
        columns: columns,
        responsive: true,
        paging: true,
        searching: true,
        info: true
    });
}

function populateTableSelection(tableNames) {
    const selector = document.getElementById('table-selector');
    selector.innerHTML = '';
    tableNames.forEach(tableName => {
        const option = document.createElement('option');
        option.value = tableName;
        option.textContent = tableName;
        selector.appendChild(option);
    });
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
            console.log("✅ Graph data loaded successfully!", data);
            graphData = data;
            populateGraphSelector();
            document.getElementById('show-graph-btn').addEventListener('click', drawKnowledgeGraph);
        })
        .catch(error => console.error("❌ Error loading graph data:", error));
}

function populateGraphSelector() {
    const selector = document.getElementById('graph-entity-selector');
    selector.innerHTML = '<option value="all">Show Full Graph</option>';

    const groupedNodes = graphData.nodes.reduce((acc, node) => {
        const group = node.group || 'unknown';
        if (!acc[group]) acc[group] = [];
        acc[group].push(node);
        return acc;
    }, {});

    for (const groupName in groupedNodes) {
        const optgroup = document.createElement('optgroup');
        const capitalizedGroupName = groupName.charAt(0).toUpperCase() + groupName.slice(1);
        optgroup.label = `${capitalizedGroupName}s`;
        
        const groupOption = document.createElement('option');
        groupOption.value = `group_${groupName}`;
        groupOption.textContent = `Show All ${capitalizedGroupName}s`;
        optgroup.appendChild(groupOption);

        groupedNodes[groupName].sort((a, b) => a.label.localeCompare(b.label));
        
        groupedNodes[groupName].forEach(node => {
            const option = document.createElement('option');
            option.value = node.id;
            option.textContent = `  ↳ ${node.label}`;
            optgroup.appendChild(option);
        });
        selector.appendChild(optgroup);
    }
}

function drawKnowledgeGraph() {
    const selection = document.getElementById('graph-entity-selector').value;
    let displayData = { nodes: [], edges: [] };

    if (selection === 'all') {
        displayData = graphData;
    } else if (selection.startsWith('group_')) {
        const groupName = selection.split('_')[1];
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
        const connectedNodeIds = new Set([focusNodeId]);
        graphData.edges.forEach(edge => {
            if (edge.from === focusNodeId) connectedNodeIds.add(edge.to);
            if (edge.to === focusNodeId) connectedNodeIds.add(edge.from);
        });
        displayData.nodes = graphData.nodes.filter(node => connectedNodeIds.has(node.id));
        displayData.edges = graphData.edges.filter(edge => connectedNodeIds.has(edge.from) && connectedNodeIds.has(edge.to));
    }

    const container = document.getElementById('knowledge-graph-canvas');
    const options = {
        nodes: { shape: 'dot', size: 16, font: { size: 14, color: '#333' }, borderWidth: 2 },
        edges: { width: 1, color: { color: '#cccccc', highlight: '#4a69bd' } },
        physics: { forceAtlas2Based: { gravitationalConstant: -50, centralGravity: 0.005, springLength: 230, springConstant: 0.18 }, maxVelocity: 146, solver: 'forceAtlas2Based', timestep: 0.35, stabilization: { iterations: 150 } },
        interaction: { hover: true, tooltipDelay: 200 },
        groups: { practice: { color: '#f0ad4e' }, stakeholder: { color: '#5bc0de' }, concern: { color: '#d9534f' }, target: { color: '#5cb85c' }, goal: { color: '#337ab7' }, indicator: { color: '#777777' } }
    };

    network = new vis.Network(container, displayData, options);

    // --- NEW: Add CLICK Interactivity for the Sidebar ---
    network.on('click', function(params) {
        const infoPanel = document.getElementById('graph-info-panel');
        // If a node is clicked
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = graphData.nodes.find(n => n.id === nodeId);
            
            if (node) {
                let html = `<h4>${node.label}</h4>`;
                html += `<p><strong>Type:</strong> ${node.group}</p>`;
                
                const connectedEdges = graphData.edges.filter(edge => edge.from === nodeId || edge.to === nodeId);
                
                // Group connections by type
                const connectionsByType = connectedEdges.reduce((acc, edge) => {
                    const otherNodeId = edge.from === nodeId ? edge.to : edge.from;
                    const otherNode = graphData.nodes.find(n => n.id === otherNodeId);
                    if (otherNode) {
                        const group = otherNode.group || 'unknown';
                        if (!acc[group]) acc[group] = [];
                        acc[group].push(otherNode);
                    }
                    return acc;
                }, {});

                if (Object.keys(connectionsByType).length > 0) {
                    html += `<p><strong>Connections:</strong></p>`;
                    for (const group in connectionsByType) {
                        const groupNodes = connectionsByType[group];
                        const capitalizedGroup = group.charAt(0).toUpperCase() + group.slice(1);
                        // Use <details> for collapsible sections
                        html += `<details class="connection-group">`;
                        html += `<summary>${capitalizedGroup}s (${groupNodes.length})</summary>`;
                        html += `<ul>`;
                        groupNodes.forEach(connectedNode => {
                            html += `<li>${connectedNode.label}</li>`;
                        });
                        html += `</ul></details>`;
                    }
                }
                infoPanel.innerHTML = html;
            }
        } else {
            // If the background is clicked, reset the sidebar
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