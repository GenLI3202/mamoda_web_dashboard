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
    console.log("--- Filter Changed ---");
    const selectedStakeholder = document.getElementById('stakeholder-filter').value;
    const selectedCategory = document.getElementById('practice-category-filter').value;
    console.log(`Selected Stakeholder: ${selectedStakeholder}, Selected Category: ${selectedCategory}`);

    let filteredPractices = [...knowledgeData.practices];

    // Filter by category
    if (selectedCategory !== 'all') {
        filteredPractices = filteredPractices.filter(p => p.category === selectedCategory);
    }

    // Filter by stakeholder (this is a more complex, multi-step filter)
    if (selectedStakeholder !== 'all') {
        // Step 1: Find all concerns linked to the selected stakeholder
        const concernIds = knowledgeData.links_stakeholder_to_concern
            .filter(l => l.sh_id === selectedStakeholder)
            .map(l => l.concern_id);
        console.log(`Found ${concernIds.length} concern(s) for this stakeholder:`, concernIds);
        
        // Step 2: Find all SDG targets linked to those concerns
        const targetIds = knowledgeData.links_concern_to_target
            .filter(l => concernIds.includes(l.concern_id))
            .map(l => l.target_id);
        console.log(`Found ${targetIds.length} target(s) for those concerns:`, targetIds);

        // Step 3: Find all practices linked to those SDG targets
        const practiceIds = new Set(knowledgeData.links_practice_to_target
            .filter(l => targetIds.includes(l.target_id))
            .map(l => l.practice_id));
        console.log(`Found ${practiceIds.size} practice(s) for those targets:`, [...practiceIds]);
        
        // Step 4: Filter the practices list to only include those IDs
        filteredPractices = filteredPractices.filter(p => practiceIds.has(p.id));
    }

    console.log(`Rendering table with ${filteredPractices.length} practices.`);
    renderPracticeTable(filteredPractices);
}

// ** KNOWLEDGE GRAPH LOGIC (Temporarily Disabled) **
function drawKnowledgeGraph() {
    console.log("Knowledge Graph tab clicked. Visualization logic is currently disabled for focused development.");
    // The visualization code will go here later.
    graphInitialized = true;
}

// ** SANKEY DIAGRAM LOGIC (Temporarily Disabled) **
function drawSankeyDiagram() {
    console.log("Impact Flow tab clicked. Visualization logic is currently disabled for focused development.");
    // The visualization code will go here later.
    sankeyInitialized = true;
}
