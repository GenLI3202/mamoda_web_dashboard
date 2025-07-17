// This variable will hold our table names once loaded from the API.
let availableTables = [];

// --- TAB SWITCHING LOGIC ---
function openTab(evt, tabName) {
    // ... (This function remains the same, no changes needed)
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

// This function handles the click event for the "Show" button in the Data Explorer tab.
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
            
            const tableColumns = columnNames.map(colName => {
                return {
                    title: colName,
                    data: colName,
                    render: function(data, type, row) {
                        if (type === 'display' && typeof data === 'object' && data !== null) {
                            return data.name || data.short_name || data.id || '';
                        }
                        return data;
                    }
                };
            });

            document.getElementById('table-title').textContent = `Data for: ${selectedTableName}`;
            renderTable(data, tableColumns);
        })
        .catch(error => console.error(`Error fetching data for ${selectedTableName}:`, error));
}
// The DataTables render function is now much simpler because the API sends clean data.
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

// This function creates creates dropdown options for each table name.
function populateTableSelection(tableNames) {
    const selector = document.getElementById('table-selector');
    selector.innerHTML = ''; // Clear any old options

    tableNames.forEach((tableName) => {
        const option = document.createElement('option');
        option.value = tableName;
        option.textContent = tableName;
        selector.appendChild(option);
    });
}

// This is the main setup function for the Data Explorer tab.
function initializeDataExplorer() {
    document.getElementById('show-table-btn').addEventListener('click', handleShowTableClick);
    // Show the default table when the page first loads.
    handleShowTableClick();
}

// --- INITIAL PAGE LOAD ---
document.addEventListener('DOMContentLoaded', () => {
    // First, fetch the list of available tables from the API
    fetch('/api/tables')
        .then(response => response.json())
        .then(tableNames => {
            console.log("✅ Available tables loaded:", tableNames);
            availableTables = tableNames; // Store the list
            populateTableSelection(tableNames); // Create the radio buttons
            initializeDataExplorer(); // Setup the Data Explorer
        })
        .catch(error => console.error("❌ Error loading table list:", error));
});