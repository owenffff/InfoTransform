import * as dom from './dom.js';
import * as state from './state.js';
import { addStreamingResult, setModelFields, setTransformResults } from './state.js';
import { handleSort } from './events.js';

/* ------------------------------------------------------------------ */
/*  Error-rendering helpers & icons                                   */
/* ------------------------------------------------------------------ */
const lockSvg = '<svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 2a4 4 0 00-4 4v2H5a2 2 0 00-2 2v6a4 4 0 004 4h6a4 4 0 004-4v-6a2 2 0 00-2-2h-1V6a4 4 0 00-4-4zm-2 6V6a2 2 0 114 0v2H8z" clip-rule="evenodd"></path></svg>';
const errorSvg = '<svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1-5a1 1 0 112 0 1 1 0 01-2 0zm0-7a1 1 0 012 0v4a1 1 0 11-2 0V6z" clip-rule="evenodd"></path></svg>';

// Default error messages by type
const defaultErrorText = {
    password_required: 'PDF is password-protected.',
    unsupported_format: 'Unsupported file format.',
    corrupt_file: 'File appears to be corrupted.',
    ocr_failure: 'Could not extract text from image.',
    timeout: 'Processing timed out.',
    generic: 'File processing failed.'
};

/** Get user-friendly error message */
function prettyError(result) {
    // Use backend error if provided, otherwise use default based on error_type
    return result.error || defaultErrorText[result.error_type] || defaultErrorText.generic;
}

/** Return first sentence or whole string if no period */
function formatErrorMessage(msg = 'Failed') {
    const trimmed = String(msg).trim();
    const idx = trimmed.indexOf('.');
    return idx > 0 ? trimmed.slice(0, idx + 1) : trimmed;
}

// View switching
export function switchView(view) {
    state.setCurrentView(view);
    localStorage.setItem('preferredView', view);
    updateViewToggle();
    
    // Re-display results in the new view if we have them
    if (state.transformResults) {
        displayResults(state.transformResults);
    }
}

