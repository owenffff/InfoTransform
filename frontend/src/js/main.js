// Information Transformer JavaScript - Enhanced with Sorting and Editing

// Global variables
let selectedFiles = [];
let transformResults = null;
let currentView = 'table'; // Default to table view
let eventSource = null;
let streamingResults = [];
let modelFields = [];
let editedData = {}; // Track edited values
let sortState = { column: null, direction: null }; // Track sort state
window.modelsData = null;

// DOM elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const analysisOptions = document.getElementById('analysisOptions');
const modelSelect = document.getElementById('modelSelect');
const aiModelSelect = document.getElementById('aiModelSelect');
const modelDescription = document.getElementById('modelDescription');
const customInstructions = document.getElementById('customInstructions');
const transformBtn = document.getElementById('transformBtn');
const processingStatus = document.getElementById('processingStatus');
const processingText = document.getElementById('processingText');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultsSummary = document.getElementById('resultsSummary');
const errorDisplay = document.getElementById('errorDisplay');
const searchInput = document.getElementById('searchInput');
const clearEditsBtn = document.getElementById('clearEditsBtn');
const toastContainer = document.getElementById('toastContainer');

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAnalysisModels();
    setupEventListeners();
    
    // Load view preference from localStorage
    const savedView = localStorage.getItem('preferredView') || 'table';
    currentView = savedView;
    updateViewToggle();
});

// Load available analysis models
async function loadAnalysisModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        // Store the data globally
        window.modelsData = data;
        
        // Populate analysis models
        modelSelect.innerHTML = '<option value="">Select an analysis model...</option>';
        for (const [key, model] of Object.entries(data.models)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = model.name;
            option.dataset.description = model.description;
            modelSelect.appendChild(option);
        }
        
        // Populate AI models
        aiModelSelect.innerHTML = '<option value="">Default</option>';
        for (const [name, config] of Object.entries(data.ai_models.models)) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = `${name} (${config.max_tokens} tokens)`;
            aiModelSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        showError('Failed to load analysis models. Please refresh the page.');
    }
}

// Setup event listeners
function setupEventListeners() {
    // File upload
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    // Model selection
    modelSelect.addEventListener('change', handleModelChange);
    
    // Transform button
    transformBtn.addEventListener('click', handleTransform);
    
    // Download button
    document.getElementById('downloadBtn')?.addEventListener('click', handleDownload);
    
    // View toggle buttons
    document.getElementById('tableViewBtn')?.addEventListener('click', () => switchView('table'));
    document.getElementById('fileViewBtn')?.addEventListener('click', () => switchView('file'));
    
    // Search functionality
    searchInput?.addEventListener('input', debounce(handleSearch, 300));
    
    // Clear edits button
    clearEditsBtn?.addEventListener('click', clearAllEdits);
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

// View switching
function switchView(view) {
    currentView = view;
    localStorage.setItem('preferredView', view);
    updateViewToggle();
    
    // Re-display results in the new view if we have them
    if (transformResults) {
        displayResults(transformResults);
    }
}

function updateViewToggle() {
    const tableBtn = document.getElementById('tableViewBtn');
    const fileBtn = document.getElementById('fileViewBtn');
    const tableView = document.getElementById('tableView');
    const fileView = document.getElementById('fileView');
    
    // Update button states
    if (currentView === 'table') {
        tableBtn?.classList.add('active');
        fileBtn?.classList.remove('active');
        tableView?.classList.remove('hidden');
        fileView?.classList.add('hidden');
    } else {
        tableBtn?.classList.remove('active');
        fileBtn?.classList.add('active');
        tableView?.classList.add('hidden');
        fileView?.classList.remove('hidden');
    }
}

// File handling
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drop-zone-active');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drop-zone-active');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drop-zone-active');
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    handleFiles(files);
}

function handleFiles(files) {
    selectedFiles = files;
    
    if (files.length > 0) {
        // Update UI to show selected files
        const fileText = files.length === 1 ? files[0].name : `${files.length} files selected`;
        document.querySelector('.drop-text').textContent = fileText;
        
        // Show analysis options
        analysisOptions.classList.remove('hidden');
        
        // Reset results
        resultsSection.classList.add('hidden');
        errorDisplay.classList.add('hidden');
        editedData = {};
        sortState = { column: null, direction: null };
    }
}

