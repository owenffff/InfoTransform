// Information Transformer JavaScript

// Global variables
let selectedFiles = [];
let transformResults = null;

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
    
    // Download buttons
    document.getElementById('downloadJsonBtn')?.addEventListener('click', () => downloadResults('json'));
    document.getElementById('downloadCsvBtn')?.addEventListener('click', () => downloadResults('csv'));
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => switchTab(e.target.dataset.tab));
    });
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
    
    // Prepare form data
    const formData = new FormData();
    
    // Determine endpoint based on file count
    const endpoint = selectedFiles.length === 1 ? '/api/transform' : '/api/transform-batch';
    
    // Add files - use 'file' for single, 'files' for batch
    if (selectedFiles.length === 1) {
        formData.append('file', selectedFiles[0]);
    } else {
        for (const file of selectedFiles) {
            formData.append('files', file);
        }
    }
    
    // Add analysis options
    console.log('Model key:', modelSelect.value);
    console.log('Custom instructions:', customInstructions.value);
    console.log('AI model:', aiModelSelect.value);
    
    formData.append('model_key', modelSelect.value);
    formData.append('custom_instructions', customInstructions.value || '');
    if (aiModelSelect.value) {
        formData.append('ai_model', aiModelSelect.value);
    }
    
    // Log FormData entries
    console.log('FormData entries:');
    for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
            console.log(`  ${key}: File(${value.name}, ${value.size} bytes)`);
        } else {
            console.log(`  ${key}: ${value}`);
        }
    }
    
    try {
        // DEBUG: First send to debug endpoint
        console.log('Sending to debug endpoint...');
        const debugResponse = await fetch('/api/debug-form', {
            method: 'POST',
            body: formData
        });
        console.log('Debug response status:', debugResponse.status);
        const debugData = await debugResponse.json();
        console.log('Debug form data:', debugData);
        
        // DEBUG: Test with simplified endpoint
        if (selectedFiles.length === 1) {
            console.log('Testing with simplified endpoint...');
            const testFormData = new FormData();
            testFormData.append('file', selectedFiles[0]);
            testFormData.append('model_key', modelSelect.value);
            
            const testResponse = await fetch('/api/test-transform', {
                method: 'POST',
                body: testFormData
            });
            console.log('Test endpoint status:', testResponse.status);
            if (testResponse.ok) {
                const testData = await testResponse.json();
                console.log('Test endpoint success:', testData);
            } else {
                const errorText = await testResponse.text();
                console.log('Test endpoint error:', errorText);
            }
        }
        
        // Show progress for batch processing
        if (selectedFiles.length > 1) {
            progressContainer.classList.remove('hidden');
            updateProgress(0, selectedFiles.length);
        }
        
        console.log(`Sending to ${endpoint}...`);
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            // Try to get error details
            let errorDetail = '';
            try {
                const errorData = await response.json();
                console.error('Error response:', errorData);
                errorDetail = JSON.stringify(errorData);
            } catch (e) {
                errorDetail = await response.text();
            }
            throw new Error(`HTTP error! status: ${response.status}, detail: ${errorDetail}`);
        }
        
        const data = await response.json();
        transformResults = data;
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Transform error:', error);
        showError(`Failed to transform files: ${error.message}`);
    } finally {
        processingStatus.classList.add('hidden');
        analysisOptions.classList.remove('hidden');
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
    
    // Display structured results
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
    
    // Display raw JSON
    const rawResults = document.getElementById('rawResults');
    rawResults.textContent = JSON.stringify(data, null, 2);
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

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === `${tabName}Tab`);
    });
}

// Download results
async function downloadResults(format) {
    if (!transformResults) return;
    
    try {
        let content, filename, mimeType;
        
        if (format === 'json') {
            content = JSON.stringify(transformResults, null, 2);
            filename = `transform_results_${new Date().toISOString().slice(0, 10)}.json`;
            mimeType = 'application/json';
        } else if (format === 'csv') {
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
