/**
 * Table sorting functionality
 * Allows for sorting table data by clicking on column headers
 */

function initTableSort(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th[data-sort]');
    
    headers.forEach(header => {
        // Add sort icons and styling
        header.classList.add('sortable');
        
        // Add click handler
        header.addEventListener('click', function() {
            const sortType = this.getAttribute('data-sort');
            const columnIndex = Array.from(headers).indexOf(this);
            const dataColumn = this.getAttribute('data-column');
            
            // Determine sort direction
            let sortDirection = 'asc';
            if (this.classList.contains('sort-asc')) {
                sortDirection = 'desc';
                this.classList.remove('sort-asc');
                this.classList.add('sort-desc');
            } else {
                // Remove any existing sort classes from all headers
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });
                this.classList.add('sort-asc');
            }
            
            // Sort the table
            sortTable(table, columnIndex, sortType, sortDirection);
            
            // Add sorting information to URL parameters without reloading
            if (dataColumn) {
                updateUrlParams(dataColumn, sortDirection);
            }
        });
    });
}

function sortTable(table, columnIndex, sortType, sortDirection) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort the rows
    rows.sort((a, b) => {
        const aValue = getCellValue(a, columnIndex, sortType);
        const bValue = getCellValue(b, columnIndex, sortType);
        
        if (sortType === 'int' || sortType === 'float') {
            return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        } else {
            return sortDirection === 'asc' 
                ? aValue.localeCompare(bValue)
                : bValue.localeCompare(aValue);
        }
    });
    
    // Reattach sorted rows to tbody
    rows.forEach(row => tbody.appendChild(row));
}

function getCellValue(row, index, sortType) {
    const cell = row.cells[index];
    const content = cell.textContent.trim();
    
    // For salary, remove '$' and ',' before converting to number
    if (content.includes('$')) {
        return parseFloat(content.replace(/[$,]/g, ''));
    }
    
    if (sortType === 'int') {
        return parseInt(content, 10) || 0;
    } else if (sortType === 'float') {
        return parseFloat(content) || 0;
    } else {
        return content;
    }
}

function updateUrlParams(sortColumn, direction) {
    // Don't change the URL if we're just sorting client-side
    // This would only be needed if we want to remember the sort in the URL
    // But since we're doing client-side sorting, we'll just leave it commented out
    
    /*
    const url = new URL(window.location);
    url.searchParams.set('sort_by', sortColumn);
    url.searchParams.set('direction', direction);
    window.history.replaceState({}, '', url);
    */
} 