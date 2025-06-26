import * as dom from './dom.js';
import * as state from './state.js';
import { handleTransform, downloadResults } from './api.js';
import { switchView, showSchemaPreview, renderSortedTable, clearAllEdits, highlightSearchTerm, removeHighlights } from './ui.js';
import { setSelectedFiles, setSortState } from './state.js';

// Setup event listeners
export function setupEventListeners() {
    // File upload
    dom.dropZone.addEventListener('click', () => dom.fileInput.click());
    dom.dropZone.addEventListener('dragover', handleDragOver);
    dom.dropZone.addEventListener('dragleave', handleDragLeave);
    dom.dropZone.addEventListener('drop', handleDrop);
    dom.fileInput.addEventListener('change', handleFileSelect);
    
    // Model selection
    dom.modelSelect.addEventListener('change', handleModelChange);
    
    // Transform button
    dom.transformBtn.addEventListener('click', handleTransform);
    
    // Download button
    document.getElementById('downloadBtn')?.addEventListener('click', handleDownload);
    
    // View toggle buttons
    document.getElementById('tableViewBtn')?.addEventListener('click', () => switchView('table'));
    document.getElementById('fileViewBtn')?.addEventListener('click', () => switchView('file'));
    
    // Search functionality
    dom.searchInput?.addEventListener('input', debounce(handleSearch, 300));
    
    // Clear edits button
    dom.clearEditsBtn?.addEventListener('click', clearAllEdits);

    // Close popovers when clicking outside
    document.addEventListener('click', () => {
        document.querySelectorAll('.field-chip.active').forEach(chip => {
            chip.classList.remove('active');
        });
    });
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// File handling
function handleDragOver(e) {
    e.preventDefault();
    dom.dropZone.classList.add('drop-zone-active');
}

function handleDragLeave(e) {
    e.preventDefault();
    dom.dropZone.classList.remove('drop-zone-active');
}

function handleDrop(e) {
    e.preventDefault();
    dom.dropZone.classList.remove('drop-zone-active');
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function handleFiles(files) {
    setSelectedFiles(files);
    
    if (files.length > 0) {
        // Update UI to show selected files
        const fileText = files.length === 1 ? files[0].name : `${files.length} files selected`;
        document.querySelector('.drop-text').textContent = fileText;
        
        // Show analysis options
        dom.analysisOptions.classList.remove('hidden');
        
        // Reset results
        dom.resultsSection.classList.add('hidden');
        dom.errorDisplay.classList.add('hidden');
        state.setEditedData({});
        state.setSortState({ column: null, direction: null });
    }
}

// Model selection
function handleModelChange(e) {
    const selectedOption = e.target.selectedOptions[0];
    if (selectedOption && selectedOption.dataset.description) {
        dom.modelDescription.textContent = selectedOption.dataset.description;
        dom.modelDescription.classList.remove('hidden');
        
        // Show schema preview
        showSchemaPreview(e.target.value);
    } else {
        dom.modelDescription.classList.add('hidden');
        document.getElementById('schemaPreview').classList.add('hidden');
    }
}

// Handle column sorting
export function handleSort(column) {
    // Update sort state
    if (state.sortState.column === column) {
        // Toggle direction
        if (state.sortState.direction === 'asc') {
            setSortState({ ...state.sortState, direction: 'desc' });
        } else if (state.sortState.direction === 'desc') {
            setSortState({ column: null, direction: null });
        } else {
            setSortState({ ...state.sortState, direction: 'asc' });
        }
    } else {
        setSortState({ column, direction: 'asc' });
    }
    
    // Update header classes
    document.querySelectorAll('#tableHeader th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.column === state.sortState.column) {
            if (state.sortState.direction === 'asc') {
                th.classList.add('sort-asc');
            } else if (state.sortState.direction === 'desc') {
                th.classList.add('sort-desc');
            }
        }
    });
    
    // Re-render the table with sorted data
    renderSortedTable();
}

// Search functionality
function handleSearch() {
    const searchTerm = dom.searchInput.value.toLowerCase();
    const rows = document.querySelectorAll('#tableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
        
        // Highlight matching text
        if (shouldShow && searchTerm) {
            highlightSearchTerm(row, searchTerm);
        } else {
            removeHighlights(row);
        }
    });
}

async function handleDownload() {
    const formatSelect = document.getElementById('downloadFormat');
    const format = formatSelect ? formatSelect.value : 'excel';
    await downloadResults(format);
}
