'use client';

import { useState, useEffect } from 'react';
import { Sparkles } from 'lucide-react';
import { useStore } from '@/lib/store';
import { transformFiles } from '@/lib/api';
import { showToast } from './Toast';
import { StreamingEvent } from '@/types';
import { dispatchStreamingEvent } from './ProcessingStatus';

export function AnalysisOptions({ onTransformStart }: { onTransformStart: () => void }) {
  const { 
    selectedFiles, 
    modelsData, 
    setStreamingResults,
    addStreamingResult,
    setModelFields,
    setIsProcessing,
    clearResults
  } = useStore();
  
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedAIModel, setSelectedAIModel] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [modelDescription, setModelDescription] = useState('');
  const [schemaFields, setSchemaFields] = useState<string[]>([]);

  useEffect(() => {
    if (modelsData?.ai_models?.default_model) {
      setSelectedAIModel(modelsData.ai_models.default_model);
    } else if (modelsData?.ai_models?.models) {
      // If no default model, use the first available model
      const firstModel = Object.keys(modelsData.ai_models.models)[0];
      if (firstModel) {
        setSelectedAIModel(firstModel);
      }
    }
  }, [modelsData]);

  const handleModelChange = (modelKey: string) => {
    setSelectedModel(modelKey);
    if (modelKey && modelsData?.models[modelKey]) {
      const model = modelsData.models[modelKey];
      setModelDescription(model.description);
      // Convert fields object to array of field names
      const fieldNames = typeof model.fields === 'object' && !Array.isArray(model.fields) 
        ? Object.keys(model.fields)
        : Array.isArray(model.fields) ? model.fields : [];
      setSchemaFields(fieldNames);
      setModelFields(fieldNames);
    } else {
      setModelDescription('');
      setSchemaFields([]);
      setModelFields([]);
    }
  };

  const handleTransform = async () => {
    if (!selectedModel) {
      showToast('error', 'Please select an analysis model');
      return;
    }

    clearResults();
    setIsProcessing(true);
    onTransformStart();

    const handleEvent = (event: StreamingEvent) => {
      // Dispatch event for ProcessingStatus component
      dispatchStreamingEvent(event);
      
      if (event.type === 'result' && event.status === 'success' && event.structured_data && event.filename) {
        // Add the result to the streaming results
        addStreamingResult({
          filename: event.filename,
          status: event.status,
          markdown_content: event.markdown_content,
          structured_data: event.structured_data,
          model_fields: event.model_fields,
          processing_time: event.processing_time,
          was_summarized: event.was_summarized,
          summarization_metrics: event.summarization_metrics
        });
      }
      if (event.type === 'complete') {
        setIsProcessing(false);
        if (event.summary) {
          if (event.summary.successful_files > 0) {
            showToast('success', `Successfully processed ${event.summary.successful_files} file(s)`);
          }
          if (event.summary.failed_files > 0) {
            showToast('error', `Failed to process ${event.summary.failed_files} file(s)`);
          }
        }
      }
      if (event.type === 'error') {
        showToast('error', event.error || 'An error occurred');
      }
    };

    const handleError = (error: string) => {
      setIsProcessing(false);
      showToast('error', error);
    };

    await transformFiles(
      selectedFiles,
      selectedModel,
      customInstructions,
      selectedAIModel,
      handleEvent,
      handleError
    );
  };

  if (!selectedFiles.length) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-brand-orange-500">2.</span>
        Configure Extraction
      </h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Analysis Model */}
        <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
          <label htmlFor="modelSelect" className="block text-sm font-semibold text-gray-800 mb-3">
            Analysis Model
          </label>
          <select
            id="modelSelect"
            value={selectedModel}
            onChange={(e) => handleModelChange(e.target.value)}
            className="block w-full rounded-md border-gray-300 bg-white shadow-sm focus:border-brand-orange-500 focus:ring-brand-orange-500 sm:text-sm"
          >
            <option value="">Select an analysis model...</option>
            {modelsData?.models && Object.entries(modelsData.models).map(([key, model]) => (
              <option key={key} value={key}>
                {model.name}
              </option>
            ))}
          </select>
          
          {modelDescription && (
            <div className="mt-4 p-3 bg-brand-orange-50 border-l-4 border-brand-orange-400 text-sm text-gray-700 rounded">
              {modelDescription}
            </div>
          )}
          
          {/* Schema Preview */}
          {schemaFields.length > 0 && (
            <div className="mt-5">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">
                Schema Preview
              </h3>
              <div className="p-4 bg-white rounded-lg border border-gray-200 shadow-inner">
                <div className="flex flex-wrap gap-2">
                  {schemaFields.map((field) => (
                    <span
                      key={field}
                      className="px-3 py-1 bg-brand-orange-100 text-brand-orange-700 rounded-full text-xs font-medium"
                    >
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Right Column: AI Model & Custom Instructions */}
        <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
          <label htmlFor="aiModelSelect" className="block text-sm font-semibold text-gray-800 mb-3">
            AI Model
          </label>
          <select
            id="aiModelSelect"
            value={selectedAIModel}
            onChange={(e) => setSelectedAIModel(e.target.value)}
            className="block w-full rounded-md border-gray-300 bg-white shadow-sm focus:border-brand-orange-500 focus:ring-brand-orange-500 sm:text-sm mb-6"
          >
            {modelsData?.ai_models?.models && Object.entries(modelsData.ai_models.models).map(([key, model]) => (
              <option key={key} value={key}>
                {model.display_name || key}
              </option>
            ))}
          </select>
          
          <div className="border-t border-gray-200 pt-5">
            <label htmlFor="customInstructions" className="block text-sm font-semibold text-gray-800 mb-3">
              Custom Instructions (Optional)
            </label>
            <textarea
              id="customInstructions"
              rows={4}
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              className="block w-full rounded-md border-gray-300 bg-white shadow-sm focus:border-brand-orange-500 focus:ring-brand-orange-500 sm:text-sm resize-none"
              placeholder="Add any specific instructions for the analysis..."
            />
            <p className="mt-2 text-xs text-gray-500">
              Provide additional context or specific requirements for the analysis
            </p>
          </div>
        </div>
      </div>
      
      <div className="mt-8 flex justify-center">
        <button
          onClick={handleTransform}
          className="inline-flex items-center px-10 py-4 border border-transparent text-lg font-semibold rounded-xl shadow-lg text-white bg-gradient-to-r from-brand-orange-500 to-brand-orange-400 hover:from-brand-orange-600 hover:to-brand-orange-500 focus:outline-none focus:ring-4 focus:ring-brand-orange-500 focus:ring-opacity-50 transition-all duration-300 transform hover:scale-105 hover:shadow-xl"
        >
          <Sparkles className="w-6 h-6 mr-3" />
          Transform to Structured Data
        </button>
      </div>
    </div>
  );
}