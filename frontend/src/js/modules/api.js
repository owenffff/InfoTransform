import * as dom from './dom.js';
import * as state from './state.js';
import { handleStreamingEvent, showError, updateProgress } from './ui.js';

// Load available analysis models
export async function loadAnalysisModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        // Store the data globally
        state.setModelsData(data);
        
        // Populate analysis models
        dom.modelSelect.innerHTML = '<option value="">Select an analysis model...</option>';
        for (const [key, model] of Object.entries(data.models)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = model.name;
            option.dataset.description = model.description;
            dom.modelSelect.appendChild(option);
        }
        
        // Populate AI models
        dom.aiModelSelect.innerHTML = '<option value="">Default</option>';
        for (const [modelId, config] of Object.entries(data.ai_models.models)) {
            const option = document.createElement('option');
            option.value = modelId;
            // Use display_name if available, otherwise use model ID
            option.textContent = config.display_name || modelId;
            dom.aiModelSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Failed to load models:', error);
        showError('Failed to load analysis models. Please refresh the page.');
    }
}

// Transform files
export async function handleTransform() {
    if (!state.selectedFiles.length) {
        showError('Please select files to transform');
        return;
    }
    
    if (!dom.modelSelect.value) {
        showError('Please select an analysis model');
        return;
    }
    
    // Hide previous results
    dom.resultsSection.classList.add('hidden');
    dom.errorDisplay.classList.add('hidden');
    
    // Show processing status
    dom.processingStatus.classList.remove('hidden');
    dom.analysisOptions.classList.add('hidden');
    
    // Reset streaming results
    state.setStreamingResults([]);
    state.setModelFields([]);
    state.setEditedData({});
    state.setSortState({ column: null, direction: null });
    
    // Always use streaming endpoint (v2) for both single and multiple files
    await handleStreamingTransform();
}

// Handle streaming transform for all files
async function handleStreamingTransform() {
    const formData = new FormData();
    for (const file of state.selectedFiles) {
        formData.append('files', file);
    }
    formData.append('model_key', dom.modelSelect.value);
    formData.append('custom_instructions', dom.customInstructions.value || '');
    if (dom.aiModelSelect.value) {
        formData.append('ai_model', dom.aiModelSelect.value);
    }
    
    // Show progress container
    dom.progressContainer.classList.remove('hidden');
    updateProgress(0, state.selectedFiles.length);
    
    // Show results section immediately for streaming
    dom.resultsSection.classList.remove('hidden');
    
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
        dom.processingStatus.classList.add('hidden');
        dom.analysisOptions.classList.remove('hidden');
    }
}

// Download results
export async function downloadResults(format) {
    if (!state.transformResults) return;
    
    // Include edited data in the download
    const resultsWithEdits = {
        ...state.transformResults,
        results: state.transformResults.results.map(result => {
            if (result.status === 'success' && result.structured_data) {
                const editedStructuredData = { ...result.structured_data };
                
                // Apply any edits
                Object.keys(state.editedData).forEach(key => {
                    const [filename, field] = key.split('_');
                    if (filename === result.filename) {
                        editedStructuredData[field] = state.editedData[key];
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
