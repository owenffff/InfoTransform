'use client';

import { useEffect, useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { AnalysisOptions } from '@/components/AnalysisOptions';
import { ProcessingStatus } from '@/components/ProcessingStatus';
import { ResultsDisplay } from '@/components/ResultsDisplay';
import { ToastContainer } from '@/components/Toast';
import { useStore } from '@/lib/store';
import { loadAnalysisModels } from '@/lib/api';
import { showToast } from '@/components/Toast';
import { dispatchStreamingEvent } from '@/components/ProcessingStatus';

export default function Home() {
  const { 
    selectedFiles, 
    setModelsData, 
    isProcessing,
    streamingResults,
    setIsProcessing
  } = useStore();
  
  const [showOptions, setShowOptions] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    // Load available models on mount
    loadAnalysisModels()
      .then(data => {
        setModelsData(data);
      })
      .catch(error => {
        console.error('Failed to load models:', error);
        showToast('error', 'Failed to load analysis models. Please refresh the page.');
      });
  }, [setModelsData]);

  useEffect(() => {
    // Show options when files are selected
    setShowOptions(selectedFiles.length > 0);
  }, [selectedFiles]);

  useEffect(() => {
    // Show results when we have streaming results
    setShowResults(streamingResults.length > 0);
  }, [streamingResults]);

  const handleTransformStart = () => {
    // This is called when transform starts
    setShowResults(true);
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header Card */}
        <div className="bg-gradient-to-br from-white to-brand-orange-50 rounded-xl shadow-lg border border-gray-200 mb-8 overflow-hidden">
          <div className="px-6 py-10 text-center relative">
            <div className="absolute inset-0 bg-gradient-to-br from-brand-orange-500/5 to-brand-orange-400/5"></div>
            <h1 className="text-5xl font-bold text-gray-900 flex items-center justify-center gap-4 relative">
              Information Transformer
            </h1>
            <p className="mt-4 text-xl text-gray-700 font-medium">
              Transform any file type into structured, actionable data
            </p>
          </div>
        </div>

        <main className="space-y-6">
          {/* Upload Section */}
          <FileUpload />
          
          {/* Analysis Options */}
          {showOptions && !isProcessing && (
            <AnalysisOptions onTransformStart={handleTransformStart} />
          )}
          
          {/* Processing Status */}
          {isProcessing && <ProcessingStatus />}
          
          {/* Results Section */}
          {showResults && !isProcessing && <ResultsDisplay />}
        </main>

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500">
          <p>Powered by Pydantic AI & OpenAI</p>
        </footer>
      </div>

      {/* Toast Container */}
      <ToastContainer />
    </div>
  );
}
