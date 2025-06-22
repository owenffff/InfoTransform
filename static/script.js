// Information Transformer JavaScript

// Global variables
let selectedFiles = [];
let transformResults = null;
let currentView = 'table'; // Default to table view
let eventSource = null;
let streamingResults = [];
let modelFields = [];

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
    document.getElementById('downloadCsvBtn')?.addEventListener('click', () => downloadResults('csv'));
    
    // View toggle buttons
    document.getElementById('tableViewBtn')?.addEventListener('click', () => switchView('table'));
    document.getElementById('fileViewBtn')?.addEventListener('click', () => switchView('file'));
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
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
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
    }
}

// Model selection
function handleModelChange(e) {
    const selectedOption = e.target.selectedOptions[0];
    if (selectedOption && selectedOption.dataset.description) {
        modelDescription.textContent = selectedOption.dataset.description;
        modelDescription.style.display = 'block';
    } else {
        modelDescription.style.display = 'none';
    }
}

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
    
    // Use streaming for multiple files
    if (selectedFiles.length > 1) {
        await handleStreamingTransform();
    } else {
        await handleSingleTransform();
    }
}

// Handle single file transform (non-streaming)
async function handleSingleTransform() {
    const formData = new FormData();
    formData.append('file', selectedFiles[0]);
    formData.append('model_key', modelSelect.value);
    formData.append('custom_instructions', customInstructions.value || '');
    if (aiModelSelect.value) {
        formData.append('ai_model', aiModelSelect.value);
    }
    
    try {
        const response = await fetch('/api/transform', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            let errorDetail = '';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || JSON.stringify(errorData);
            } catch (e) {
                errorDetail = await response.text();
            }
            throw new Error(`Transform failed: ${errorDetail}`);
        }
        
        const data = await response.json();
        transformResults = data;
        displayResults(data);
        
    } catch (error) {
        console.error('Transform error:', error);
        showError(`Failed to transform file: ${error.message}`);
    } finally {
        processingStatus.classList.add('hidden');
        analysisOptions.classList.remove('hidden');
    }
}

// Handle streaming transform for multiple files
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
        const response = await fetch('/api/transform-stream', {
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
    
    // Create header row
    const headerRow = document.createElement('tr');
    
    // Filename column
    const filenameHeader = document.createElement('th');
    filenameHeader.textContent = 'Filename';
    filenameHeader.className = 'sortable';
    headerRow.appendChild(filenameHeader);
    
    // Dynamic field columns
    fields.forEach(field => {
        const th = document.createElement('th');
        th.textContent = formatFieldName(field);
        th.className = 'sortable';
        th.dataset.field = field;
        headerRow.appendChild(th);
    });
    
    tableHeader.appendChild(headerRow);
}

// Add a row to the table
function addTableRow(result) {
    const tableBody = document.getElementById('tableBody');
    const row = document.createElement('tr');
    
    // Filename cell
    const filenameCell = document.createElement('td');
    filenameCell.className = 'filename-cell';
    filenameCell.textContent = result.filename;
    row.appendChild(filenameCell);
    
    // Data cells
    if (result.status === 'success' && result.structured_data) {
        modelFields.forEach(field => {
            const cell = document.createElement('td');
            const value = result.structured_data[field];
            
            if (value === undefined || value === null) {
                cell.textContent = '—';
                cell.style.color = '#bdc3c7';
            } else if (typeof value === 'boolean') {
                cell.textContent = value ? '✓' : '✗';
                cell.className = value ? 'boolean-true' : 'boolean-false';
            } else if (Array.isArray(value)) {
                cell.className = 'list-cell';
                value.forEach(item => {
                    const span = document.createElement('span');
                    span.className = 'list-item';
                    span.textContent = item;
                    cell.appendChild(span);
                });
            } else {
                cell.textContent = String(value);
                if (String(value).length > 50) {
                    cell.className = 'cell-tooltip';
                    cell.setAttribute('data-tooltip', String(value));
                    cell.textContent = String(value).substring(0, 47) + '...';
                }
            }
            
            row.appendChild(cell);
        });
    } else {
        // Error row
        const errorCell = document.createElement('td');
        errorCell.colSpan = modelFields.length;
        errorCell.textContent = result.error || 'Failed';
        errorCell.style.color = '#e74c3c';
        row.appendChild(errorCell);
    }
    
    tableBody.appendChild(row);
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
    item.className = 'result-item';
    
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
        
        if (Array.isArray(value)) {
            fieldValue.className += ' list';
            value.forEach(item => {
                const span = document.createElement('span');
                span.textContent = item;
                fieldValue.appendChild(span);
            });
        } else if (typeof value === 'boolean') {
            fieldValue.textContent = value ? '✓ Yes' : '✗ No';
            fieldValue.style.color = value ? '#27ae60' : '#e74c3c';
        } else {
            fieldValue.textContent = value || 'N/A';
        }
        
        field.appendChild(fieldValue);
        item.appendChild(field);
    }
    
    return item;
}

// Create error item element
function createErrorItem(filename, error) {
    const item = document.createElement('div');
    item.className = 'result-item error';
    item.style.borderColor = '#e74c3c';
    
    const title = document.createElement('h4');
    title.textContent = filename + ' (Failed)';
    title.style.color = '#e74c3c';
    item.appendChild(title);
    
    const errorText = document.createElement('p');
    errorText.textContent = error;
    errorText.style.color = '#c0392b';
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

// Download results
async function downloadResults(format) {
    if (!transformResults) return;
    
    try {
        let content, filename, mimeType;
        
        if (format === 'csv') {
            content = convertToCSV(transformResults);
            filename = `transform_results_${new Date().toISOString().slice(0, 10)}.csv`;
            mimeType = 'text/csv';
        }
        
        // Create blob and download
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
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
            if (typeof value === 'string' && value.includes(',')) {
                return `"${value}"`;
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