// Model selection
function handleModelChange(e) {
    const selectedOption = e.target.selectedOptions[0];
    if (selectedOption && selectedOption.dataset.description) {
        modelDescription.textContent = selectedOption.dataset.description;
        modelDescription.classList.remove('hidden');
        
        // Show schema preview
        showSchemaPreview(e.target.value);
    } else {
        modelDescription.classList.add('hidden');
        document.getElementById('schemaPreview').classList.add('hidden');
    }
}

function showSchemaPreview(modelKey) {
    const schemaPreview = document.getElementById('schemaPreview');
    const chipsContainer = document.getElementById('schemaChipsContainer');
    
    const modelInfo = window.modelsData?.models[modelKey];
    
    if (modelInfo && modelInfo.fields) {
        chipsContainer.innerHTML = '';
        
        Object.entries(modelInfo.fields).forEach(([fieldName, fieldInfo]) => {
            const chip = createFieldChip(fieldName, fieldInfo);
            chipsContainer.appendChild(chip);
        });
        
        schemaPreview.classList.remove('hidden');
    }
}

function createFieldChip(fieldName, fieldInfo) {
    const chip = document.createElement('div');
    chip.className = 'field-chip';
    if (!fieldInfo.required) {
        chip.className += ' optional';
    }
    
    // Chip text
    chip.innerHTML = `<span>${fieldName}${!fieldInfo.required ? '?' : ''}</span>`;
    
    // Create popover
    const popover = document.createElement('div');
    popover.className = 'field-details-popover';
    popover.innerHTML = `
        <div class="font-semibold mb-2">${fieldName}</div>
        <div class="space-y-1 text-sm">
            <div><span class="font-medium">Type:</span> ${fieldInfo.type}</div>
            <div><span class="font-medium">Required:</span> ${fieldInfo.required ? 'Yes' : 'No'}</div>
            ${fieldInfo.description ? `<div><span class="font-medium">Description:</span> ${fieldInfo.description}</div>` : ''}
        </div>
    `;
    
    chip.appendChild(popover);
    
    // Click handler
    chip.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close others
        document.querySelectorAll('.field-chip').forEach(c => {
            if (c !== chip) c.classList.remove('active');
        });
        chip.classList.toggle('active');
    });
    
    return chip;
}

// Close popovers when clicking outside
document.addEventListener('click', () => {
    document.querySelectorAll('.field-chip.active').forEach(chip => {
        chip.classList.remove('active');
    });
});

// Transform files
async function handleTransform() {
    if (!selectedFiles.length) {
        showError('Please select files to transform');
        return;
    }
    
    if (!modelSelect.value) {
        showError('Please select an analysis model');
        return;
    }
    
    // Hide previous results
    resultsSection.classList.add('hidden');
    errorDisplay.classList.add('hidden');
    
    // Show processing status
    processingStatus.classList.remove('hidden');
    analysisOptions.classList.add('hidden');
    
    // Reset streaming results
    streamingResults = [];
    modelFields = [];
    editedData = {};
    sortState = { column: null, direction: null };
    
    // Always use streaming endpoint (v2) for both single and multiple files
    await handleStreamingTransform();
}