export function updateViewToggle() {
    const tableBtn = document.getElementById('tableViewBtn');
    const fileBtn = document.getElementById('fileViewBtn');
    const tableView = document.getElementById('tableView');
    const fileView = document.getElementById('fileView');
    
    // Update button states
    if (state.currentView === 'table') {
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

export function showSchemaPreview(modelKey) {
    const schemaPreview = document.getElementById('schemaPreview');
    const chipsContainer = document.getElementById('schemaChipsContainer');
    
    const modelInfo = state.modelsData?.models[modelKey];
    
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
    const fieldType = fieldInfo.type?.toLowerCase() || 'string';
    
    // Apply type-specific styling
    chip.className = `field-chip ${fieldInfo.required ? 'required' : 'optional'}`;
    chip.setAttribute('data-type', fieldType);
    
    // Add icon based on type
    const icon = getFieldTypeIcon(fieldType);
    if (icon) {
        const iconSpan = document.createElement('span');
        iconSpan.innerHTML = icon;
        iconSpan.className = 'text-lg';
        chip.appendChild(iconSpan);
    }
    
    // Chip text
    const chipText = document.createElement('span');
    chipText.textContent = `${fieldName}${!fieldInfo.required ? '?' : ''}`;
    chipText.className = 'font-medium';
    chip.appendChild(chipText);
    
    // Create enhanced popover
    const popover = document.createElement('div');
    popover.className = 'field-details-popover';
    
    const popoverContent = document.createElement('div');
    popoverContent.className = 'field-details-popover-content';
    
    // Header with field name and type badge
    const header = document.createElement('div');
    header.className = 'flex items-center justify-between mb-3';
    header.innerHTML = `
        <h4 class="text-lg font-bold text-gray-900">${fieldName}</h4>
        <span class="px-2 py-1 text-xs font-medium rounded-full ${getTypeBadgeClass(fieldType)}">
            ${fieldType.toUpperCase()}
        </span>
    `;
    popoverContent.appendChild(header);
    
    // Field details
    const details = document.createElement('div');
    details.className = 'space-y-2';
    
    // Required/Optional status
    const requiredStatus = document.createElement('div');
    requiredStatus.className = 'flex items-center gap-2';
    requiredStatus.innerHTML = `
        <span class="text-sm font-medium text-gray-600">Status:</span>
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
            fieldInfo.required 
                ? 'bg-red-100 text-red-800' 
                : 'bg-green-100 text-green-800'
        }">
            ${fieldInfo.required ? 'Required' : 'Optional'}
        </span>
    `;
    details.appendChild(requiredStatus);
    
    // Description if available
    if (fieldInfo.description) {
        const description = document.createElement('div');
        description.className = 'pt-2 border-t border-gray-100';
        description.innerHTML = `
            <p class="text-sm text-gray-700 leading-relaxed">${fieldInfo.description}</p>
        `;
        details.appendChild(description);
    }
    
    // Example values if available
    if (fieldInfo.examples && fieldInfo.examples.length > 0) {
        const examples = document.createElement('div');
        examples.className = 'pt-2 border-t border-gray-100';
        examples.innerHTML = `
            <p class="text-xs font-medium text-gray-600 mb-1">Examples:</p>
            <div class="flex flex-wrap gap-1">
                ${fieldInfo.examples.map(ex => 
                    `<code class="px-2 py-0.5 bg-gray-100 text-gray-800 rounded text-xs">${ex}</code>`
                ).join('')}
            </div>
        `;
        details.appendChild(examples);
    }
    
    // Constraints if available
    if (fieldInfo.constraints) {
        const constraints = document.createElement('div');
        constraints.className = 'pt-2 border-t border-gray-100';
        constraints.innerHTML = `
            <p class="text-xs font-medium text-gray-600 mb-1">Constraints:</p>
            <ul class="text-xs text-gray-700 space-y-0.5">
                ${Object.entries(fieldInfo.constraints).map(([key, value]) => 
                    `<li>• ${formatConstraint(key, value)}</li>`
                ).join('')}
            </ul>
        `;
        details.appendChild(constraints);
    }
    
    popoverContent.appendChild(details);
    popover.appendChild(popoverContent);
    chip.appendChild(popover);
    
    // Enhanced interaction behavior
    let hoverTimeout;
    
    const showPopover = () => {
        clearTimeout(hoverTimeout);
        // Position popover to avoid going off-screen
        const chipRect = chip.getBoundingClientRect();
        const popoverRect = popover.getBoundingClientRect();
        
        // Adjust horizontal position if needed
        if (chipRect.left + popoverRect.width / 2 > window.innerWidth - 20) {
            popover.style.left = 'auto';
            popover.style.right = '0';
            popover.style.transform = 'translateX(0)';
        } else if (chipRect.left - popoverRect.width / 2 < 20) {
            popover.style.left = '0';
            popover.style.right = 'auto';
            popover.style.transform = 'translateX(0)';
        }
        
        popover.classList.remove('hidden');
    };

    const hidePopover = () => {
        if (!chip.classList.contains('active')) {
            hoverTimeout = setTimeout(() => {
                popover.classList.add('hidden');
            }, 200);
        }
    };

    // Enhanced hover behavior
    chip.addEventListener('mouseenter', showPopover);
    chip.addEventListener('mouseleave', (e) => {
        if (!popover.contains(e.relatedTarget)) {
            hidePopover();
        }
    });
    
    popover.addEventListener('mouseenter', () => {
        clearTimeout(hoverTimeout);
    });
    
    popover.addEventListener('mouseleave', (e) => {
        if (!chip.contains(e.relatedTarget)) {
            hidePopover();
        }
    });
    
    // Click to pin/unpin
    chip.addEventListener('click', (e) => {
        e.stopPropagation();
        // Close any other pinned chip
        document.querySelectorAll('.field-chip.active').forEach(c => {
            if (c !== chip) {
                c.classList.remove('active');
            }
        });
        // Toggle active state
        chip.classList.toggle('active');
        if (chip.classList.contains('active')) {
            showPopover();
        }
    });
    
    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!chip.contains(e.target) && !popover.contains(e.target)) {
            chip.classList.remove('active');
            popover.classList.add('hidden');
        }
    });
    
    return chip;
}

// Helper function to get icon for field type
function getFieldTypeIcon(type) {
    // Return empty string - no icons
    return '';
}

// Helper function to get type badge class
function getTypeBadgeClass(type) {
    const classes = {
        'string': 'bg-emerald-100 text-emerald-800',
        'number': 'bg-purple-100 text-purple-800',
        'boolean': 'bg-amber-100 text-amber-800',
        'array': 'bg-pink-100 text-pink-800',
        'object': 'bg-indigo-100 text-indigo-800'
    };
    return classes[type] || 'bg-gray-100 text-gray-800';
}

