/* FILE: script.js */

// State variables to track if visualizations have been initialized
let knowledgeData = {};
let graphInitialized = false;
let sankeyInitialized = false;

// ** GLOBAL TAB SWITCHING FUNCTION **
// This function is in the global scope, so the HTML onclick can find it.
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

    // Lazy load visualizations only when the tab is clicked for the first time
    if (tabName === 'Graph' && !graphInitialized) {
        drawKnowledgeGraph();
    }
    if (tabName === 'Sankey' && !sankeyInitialized) {
        drawSankeyDiagram();
    }
}

// ** CORE APPLICATION LOGIC **

// This function runs once the entire HTML page is ready
document.addEventListener('DOMContentLoaded', () => {
    // Fetch the JSON data
    // --- THIS IS THE CORRECTED LINE ---
    fetch('mining_knowledge.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            knowledgeData = data;
            console.log("Data loaded successfully!", knowledgeData);
            initializeDataExplorer();
        })
        .catch(error => {
            console.error('Error loading knowledge data:', error);
        });
});

// Main function to set up the Data Explorer tab
function initializeDataExplorer() {
    populateFilters();
    renderPracticeTable(knowledgeData.practices);
    
    document.getElementById('stakeholder-filter').addEventListener('change', handleFilterChange);
    document.getElementById('practice-category-filter').addEventListener('change', handleFilterChange);
}

// Function to populate the filter dropdowns
function populateFilters() {
    const stakeholderFilter = document.getElementById('stakeholder-filter');
    stakeholderFilter.innerHTML = '<option value="all">All Stakeholders</option>';
    knowledgeData.stakeholders.forEach(sh => {
        stakeholderFilter.innerHTML += `<option value="${sh.id}">${sh.name}</option>`;
    });

    const practiceFilter = document.getElementById('practice-category-filter');
    practiceFilter.innerHTML = '<option value="all">All Practice Categories</option>';
    const categories = [...new Set(knowledgeData.practices.map(p => p.category))];
    categories.forEach(cat => {
        practiceFilter.innerHTML += `<option value="${cat}">${cat}</option>`;
    });
}

// Function to draw the main data table
function renderPracticeTable(practices) {
    const tableBody = document.querySelector("#results-table tbody");
    tableBody.innerHTML = ""; // Clear existing rows
    if (!practices || practices.length === 0) {
        const row = tableBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 3;
        cell.textContent = "No matching practices found.";
        cell.style.textAlign = "center";
        return;
    }
    practices.forEach(practice => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${practice.name}</td>
            <td>${practice.category}</td>
            <td>${practice.description || ''}</td>
        `;
    });
}

// Function that runs every time a filter is changed
function handleFilterChange() {
    const selectedStakeholder = document.getElementById('stakeholder-filter').value;
    const selectedCategory = document.getElementById('practice-category-filter').value;

    let filteredPractices = [...knowledgeData.practices];

    // Filter by category
    if (selectedCategory !== 'all') {
        filteredPractices = filteredPractices.filter(p => p.category === selectedCategory);
    }

    // Filter by stakeholder (this is a more complex, multi-step filter)
    if (selectedStakeholder !== 'all') {
        const concernIds = knowledgeData.links_stakeholder_to_concern
            .filter(l => l.sh_id === selectedStakeholder)
            .map(l => l.concern_id);
        
        const targetIds = knowledgeData.links_concern_to_target
            .filter(l => concernIds.includes(l.concern_id))
            .map(l => l.target_id);

        const practiceIds = new Set(knowledgeData.links_practice_to_target
            .filter(l => targetIds.includes(l.target_id))
            .map(l => l.practice_id));
        
        filteredPractices = filteredPractices.filter(p => practiceIds.has(p.id));
    }

    renderPracticeTable(filteredPractices);
}

// ** KNOWLEDGE GRAPH LOGIC **
function drawKnowledgeGraph() {
    if (typeof vis === 'undefined') { console.error("vis.js library not loaded!"); return; }
    
    const nodes = [
        ...knowledgeData.practices.map(d => ({id: d.id, label: d.name, group: 'practice'})),
        ...knowledgeData.stakeholders.map(d => ({id: d.id, label: d.name, group: 'stakeholder'})),
        ...knowledgeData.concerns.map(d => ({id: d.id, label: d.name, group: 'concern'})),
        ...knowledgeData.sdg_targets.map(d => ({id: d.id, label: d.short_name, group: 'target'}))
    ];

    const edges = [
        ...knowledgeData.links_practice_to_target.map(l => ({from: l.practice_id, to: l.target_id})),
        ...knowledgeData.links_stakeholder_to_concern.map(l => ({from: l.sh_id, to: l.concern_id})),
        ...knowledgeData.links_concern_to_target.map(l => ({from: l.concern_id, to: l.target_id}))
    ];

    const container = document.getElementById('knowledge-network');
    const data = { nodes: nodes, edges: edges };
    const options = {
        nodes: { shape: 'dot', size: 16 },
        physics: { stabilization: false, barnesHut: { gravitationalConstant: -80000, springConstant: 0.001, springLength: 200 } },
        groups: {
            practice: { color: { background: '#f0ad4e' } },
            stakeholder: { color: { background: '#5bc0de' } },
            concern: { color: { background: '#d9534f' } },
            target: { color: { background: '#5cb85c' } }
        }
    };

    const network = new vis.Network(container, data, options);
    graphInitialized = true;
}

// ** SANKEY DIAGRAM LOGIC **
function drawSankeyDiagram() {
    if (typeof google === 'undefined') { console.error("Google Charts library not loaded!"); return; }
    google.charts.load('current', {'packages':['sankey']});
    google.charts.setOnLoadCallback(() => {
        const dataTable = new google.visualization.DataTable();
        dataTable.addColumn('string', 'From');
        dataTable.addColumn('string', 'To');
        dataTable.addColumn('number', 'Weight');
        
        const sankeyData = knowledgeData.links_practice_to_target.map(l => {
            const practiceName = knowledgeData.practices.find(p => p.id === l.practice_id)?.name;
            const targetName = knowledgeData.sdg_targets.find(t => t.id === l.target_id)?.short_name;
            // Ensure we have both names before adding the row
            if (practiceName && targetName) {
                return [practiceName, targetName, l.impact_score || 1];
            }
            return null;
        }).filter(row => row !== null); // Filter out any null entries
        
        dataTable.addRows(sankeyData);
        
        const options = { width: '100%', height: 550 };
        const chart = new google.visualization.Sankey(document.getElementById('sankey-diagram'));
        chart.draw(dataTable, options);
        sankeyInitialized = true;
    });
}
