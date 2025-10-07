import { create } from 'zustand';
import { FileResult, ModelsData } from '@/types';

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