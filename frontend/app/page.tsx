'use client';

import React, { useEffect, useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { AnalysisOptions } from '@/components/AnalysisOptions';
import { ProcessingStatus } from '@/components/ProcessingStatus';
import { ResultsDisplay } from '@/components/ResultsDisplay';
import { ToastContainer } from '@/components/Toast';
import { useStore } from '@/lib/store';
import { loadAnalysisModels } from '@/lib/api';
import { showToast } from '@/components/Toast';
import { Sparkles, FileText, Activity } from 'lucide-react';
import { Separator } from '@/components/ui/separator';

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
        showToast('error', 'Failed to load document schemas. Please refresh the page.');
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

  const getStepStatus = (step: number) => {
    // Step 1: Upload - completed if files selected, active if not
    if (step === 1) return selectedFiles.length > 0 ? 'completed' : 'active';
    
    // Step 2: Configure - completed if processing or has results, active if files but not processing, inactive otherwise
    if (step === 2) {
      if (selectedFiles.length === 0) return 'inactive';
      if (isProcessing || streamingResults.length > 0) return 'completed';
      return 'active';
    }
    
    // Step 3: Process - completed if has results, active if processing, inactive otherwise
    if (step === 3) {
      if (streamingResults.length > 0) return 'completed';
      if (isProcessing) return 'active';
      return 'inactive';
    }
    
    // Step 4: Results - completed if has results and not processing, active if processing, inactive otherwise
    if (step === 4) {
      if (streamingResults.length > 0 && !isProcessing) return 'completed';
      if (isProcessing) return 'active';
      return 'inactive';
    }
    
    return 'inactive';
  };

  const StepIndicator = ({ title, icon, status }: { 
    title: string; 
    icon: React.ReactNode;
    status: string;
  }) => (
    <div className={`flex items-center gap-3 ${
      status === 'completed' ? 'text-primary' :
      status === 'active' ? 'text-foreground' :
      'text-muted-foreground'
    }`}>
      <div className={`
        flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300
        ${status === 'completed' ? 'bg-primary border-primary text-primary-foreground' :
          status === 'active' ? 'bg-background border-primary text-primary' :
          'bg-muted border-muted-foreground/30'}
      `}>
        {status === 'completed' ? '✓' : icon}
      </div>
      <div className="flex items-center gap-2">
        {icon}
        <span className="font-medium hidden sm:inline">{title}</span>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-secondary/20">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-background/80 border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-primary to-primary/80 rounded-lg">
                <Sparkles className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  InfoTransform
                </h1>
                <p className="text-xs text-muted-foreground">
                  Transform any file into structured data
                </p>
              </div>
            </div>
            
            {/* Progress Steps */}
            <div className="hidden lg:flex items-center gap-8">
              <StepIndicator 
                title="Upload" 
                icon={<FileText className="w-4 h-4" />}
                status={getStepStatus(1)} 
              />
              <Separator className="w-8" />
              <StepIndicator 
                title="Configure" 
                icon={<Sparkles className="w-4 h-4" />}
                status={getStepStatus(2)} 
              />
              <Separator className="w-8" />
              <StepIndicator 
                title="Process" 
                icon={<Activity className="w-4 h-4" />}
                status={getStepStatus(3)} 
              />
              <Separator className="w-8" />
              <StepIndicator 
                title="Results" 
                icon={<FileText className="w-4 h-4" />}
                status={getStepStatus(4)} 
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        
        {/* Mobile Progress */}
        <div className="lg:hidden mb-6">
          <div className="flex items-center justify-between gap-2">
            <StepIndicator 
              title="Upload" 
              icon={<></>}
              status={getStepStatus(1)} 
            />
            <StepIndicator 
              title="Configure" 
              icon={<></>}
              status={getStepStatus(2)} 
            />
            <StepIndicator 
              title="Process" 
              icon={<></>}
              status={getStepStatus(3)} 
            />
            <StepIndicator 
              title="Results" 
              icon={<></>}
              status={getStepStatus(4)} 
            />
          </div>
        </div>

        <div className="space-y-6">
          {/* Upload Section */}
          <FileUpload />
          
          {/* Analysis Options */}
          {showOptions && !isProcessing && (
            <AnalysisOptions onTransformStart={handleTransformStart} />
          )}
          

          {/* Processing Status */}
          {isProcessing && <ProcessingStatus />}

          {/* Results Section - Show during and after processing */}
          {showResults && <ResultsDisplay />}
        </div>
      </main>

      {/* Toast Container */}
      <ToastContainer />
    </div>
  );
}
