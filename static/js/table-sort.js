/**
 * NBA Analytics Hub - Table Sorting Functionality
 * A robust solution for sorting tables with different data types
 */

function initTableSort(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('thead th.sortable');
    
    headers.forEach(header => {
        header.addEventListener('click', function() {
            // Get the column's data type
            const sortType = this.getAttribute('data-sort') || 'string';
            const columnName = this.getAttribute('data-column');
            
            // Get the current sort direction - MODIFIED to default to descending on first click
            // If header is already sorted descending, then switch to ascending
            let sortDirection = this.classList.contains('sort-desc') ? 'asc' : 'desc';
            
            // Clear all sort indicators
            headers.forEach(h => {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            
            // Add sort indicator to current header
            this.classList.add(sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
            
            // Get the column index
            const colIndex = Array.from(this.parentNode.children).indexOf(this);
            
            // Sort the table
            sortTable(table, colIndex, sortType, sortDirection);
        });
    });
}

function sortTable(table, colIndex, sortType, sortDirection) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Sort rows based on the column data
    const sortedRows = rows.sort((a, b) => {
        const aValue = getCellValue(a, colIndex, sortType);
        const bValue = getCellValue(b, colIndex, sortType);
        
        // Compare values based on sort type
        if (sortType === 'int' || sortType === 'float') {
            return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        } else if (sortType === 'date') {
            // Date sorting - convert to timestamps for comparison
            const aDate = new Date(aValue);
            const bDate = new Date(bValue);
            return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
        } else if (sortType === 'time') {
            // Time sorting (format: MM:SS)
            const aTime = convertTimeToSeconds(aValue);
            const bTime = convertTimeToSeconds(bValue);
            return sortDirection === 'asc' ? aTime - bTime : bTime - aTime;
        } else {
            return sortDirection === 'asc' 
                ? aValue.localeCompare(bValue, undefined, {sensitivity: 'base'}) 
                : bValue.localeCompare(aValue, undefined, {sensitivity: 'base'});
        }
    });
    
    // Remove existing rows
    while (tbody.firstChild) {
        tbody.removeChild(tbody.firstChild);
    }
    
    // Add sorted rows
    sortedRows.forEach(row => {
        tbody.appendChild(row);
    });
    
    // Add visual feedback of sorting
    animateSortedTable(tbody);
}

function getCellValue(row, colIndex, sortType) {
    const cell = row.cells[colIndex];
    let value = cell.textContent.trim();
    
    // Handle different data types
    if (sortType === 'int') {
        return parseInt(value.replace(/[^0-9.-]+/g, '')) || 0;
    } else if (sortType === 'float') {
        return parseFloat(value.replace(/[^0-9.-]+/g, '')) || 0;
    } else if (sortType === 'date' || sortType === 'time') {
        // Just return the raw value for date/time - we'll process it in sortTable
        return value;
    } else {
        return value;
    }
}

function convertTimeToSeconds(timeStr) {
    // Handle MM:SS format
    if (timeStr.includes(':')) {
        const [minutes, seconds] = timeStr.split(':').map(num => parseInt(num, 10));
        return (minutes * 60) + seconds;
    }
    // Handle seconds only
    return parseInt(timeStr, 10) || 0;
}

function animateSortedTable(tbody) {
    // Add subtle animation to show rows are sorted
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 20); // Stagger animation
    });
} 