// Helper function to format constraints
function formatConstraint(key, value) {
    const formatters = {
        'minLength': (v) => `Minimum length: ${v}`,
        'maxLength': (v) => `Maximum length: ${v}`,
        'min': (v) => `Minimum value: ${v}`,
        'max': (v) => `Maximum value: ${v}`,
        'pattern': (v) => `Pattern: ${v}`,
        'enum': (v) => `Allowed values: ${v.join(', ')}`
    };
    return formatters[key] ? formatters[key](value) : `${key}: ${value}`;
}

// Handle streaming events
export function handleStreamingEvent(data) {
    switch (data.type) {
        case 'init':
            // Initialize table with model fields
            setModelFields(data.model_fields || []);
            if (state.currentView === 'table') {
                initializeTable(state.modelFields);
            }
            break;
            
        case 'progress':
            // Update progress bar
            updateProgress(data.current, data.total);
            break;
            
        case 'result':
            // Store result
            addStreamingResult(data);

            // Render in whichever view is active (helpers handle success vs error)
            if (state.currentView === 'table') {
                addTableRow(data);
            } else {
                addFileResult(data);
            }

            // Update progress from result
            if (data.progress) {
                updateProgress(data.progress.current, data.progress.total);
                updateSummaryStats(data.progress);
            }
            break;
            
        case 'conversion_summary':
            if (data.password_required && data.password_required.length) {
                showToast(
                    `Failed to process password-protected PDFs: ${data.password_required.join(', ')}`,
                    'error'
                );
            }
            break;

        case 'complete':
            // Transform complete
            setTransformResults({
                model_used: data.model_used,
                ai_model_used: data.ai_model_used,
                total_files: data.total_files,
                successful: data.successful,
                failed: data.failed,
                results: state.streamingResults.map(r => ({
                    filename: r.filename,
                    status: r.status,
                    structured_data: r.structured_data,
                    error: r.error
                }))
            });
            showToast('Transformation complete!', 'success');
            break;
    }
}

// Initialize table with headers
export function initializeTable(fields) {
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
    filenameHeader.innerHTML = '<span class="inline-flex items-center gap-2">Filename</span>';
    filenameHeader.className = 'sortable';
    filenameHeader.dataset.column = 'filename';
    filenameHeader.addEventListener('click', () => handleSort('filename'));
    headerRow.appendChild(filenameHeader);
    
    // Dynamic field columns
    fields.forEach(field => {
        const th = document.createElement('th');
        th.innerHTML = `<span class="inline-flex items-center gap-1">${formatFieldName(field)}</span>`;
        th.className = 'sortable';
        th.dataset.column = field;
        th.addEventListener('click', () => handleSort(field));
        headerRow.appendChild(th);
    });
    
    tableHeader.appendChild(headerRow);
}

// Render sorted table
export function renderSortedTable() {
    const tableBody = document.getElementById('tableBody');
    const rows = Array.from(tableBody.querySelectorAll('tr'));
    
    if (state.sortState.column && state.sortState.direction) {
        rows.sort((a, b) => {
            let aValue, bValue;
            
            if (state.sortState.column === 'filename') {
                aValue = a.querySelector('.filename-cell').textContent;
                bValue = b.querySelector('.filename-cell').textContent;
            } else {
                const aCell = a.querySelector(`[data-field="${state.sortState.column}"]`);
                const bCell = b.querySelector(`[data-field="${state.sortState.column}"]`);
                aValue = aCell ? aCell.textContent : '';
                bValue = bCell ? bCell.textContent : '';
            }
            
            // Handle numeric values
            const aNum = parseFloat(aValue);
            const bNum = parseFloat(bValue);
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return state.sortState.direction === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // Handle string values
            const comparison = aValue.localeCompare(bValue);
            return state.sortState.direction === 'asc' ? comparison : -comparison;
        });
    }
    
    // Clear and re-append sorted rows
    tableBody.innerHTML = '';
    rows.forEach(row => tableBody.appendChild(row));
}

