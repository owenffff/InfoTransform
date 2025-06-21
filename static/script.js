// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const processingStatus = document.getElementById('processingStatus');
const resultsSection = document.getElementById('resultsSection');
const resultContent = document.getElementById('resultContent');
const downloadBtn = document.getElementById('downloadBtn');
const errorDisplay = document.getElementById('errorDisplay');

// State
let currentResult = null;

// Event Listeners
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadMarkdown);

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
        handleFile(files[0]);
    }
});

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
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

// UI Functions
function showProcessing() {
    processingStatus.classList.remove('hidden');
}

function hideProcessing() {
    processingStatus.classList.add('hidden');
}

function showResults(result) {
    currentResult = result;
    resultContent.textContent = result.content;
    resultsSection.classList.remove('hidden');
}

function hideResults() {
    resultsSection.classList.add('hidden');
    currentResult = null;
}

function showError(message) {
    const errorMessage = errorDisplay.querySelector('.error-message');
    errorMessage.textContent = message;
    errorDisplay.classList.remove('hidden');
}

function hideError() {
    errorDisplay.classList.add('hidden');
}

// Download Function
async function downloadMarkdown() {
    if (!currentResult) return;
    
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