// Handle streaming transform for all files
async function handleStreamingTransform() {
    const formData = new FormData();
    for (const file of selectedFiles) {
        formData.append('files', file);
    }
    formData.append('model_key', modelSelect.value);
    formData.append('custom_instructions', customInstructions.value || '');
    if (aiModelSelect.value) {
        formData.append('ai_model', aiModelSelect.value);
    }
    
    // Show progress container
    progressContainer.classList.remove('hidden');
    updateProgress(0, selectedFiles.length);
    
    // Show results section immediately for streaming
    resultsSection.classList.remove('hidden');
    
    try {
        const response = await fetch('/api/transform-stream-v2', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Transform failed: ${response.statusText}`);
        }
        
        // Handle the streaming response directly
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    handleStreamingEvent(data);
                }
            }
        }
        
    } catch (error) {
        console.error('Streaming error:', error);
        showError(`Failed to transform files: ${error.message}`);
    } finally {
        processingStatus.classList.add('hidden');
        analysisOptions.classList.remove('hidden');
    }
}

// Handle streaming events
function handleStreamingEvent(data) {
    switch (data.type) {
        case 'init':
            // Initialize table with model fields
            modelFields = data.model_fields || [];
            if (currentView === 'table') {
                initializeTable(modelFields);
            }
            break;
            
        case 'progress':
            // Update progress bar
            updateProgress(data.current, data.total);
            break;
            
        case 'result':
            // Add result to table or file view
            streamingResults.push(data);
            if (data.status === 'success') {
                if (currentView === 'table') {
                    addTableRow(data);
                } else {
                    addFileResult(data);
                }
            }
            // Update progress from result
            if (data.progress) {
                updateProgress(data.progress.current, data.progress.total);
                updateSummaryStats(data.progress);
            }
            break;
            
        case 'complete':
            // Transform complete
            transformResults = {
                model_used: data.model_used,
                ai_model_used: data.ai_model_used,
                total_files: data.total_files,
                successful: data.successful,
                failed: data.failed,
                results: streamingResults.map(r => ({
                    filename: r.filename,
                    status: r.status,
                    structured_data: r.structured_data,
                    error: r.error
                }))
            };
            showToast('Transformation complete!', 'success');
            break;
    }
}

// Initialize table with headers
function initializeTable(fields) {
    const tableHeader = document.getElementById('tableHeader');
    const tableBody = document.getElementById('tableBody');
    
    // Clear existing content
    tableHeader.innerHTML = '';
    tableBody.innerHTML = '';
    
    // Ensure fields is an array
    if (!Array.isArray(fields)) {
        console.error('Expected fields to be an array, got:', fields);
        fields = [];
    }
    
    // Create header row
    const headerRow = document.createElement('tr');
    
    // Filename column
    const filenameHeader = document.createElement('th');
    filenameHeader.textContent = 'Filename';
    filenameHeader.className = 'sortable';
    filenameHeader.dataset.column = 'filename';
    filenameHeader.addEventListener('click', () => handleSort('filename'));
    headerRow.appendChild(filenameHeader);
    
    // Dynamic field columns
    fields.forEach(field => {
        const th = document.createElement('th');
        th.textContent = formatFieldName(field);
        th.className = 'sortable';
        th.dataset.column = field;
        th.addEventListener('click', () => handleSort(field));
        headerRow.appendChild(th);
    });
    
    tableHeader.appendChild(headerRow);
}

// Handle column sorting
function handleSort(column) {
    // Update sort state
    if (sortState.column === column) {
        // Toggle direction
        if (sortState.direction === 'asc') {
            sortState.direction = 'desc';
        } else if (sortState.direction === 'desc') {
            sortState.direction = null;
            sortState.column = null;
        } else {
            sortState.direction = 'asc';
        }
    } else {
        sortState.column = column;
        sortState.direction = 'asc';
    }
    
    // Update header classes
    document.querySelectorAll('#tableHeader th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        if (th.dataset.column === sortState.column) {
            if (sortState.direction === 'asc') {
                th.classList.add('sort-asc');
            } else if (sortState.direction === 'desc') {
                th.classList.add('sort-desc');
            }
        }
    });
    
    // Re-render the table with sorted data
    renderSortedTable();
}

// Render sorted table
function renderSortedTable() {
    const tableBody = document.getElementById('tableBody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    if (sortState.column && sortState.direction) {
        rows.sort((a, b) => {
            let aValue, bValue;
            
            if (sortState.column === 'filename') {
                aValue = a.querySelector('.filename-cell').textContent;
                bValue = b.querySelector('.filename-cell').textContent;
            } else {
                const aCell = a.querySelector(`[data-field="${sortState.column}"]`);
                const bCell = b.querySelector(`[data-field="${sortState.column}"]`);
                aValue = aCell ? aCell.textContent : '';
                bValue = bCell ? bCell.textContent : '';
            }
            
            // Handle numeric values
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return sortState.direction === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // Handle string values
            const comparison = aValue.localeCompare(bValue);
            return sortState.direction === 'asc' ? comparison : -comparison;
        });
    }
    
    // Clear and re-append sorted rows
    tableBody.innerHTML = '';
    rows.forEach(row => tableBody.appendChild(row));
}

// Add a row to the table
function addTableRow(result) {
    const tableBody = document.getElementById('tableBody');
    const row = document.createElement('tr');
    row.dataset.filename = result.filename;
    
    // Filename cell
    const filenameCell = document.createElement('td');
    filenameCell.className = 'filename-cell';
    filenameCell.textContent = result.filename;
    row.appendChild(filenameCell);
    
    // Data cells
    if (result.status === 'success' && result.structured_data) {
        modelFields.forEach(field => {
            const cell = document.createElement('td');
            cell.dataset.field = field;
            const value = getEditedValue(result.filename, field) ?? result.structured_data[field];
            
            // Make cell editable
            cell.className = 'cell-editable';
            cell.addEventListener('dblclick', () => makeEditable(cell, result.filename, field, value));
            
            renderCellValue(cell, value);
            row.appendChild(cell);
        });
    } else {
        // Error row
        const errorCell = document.createElement('td');
        errorCell.colSpan = modelFields.length;
        errorCell.textContent = result.error || 'Failed';
        errorCell.className = 'text-red-600';
        row.appendChild(errorCell);
    }
    
    tableBody.appendChild(row);
}

// Get edited value if exists
function getEditedValue(filename, field) {
    return editedData[`${filename}_${field}`];
}

// Make cell editable
function makeEditable(cell, filename, field, originalValue) {
    if (cell.classList.contains('cell-editing')) return;
    
    cell.classList.add('cell-editing');
    const currentValue = getEditedValue(filename, field) ?? originalValue;
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'cell-input';
    input.value = Array.isArray(currentValue) ? currentValue.join(', ') : String(currentValue || '');
    
    // Handle save on blur or enter
    const saveEdit = () => {
        const newValue = input.value.trim();
        if (newValue !== String(currentValue || '')) {
            saveEditedValue(filename, field, newValue);
            showToast('Value updated', 'success');
        }
        cell.classList.remove('cell-editing');
        renderCellValue(cell, newValue || originalValue);
    };
    
    // Handle cancel on escape
    const cancelEdit = () => {
        cell.classList.remove('cell-editing');
        renderCellValue(cell, currentValue);
    };
    
    input.addEventListener('blur', saveEdit);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveEdit();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            input.removeEventListener('blur', saveEdit);
            cancelEdit();
        }
    });
    
    cell.innerHTML = '';
    cell.appendChild(input);
    input.focus();
    input.select();
}

// Save edited value
function saveEditedValue(filename, field, value) {
    const key = `${filename}_${field}`;
    editedData[key] = value;
    
    // Mark row as edited
    const row = document.querySelector(`tr[data-filename="${filename}"]`);
    if (row) {
        row.classList.add('edited');
    }
    
    // Show clear edits button
    if (Object.keys(editedData).length > 0) {
        clearEditsBtn?.classList.remove('hidden');
    }
}

// Clear all edits
function clearAllEdits() {
    editedData = {};
    
    // Remove edited class from all rows
    document.querySelectorAll('tr.edited').forEach(row => {
        row.classList.remove('edited');
    });
    
    // Re-render table to show original values
    if (transformResults) {
        displayResults(transformResults);
    }
    
    clearEditsBtn?.classList.add('hidden');
    showToast('All edits cleared', 'info');
}

// Render cell value
function renderCellValue(cell, value) {
    cell.innerHTML = '';
    
    if (value === undefined || value === null || value === '') {
        cell.textContent = '—';
        cell.className = 'cell-editable text-gray-400';
    } else if (typeof value === 'boolean') {
        cell.textContent = value ? '✓' : '✗';
        cell.className = `cell-editable ${value ? 'boolean-true' : 'boolean-false'}`;
    } else if (Array.isArray(value)) {
        cell.className = 'cell-editable list-cell';
        value.forEach(item => {
            const span = document.createElement('span');
            span.className = 'list-item';
            span.textContent = item;
            cell.appendChild(span);
        });
    } else {
        cell.textContent = String(value);
        cell.className = 'cell-editable';
        if (String(value).length > 50) {
            cell.classList.add('cell-tooltip');
            cell.setAttribute('data-tooltip', String(value));
            cell.textContent = String(value).substring(0, 47) + '...';
        }
    }
}

// Search functionality
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
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

// Highlight search term in row
function highlightSearchTerm(row, term) {
    row.querySelectorAll('td').forEach(cell => {
        if (cell.classList.contains('cell-editing')) return;
        
        const text = cell.textContent;
        const regex = new RegExp(`(${term})`, 'gi');
        if (regex.test(text)) {
            cell.innerHTML = text.replace(regex, '<span class="search-highlight">$1</span>');
        }
    });
}

// Remove search highlights
function removeHighlights(row) {
    row.querySelectorAll('.search-highlight').forEach(span => {
        span.replaceWith(span.textContent);
    });
}

// Add result to file view
function addFileResult(result) {
    const structuredResults = document.getElementById('structuredResults');
    
    if (result.status === 'success' && result.structured_data) {
        const resultItem = createResultItem(result.filename, result.structured_data);
        structuredResults.appendChild(resultItem);
    } else {
        const errorItem = createErrorItem(result.filename, result.error);
        structuredResults.appendChild(errorItem);
    }
}

// Update summary statistics
function updateSummaryStats(progress) {
    document.getElementById('totalFiles').textContent = progress.total;
    document.getElementById('successfulFiles').textContent = progress.successful;
    document.getElementById('failedFiles').textContent = progress.failed;
    
    if (progress.total > 1) {
        document.getElementById('resultsSummary').classList.remove('hidden');
    }
}

// Display results
function displayResults(data) {
    resultsSection.classList.remove('hidden');
    
    // Update summary if multiple files
    if (data.total_files > 1) {
        resultsSummary.classList.remove('hidden');
        document.getElementById('totalFiles').textContent = data.total_files;
        document.getElementById('successfulFiles').textContent = data.successful;
        document.getElementById('failedFiles').textContent = data.failed;
        
        // Display summary content
        if (data.summary) {
            const summaryContent = document.getElementById('summaryContent');
            summaryContent.innerHTML = formatSummary(data.summary);
        }
    } else {
        resultsSummary.classList.add('hidden');
    }
    
    if (currentView === 'table') {
        // Display table view
        displayTableView(data);
    } else {
        // Display file view
        displayFileView(data);
    }
}

// Display table view
function displayTableView(data) {
    // Get model fields from first successful result
    const firstSuccess = data.results.find(r => r.status === 'success' && r.structured_data);
    if (firstSuccess) {
        modelFields = Object.keys(firstSuccess.structured_data);
        initializeTable(modelFields);
        
        // Add all results to table
        data.results.forEach(result => {
            addTableRow({
                filename: result.filename,
                status: result.status,
                structured_data: result.structured_data,
                error: result.error
            });
        });
        
        // Apply any existing edits
        Object.keys(editedData).forEach(key => {
            const [filename, field] = key.split('_');
            const row = document.querySelector(`tr[data-filename="${filename}"]`);
            if (row) {
                row.classList.add('edited');
                const cell = row.querySelector(`td[data-field="${field}"]`);
                if (cell) {
                    renderCellValue(cell, editedData[key]);
                }
            }
        });
        
        // Show clear edits button if there are edits
        if (Object.keys(editedData).length > 0) {
            clearEditsBtn?.classList.remove('hidden');
        }
    }
}

// Display file view
function displayFileView(data) {
    const structuredResults = document.getElementById('structuredResults');
    structuredResults.innerHTML = '';
    
    for (const result of data.results) {
        if (result.status === 'success' && result.structured_data) {
            const resultItem = createResultItem(result.filename, result.structured_data);
            structuredResults.appendChild(resultItem);
        } else if (result.status === 'error') {
            const errorItem = createErrorItem(result.filename, result.error);
            structuredResults.appendChild(errorItem);
        }
    }
}

// Create result item element
function createResultItem(filename, data) {
    const item = document.createElement('div');
    item.className = 'result-card';
    
    const title = document.createElement('h4');
    title.textContent = filename;
    item.appendChild(title);
    
    for (const [key, value] of Object.entries(data)) {
        const field = document.createElement('div');
        field.className = 'result-field';
        
        const fieldName = document.createElement('span');
        fieldName.className = 'field-name';
        fieldName.textContent = formatFieldName(key) + ':';
        field.appendChild(fieldName);
        
        const fieldValue = document.createElement('span');
        fieldValue.className = 'field-value';
        
        // Check for edited value
        const editedValue = getEditedValue(filename, key);
        const displayValue = editedValue ?? value;
        
        if (Array.isArray(displayValue)) {
            fieldValue.className += ' list';
            displayValue.forEach(item => {
                const span = document.createElement('span');
                span.textContent = item;
                fieldValue.appendChild(span);
            });
        } else if (typeof displayValue === 'boolean') {
            fieldValue.textContent = displayValue ? '✓ Yes' : '✗ No';
            fieldValue.className = displayValue ? 'field-value text-green-600' : 'field-value text-red-600';
        } else {
            fieldValue.textContent = displayValue || 'N/A';
        }
        
        field.appendChild(fieldValue);
        item.appendChild(field);
    }
    
    return item;
}

// Create error item element
function createErrorItem(filename, error) {
    const item = document.createElement('div');
    item.className = 'result-card error';
    
    const title = document.createElement('h4');
    title.textContent = filename + ' (Failed)';
    title.className = 'text-red-600';
    item.appendChild(title);
    
    const errorText = document.createElement('p');
    errorText.textContent = error;
    errorText.className = 'text-sm text-red-600';
    item.appendChild(errorText);
    
    return item;
}

// Format field name for display
function formatFieldName(name) {
    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

// Format summary data
function formatSummary(summary) {
    let html = '';
    
    for (const [key, value] of Object.entries(summary)) {
        if (key === 'total_analyzed') continue;
        
        html += `<p><strong>${formatFieldName(key)}:</strong> `;
        
        if (Array.isArray(value)) {
            html += value.join(', ');
        } else if (typeof value === 'number') {
            html += value.toFixed(2);
        } else {
            html += value;
        }
        
        html += '</p>';
    }
    
    return html;
}

// Handle download button click
async function handleDownload() {
    const formatSelect = document.getElementById('downloadFormat');
    const format = formatSelect ? formatSelect.value : 'excel';
    await downloadResults(format);
}

// Download results
async function downloadResults(format) {
    if (!transformResults) return;
    
    // Include edited data in the download
    const resultsWithEdits = {
        ...transformResults,
        results: transformResults.results.map(result => {
            if (result.status === 'success' && result.structured_data) {
                const editedStructuredData = { ...result.structured_data };
                
                // Apply any edits
                Object.keys(editedData).forEach(key => {
                    const [filename, field] = key.split('_');
                    if (filename === result.filename) {
                        editedStructuredData[field] = editedData[key];
                    }
                });
                
                return {
                    ...result,
                    structured_data: editedStructuredData
                };
            }
            return result;
        })
    };
    
    try {
        if (format === 'csv') {
            // Client-side CSV generation
            const content = convertToCSV(resultsWithEdits);
            const filename = `transform_results_${new Date().toISOString().slice(0, 10)}.csv`;
            const blob = new Blob([content], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('CSV downloaded successfully', 'success');
        } else if (format === 'excel') {
            // Server-side Excel generation
            const response = await fetch('/api/download-results', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    results: resultsWithEdits,
                    format: 'excel'
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate Excel file');
            }
            
            const blob = await response.blob();
            const filename = `transform_results_${new Date().toISOString().slice(0, 10)}.xlsx`;
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('Excel downloaded successfully', 'success');
        }
    } catch (error) {
        console.error('Download error:', error);
        showError('Failed to download results');
    }
}

// Convert results to CSV
function convertToCSV(data) {
    const results = data.results.filter(r => r.status === 'success' && r.structured_data);
    
    if (results.length === 0) {
        return 'No successful results to export';
    }
    
    // Get all unique keys
    const allKeys = new Set(['filename']);
    results.forEach(r => {
        Object.keys(r.structured_data).forEach(key => allKeys.add(key));
    });
    
    const headers = Array.from(allKeys);
    const rows = [headers.join(',')];
    
    // Add data rows
    results.forEach(result => {
        const row = headers.map(header => {
            if (header === 'filename') {
                return result.filename;
            }
            const value = result.structured_data[header];
            if (value === undefined || value === null) {
                return '';
            }
            if (Array.isArray(value)) {
                return `"${value.join('; ')}"`;
            }
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        rows.push(row.join(','));
    });
    
    return rows.join('\n');
}

// Update progress
function updateProgress(current, total) {
    const percentage = (current / total) * 100;
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${current} / ${total} files`;
}

// Show error message
function showError(message) {
    errorDisplay.classList.remove('hidden');
    errorDisplay.querySelector('.error-message').textContent = message;
    processingStatus.classList.add('hidden');
}

// Clear error message
function clearError() {
    errorDisplay.classList.add('hidden');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = document.createElement('div');
    icon.className = 'flex-shrink-0';
    
    // Set icon based on type
    let iconSvg = '';
    switch (type) {
        case 'success':
            iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>';
            break;
        case 'error':
            iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>';
            break;
        case 'warning':
            iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>';
            break;
        default:
            iconSvg = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>';
    }
    
    icon.innerHTML = iconSvg;
    toast.appendChild(icon);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'ml-3 text-sm font-medium';
    messageDiv.textContent = message;
    toast.appendChild(messageDiv);
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex h-8 w-8 hover:bg-gray-100 hover:bg-opacity-25 focus:outline-none focus:ring-2 focus:ring-gray-300';
    closeBtn.innerHTML = '<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>';
    closeBtn.addEventListener('click', () => removeToast(toast));
    toast.appendChild(closeBtn);
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => removeToast(toast), 5000);
}

// Remove toast notification
function removeToast(toast) {
    toast.classList.add('fade-out');
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300);
}
