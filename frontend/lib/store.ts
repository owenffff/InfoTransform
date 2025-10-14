import { create } from 'zustand';
import { FileResult, ModelsData, ReviewSession, FileReviewStatus, FieldEdit } from '@/types';
import { updateFileFields, approveFile as approveFileAPI } from './api';

interface AppState {
  // Files
  selectedFiles: File[];
  setSelectedFiles: (files: File[]) => void;
  
  // Models
  modelsData: ModelsData | null;
  setModelsData: (data: ModelsData) => void;
  
  // Results
  streamingResults: FileResult[];
  setStreamingResults: (results: FileResult[]) => void;
  addStreamingResult: (result: FileResult) => void;
  
  // Model fields
  modelFields: string[];
  setModelFields: (fields: string[]) => void;
  
  // Edited data
  editedData: Record<string, Record<string, any>>;
  setEditedData: (data: Record<string, Record<string, any>>) => void;
  updateEditedData: (filename: string, field: string, value: any) => void;
  
  // Sort state
  sortState: { column: string | null; direction: 'asc' | 'desc' | null };
  setSortState: (state: { column: string | null; direction: 'asc' | 'desc' | null }) => void;
  
  // Processing state
  isProcessing: boolean;
  setIsProcessing: (processing: boolean) => void;
  
  // View state
  viewMode: 'table' | 'cards';
  setViewMode: (mode: 'table' | 'cards') => void;
  
  // Clear all results
  clearResults: () => void;
}

interface ReviewState {
  currentSession: ReviewSession | null;
  currentFileIndex: number;
  activeViewMode: 'form' | 'table' | 'json';
  activeSourceTab: 'source' | 'markdown';
  highlightedFields: string[];
  lockedHighlights: string[];
  pendingEdits: Record<string, FieldEdit>;
  hasUnsavedChanges: boolean;
  isSidebarCollapsed: boolean;
  
  setCurrentSession: (session: ReviewSession | null) => void;
  setCurrentFile: (index: number) => void;
  setActiveViewMode: (mode: 'form' | 'table' | 'json') => void;
  setActiveSourceTab: (tab: 'source' | 'markdown') => void;
  updateField: (fieldName: string, value: any, recordIndex?: number) => void;
  saveChanges: () => Promise<void>;
  discardChanges: () => void;
  approveFile: (comments?: string) => Promise<void>;
  rejectFile: (reason: string) => Promise<void>;
  addHighlight: (fieldName: string) => void;
  removeHighlight: (fieldName: string) => void;
  lockHighlight: (fieldName: string) => void;
  toggleSidebar: () => void;
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  currentSession: null,
  currentFileIndex: 0,
  activeViewMode: 'form',
  activeSourceTab: 'source',
  highlightedFields: [],
  lockedHighlights: [],
  pendingEdits: {},
  hasUnsavedChanges: false,
  isSidebarCollapsed: false,
  
  setCurrentSession: (session) => set({ currentSession: session, currentFileIndex: 0 }),
  
  setCurrentFile: (index) => {
    const state = get();
    if (state.hasUnsavedChanges) {
      const confirmed = window.confirm('You have unsaved changes. Do you want to discard them?');
      if (!confirmed) return;
    }
    set({ 
      currentFileIndex: index, 
      pendingEdits: {}, 
      hasUnsavedChanges: false,
      highlightedFields: [],
      lockedHighlights: []
    });
  },
  
  setActiveViewMode: (mode) => set({ activeViewMode: mode }),
  setActiveSourceTab: (tab) => set({ activeSourceTab: tab }),
  
  updateField: (fieldName, value, recordIndex) => {
    const state = get();
    const currentFile = state.currentSession?.files[state.currentFileIndex];
    if (!currentFile) return;
    
    const data = currentFile.extracted_data;
    const isArray = Array.isArray(data);
    
    let originalValue;
    let editKey;
    
    if (isArray && recordIndex !== undefined) {
      originalValue = data[recordIndex]?.[fieldName];
      editKey = `${recordIndex}.${fieldName}`;
    } else if (!isArray) {
      originalValue = data[fieldName];
      editKey = fieldName;
    } else {
      return;
    }
    
    set({
      pendingEdits: {
        ...state.pendingEdits,
        [editKey]: {
          field_name: fieldName,
          original_value: originalValue,
          edited_value: value,
          edited_at: new Date().toISOString(),
          validation_status: 'valid',
          record_index: recordIndex
        }
      },
      hasUnsavedChanges: true
    });
  },
  