// Add a row to the table
export function addTableRow(result) {
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
        state.modelFields.forEach(field => {
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
        // Error row - style nicely
        row.classList.add('bg-red-50');
        const errorCell = document.createElement('td');
        errorCell.colSpan = state.modelFields.length + 1; // span all columns
        errorCell.innerHTML = `
            <span class="inline-flex items-center gap-2 text-red-600">
                ${result.error_type === 'password_required' ? lockSvg : errorSvg}
                ${formatErrorMessage(prettyError(result))}
            </span>`;
        row.appendChild(errorCell);
    }
    
    tableBody.appendChild(row);
}

// Get edited value if exists
function getEditedValue(filename, field) {
    return state.editedData[`${filename}_${field}`];
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
    state.updateEditedData(key, value);
    
    // Mark row as edited
    const row = document.querySelector(`tr[data-filename="${filename}"]`);
    if (row) {
        row.classList.add('edited');
    }
    
    // Show clear edits button
    if (Object.keys(state.editedData).length > 0) {
        dom.clearEditsBtn?.classList.remove('hidden');
    }
}

// Clear all edits
export function clearAllEdits() {
    state.setEditedData({});
    
    // Remove edited class from all rows
    document.querySelectorAll('tr.edited').forEach(row => {
        row.classList.remove('edited');
    });
    
    // Re-render table to show original values
    if (state.transformResults) {
        displayResults(state.transformResults);
    }
    
    dom.clearEditsBtn?.classList.add('hidden');
    showToast('All edits cleared', 'info');
}

// Render cell value
function renderCellValue(cell, value) {
    cell.innerHTML = '';
    
    if (value === undefined || value === null || value === '') {
        cell.textContent = '—';
        cell.className = 'cell-editable text-gray-400';
    } else if (typeof value === 'boolean') {
        cell.textContent = value ? 'Yes' : 'No';
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

// Highlight search term in row
export function highlightSearchTerm(row, term) {
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
export function removeHighlights(row) {
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
export function displayResults(data) {
    dom.resultsSection.classList.remove('hidden');
    
    // Update summary if multiple files
    if (data.total_files > 1) {
        dom.resultsSummary.classList.remove('hidden');
        document.getElementById('totalFiles').textContent = data.total_files;
        document.getElementById('successfulFiles').textContent = data.successful;
        document.getElementById('failedFiles').textContent = data.failed;
        
        // Display summary content
        if (data.summary) {
            const summaryContent = document.getElementById('summaryContent');
            summaryContent.innerHTML = formatSummary(data.summary);
        }
    } else {
        dom.resultsSummary.classList.add('hidden');
    }
    
    if (state.currentView === 'table') {
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
        setModelFields(Object.keys(firstSuccess.structured_data));
        initializeTable(state.modelFields);
        
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
        Object.keys(state.editedData).forEach(key => {
            const [filename, field] = key.split('_');
            const row = document.querySelector(`tr[data-filename="${filename}"]`);
            if (row) {
                row.classList.add('edited');
                const cell = row.querySelector(`td[data-field="${field}"]`);
                if (cell) {
                    renderCellValue(cell, state.editedData[key]);
                }
            }
        });
        
        // Show clear edits button if there are edits
        if (Object.keys(state.editedData).length > 0) {
            dom.clearEditsBtn?.classList.remove('hidden');
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
            fieldValue.textContent = displayValue ? 'Yes' : 'No';
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
    
    // Decide icon and message
    const iconSpan = document.createElement('span');
    iconSpan.innerHTML = error?.toLowerCase().includes('password') ? lockSvg : errorSvg;
    item.prepend(iconSpan);

    const errorText = document.createElement('p');
    errorText.textContent = formatErrorMessage(prettyError({error, error_type: error?.toLowerCase().includes('password') ? 'password_required' : 'generic'}));
    errorText.className = 'text-sm text-red-600 mt-2';
    item.appendChild(errorText);

    item.classList.add('border', 'border-red-300', 'bg-red-50');
    
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

// Convert results to CSV
export function convertToCSV(data) {
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
export function updateProgress(current, total) {
    const percentage = (current / total) * 100;
    dom.progressBar.style.width = `${percentage}%`;
    dom.progressText.textContent = `${current} / ${total} files`;
}

// Show error message
export function showError(message) {
    dom.errorDisplay.classList.remove('hidden');
    dom.errorDisplay.querySelector('.error-message').textContent = message;
    dom.processingStatus.classList.add('hidden');
}

// Clear error message
export function clearError() {
    dom.errorDisplay.classList.add('hidden');
}

// Show toast notification
export function showToast(message, type = 'info') {
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
    
    dom.toastContainer.appendChild(toast);
    
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
