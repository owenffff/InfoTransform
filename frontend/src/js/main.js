import { loadAnalysisModels } from './modules/api.js';
import { setupEventListeners } from './modules/events.js';
import { updateViewToggle } from './modules/ui.js';
import { setCurrentView } from './modules/state.js';

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAnalysisModels();
    setupEventListeners();
    
    // Load view preference from localStorage
    const savedView = localStorage.getItem('preferredView') || 'table';
    setCurrentView(savedView);
    updateViewToggle();
});
