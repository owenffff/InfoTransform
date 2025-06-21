// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const processingStatus = document.getElementById('processingStatus');
const processingText = document.getElementById('processingText');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultContent = document.getElementById('resultContent');
const downloadBtn = document.getElementById('downloadBtn');
const downloadZipBtn = document.getElementById('downloadZipBtn');
const errorDisplay = document.getElementById('errorDisplay');
const batchSummary = document.getElementById('batchSummary');
const totalFiles = document.getElementById('totalFiles');
const processedFiles = document.getElementById('processedFiles');
const failedFiles = document.getElementById('failedFiles');
const skippedFiles = document.getElementById('skippedFiles');

// State
let currentResult = null;
let isBatchMode = false;
let batchResults = null;

// Event Listeners
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadMarkdown);
downloadZipBtn.addEventListener('click', () => downloadBatch('zip'));

// Drag and Drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFiles(files);
    }
});

// File Handling
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    // Reset UI
    hideError();
    hideResults();
    
    // Check if multiple files or contains ZIP
    if (files.length > 1 || (files.length === 1 && files[0].name.toLowerCase().endsWith('.zip'))) {
        // Batch mode
        isBatchMode = true;
        handleBatchUpload(files);
    } else {
        // Single file mode
        isBatchMode = false;
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // Reset UI
    hideError();
    hideResults();
    
    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showError('File size exceeds 16MB limit');
        return;
    }
    
    // Show processing status
    showProcessing();
    
    // Upload and process file
    uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showResults(result);
        } else {
            showError(result.error || 'Processing failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideProcessing();
    }
}

// Batch Upload
async function handleBatchUpload(files) {
    const formData = new FormData();
    
    // Add all files to form data
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }
    
    // Show processing with progress
    showProcessing(true);
    processingText.textContent = `Processing ${files.length} file(s)...`;
    
    try {
        const response = await fetch('/upload-batch', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showBatchResults(result);
        } else {
            showError(result.error || 'Batch processing failed');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideProcessing();
    }
}

// UI Functions
function showProcessing(showProgress = false) {
    processingStatus.classList.remove('hidden');
    if (showProgress) {
        progressContainer.classList.remove('hidden');
    } else {
        progressContainer.classList.add('hidden');
    }
}

function hideProcessing() {
    processingStatus.classList.add('hidden');
    progressContainer.classList.add('hidden');
    processingText.textContent = 'Processing your file...';
}

function showResults(result) {
    currentResult = result;
    resultContent.textContent = result.content;
    resultsSection.classList.remove('hidden');
    
    // Hide batch-specific UI
    batchSummary.classList.add('hidden');
    downloadZipBtn.classList.add('hidden');
}

function showBatchResults(result) {
    batchResults = result;
    
    // Show summary
    batchSummary.classList.remove('hidden');
    totalFiles.textContent = result.total_files;
    processedFiles.textContent = result.processed;
    failedFiles.textContent = result.failed;
    skippedFiles.textContent = result.skipped;
    
    // Show download options
    downloadZipBtn.classList.remove('hidden');
    
    // Create combined markdown content
    const combinedContent = createBatchSummary(result);
    resultContent.textContent = combinedContent;
    resultsSection.classList.remove('hidden');
}

function createBatchSummary(result) {
    let content = '# Batch Processing Results\n\n';
    content += `## Summary\n`;
    content += `- Total files: ${result.total_files}\n`;
    content += `- Successfully processed: ${result.processed}\n`;
    content += `- Failed: ${result.failed}\n`;
    content += `- Skipped: ${result.skipped}\n\n`;
    
    if (result.results && result.results.length > 0) {
        content += '## Processed Files\n\n';
        result.results.forEach((file, index) => {
            content += `### ${index + 1}. ${file.relative_path || file.filename}\n\n`;
            content += file.content + '\n\n';
            content += '---\n\n';
        });
    }
    
    if (result.errors && result.errors.length > 0) {
        content += '## Failed Files\n\n';
        result.errors.forEach(error => {
            content += `- ${error.filename}: ${error.error}\n`;
        });
    }
    
    return content;
}

function hideResults() {
    resultsSection.classList.add('hidden');
    currentResult = null;
    batchResults = null;
    isBatchMode = false;
}

function showError(message) {
    const errorMessage = errorDisplay.querySelector('.error-message');
    errorMessage.textContent = message;
    errorDisplay.classList.remove('hidden');
}

function hideError() {
    errorDisplay.classList.add('hidden');
}

// Download Functions
async function downloadMarkdown() {
    if (isBatchMode && batchResults) {
        downloadBatch('markdown');
    } else if (currentResult) {
        downloadSingleFile();
    }
}

async function downloadSingleFile() {
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content: currentResult.content,
                filename: currentResult.filename
            })
        });
        
        if (response.ok) {
            // Get the filename from the Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition && contentDisposition.match(/filename="(.+)"/);
            const filename = filenameMatch ? filenameMatch[1] : 'output.md';
            
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showError('Download failed');
        }
    } catch (error) {
        showError('Download error: ' + error.message);
    }
}

async function downloadBatch(format) {
    if (!batchResults || !batchResults.results) return;
    
    try {
        const response = await fetch('/download-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                results: batchResults.results,
                format: format
            })
        });
        
        if (response.ok) {
            const contentDisposition = response.headers.get('Content-Disposition');
            const filenameMatch = contentDisposition && contentDisposition.match(/filename="(.+)"/);
            const filename = filenameMatch ? filenameMatch[1] : `batch_${format}.${format === 'zip' ? 'zip' : 'md'}`;
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showError('Batch download failed');
        }
    } catch (error) {
        showError('Download error: ' + error.message);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if the server is healthy
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            if (!data.processors_initialized) {
                showError('Server is not properly configured. Please check your API settings.');
            }
        })
        .catch(() => {
            showError('Cannot connect to server');
        });
});
