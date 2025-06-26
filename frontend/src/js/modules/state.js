// Global variables
export let selectedFiles = [];
export let transformResults = null;
export let currentView = 'table'; // Default to table view
export let eventSource = null;
export let streamingResults = [];
export let modelFields = [];
export let editedData = {}; // Track edited values
export let sortState = { column: null, direction: null }; // Track sort state
export let modelsData = null;

export function setSelectedFiles(files) {
    selectedFiles = files;
}

export function setTransformResults(results) {
    transformResults = results;
}

export function setCurrentView(view) {
    currentView = view;
}

export function setEventSource(source) {
    eventSource = source;
}

export function setStreamingResults(results) {
    streamingResults = results;
}

export function addStreamingResult(result) {
    streamingResults.push(result);
}

export function setModelFields(fields) {
    modelFields = fields;
}

export function setEditedData(data) {
    editedData = data;
}

export function updateEditedData(key, value) {
    editedData[key] = value;
}

export function setSortState(state) {
    sortState = state;
}

export function setModelsData(data) {
    modelsData = data;
}