  saveChanges: async () => {
    const state = get();
    const session = state.currentSession;
    const currentFile = session?.files[state.currentFileIndex];
    
    if (!session || !currentFile) return;
    
    const edits = Object.values(state.pendingEdits);
    
    try {
      const updatedFile = await updateFileFields(session.session_id, currentFile.file_id, edits);
      
      const updatedFiles = [...session.files];
      updatedFiles[state.currentFileIndex] = updatedFile;
      
      set({
        currentSession: { ...session, files: updatedFiles },
        pendingEdits: {},
        hasUnsavedChanges: false
      });
    } catch (error) {
      console.error('Failed to save changes:', error);
    }
  },
  
  discardChanges: () => set({ pendingEdits: {}, hasUnsavedChanges: false }),
  
  approveFile: async (comments) => {
    const state = get();
    const session = state.currentSession;
    const currentFile = session?.files[state.currentFileIndex];
    
    if (!session || !currentFile) return;
    
    try {
      const updatedFile = await approveFileAPI(session.session_id, currentFile.file_id, {
        approved_at: new Date().toISOString(),
        approved_by: 'user',
        comments,
        approval_status: 'approved'
      });
      
      const updatedFiles = [...session.files];
      updatedFiles[state.currentFileIndex] = updatedFile;
      
      const approvedCount = updatedFiles.filter(f => f.status === 'approved').length;
      const rejectedCount = updatedFiles.filter(f => f.status === 'rejected').length;
      
      set({
        currentSession: { 
          ...session, 
          files: updatedFiles,
          batch_metadata: {
            ...session.batch_metadata,
            approved_count: approvedCount,
            rejected_count: rejectedCount
          }
        }
      });
    } catch (error) {
      console.error('Failed to approve file:', error);
    }
  },
  
  rejectFile: async (reason) => {
    const state = get();
    const session = state.currentSession;
    const currentFile = session?.files[state.currentFileIndex];
    
    if (!session || !currentFile) return;
    
    try {
      const updatedFile = await approveFileAPI(session.session_id, currentFile.file_id, {
        approved_at: new Date().toISOString(),
        approved_by: 'user',
        approval_status: 'rejected',
        rejection_reason: reason
      });
      
      const updatedFiles = [...session.files];
      updatedFiles[state.currentFileIndex] = updatedFile;
      
      set({
        currentSession: { ...session, files: updatedFiles }
      });
    } catch (error) {
      console.error('Failed to reject file:', error);
    }
  },
  
  addHighlight: (fieldName) => {
    const state = get();
    if (!state.highlightedFields.includes(fieldName)) {
      set({ highlightedFields: [...state.highlightedFields, fieldName] });
    }
  },
  
  removeHighlight: (fieldName) => {
    set((state) => ({
      highlightedFields: state.highlightedFields.filter(f => f !== fieldName)
    }));
  },
  
  lockHighlight: (fieldName) => {
    const state = get();
    if (state.lockedHighlights.includes(fieldName)) {
      set({ lockedHighlights: state.lockedHighlights.filter(f => f !== fieldName) });
    } else {
      set({ lockedHighlights: [...state.lockedHighlights, fieldName] });
    }
  },
  
  toggleSidebar: () => set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed }))
}));

export const useStore = create<AppState>((set) => ({
  // Files
  selectedFiles: [],
  setSelectedFiles: (files) => set({ selectedFiles: files }),
  
  // Models
  modelsData: null,
  setModelsData: (data) => set({ modelsData: data }),
  
  // Results
  streamingResults: [],
  setStreamingResults: (results) => set({ streamingResults: results }),
  addStreamingResult: (result) => set((state) => ({
    streamingResults: [...state.streamingResults, result]
  })),
  
  // Model fields
  modelFields: [],
  setModelFields: (fields) => set({ modelFields: fields }),
  
  // Edited data
  editedData: {},
  setEditedData: (data) => set({ editedData: data }),
  updateEditedData: (filename, field, value) => set((state) => ({
    editedData: {
      ...state.editedData,
      [filename]: {
        ...state.editedData[filename],
        [field]: value
      }
    }
  })),
  
  // Sort state
  sortState: { column: null, direction: null },
  setSortState: (state) => set({ sortState: state }),
  
  // Processing state
  isProcessing: false,
  setIsProcessing: (processing) => set({ isProcessing: processing }),
  
  // View state
  viewMode: 'table',
  setViewMode: (mode) => set({ viewMode: mode }),
  
  // Clear all results
  clearResults: () => set({
    streamingResults: [],
    editedData: {},
    sortState: { column: null, direction: null }
  })
}));