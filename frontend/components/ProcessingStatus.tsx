'use client';

import { useEffect, useRef, useState } from 'react';
import { CheckCircle, XCircle, Clock, FileText, Activity } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Task, TaskContent, TaskItem, TaskTrigger } from '@/components/ai-elements/task';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader as AiLoader } from '@/components/ai-elements/loader';
import { Progress } from '@/components/ui/progress';
import { useStore } from '@/lib/store';
import { cn } from '@/lib/utils';

export interface StreamingEvent {
  type: 'start' | 'markdown_conversion' | 'ai_analysis' | 'result' | 'complete' | 'error' | 'reset';
  filename?: string;
  status?: 'success' | 'error' | 'processing';
  message?: string;
  error?: string;
  progress?: number;
  total?: number;
  markdown_content?: string;
  structured_data?: any;
  model_fields?: string[];
  processing_time?: number;
  was_summarized?: boolean;
  summarization_metrics?: {
    original_length: number;
    summary_length: number;
    compression_ratio: number;
  };
  summary?: {
    total_files: number;
    successful_files: number;
    failed_files: number;
    total_time: number;
  };
}


let eventHandlers: Map<string, (event: StreamingEvent) => void> = new Map();

export function addStreamingEventListener(id: string, handler: (event: StreamingEvent) => void) {
  eventHandlers.set(id, handler);
}

export function removeStreamingEventListener(id: string) {
  eventHandlers.delete(id);
}

export function dispatchStreamingEvent(event: StreamingEvent) {
  eventHandlers.forEach(handler => handler(event));
}

export function ProcessingStatus() {
  const [currentFile, setCurrentFile] = useState<string>('');
  const [overallProgress, setOverallProgress] = useState(0);
  const [processedCount, setProcessedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [successCount, setSuccessCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [currentPhase, setCurrentPhase] = useState<'converting' | 'analyzing' | 'complete'>('converting');
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<string>('');
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [handlerId] = useState(() => `handler-${Date.now()}-${Math.random()}`);
  const finishedFilesRef = useRef<Set<string>>(new Set());
  const { selectedFiles } = useStore();

  useEffect(() => {
    const handleEvent = (event: StreamingEvent) => {
      const timestamp = new Date().toLocaleTimeString();
      
      switch (event.type) {
        case 'reset':
          // Reset all counts and state
          setCurrentFile('');
          setOverallProgress(0);
          setProcessedCount(0);
          setTotalCount(0);
          setSuccessCount(0);
          setErrorCount(0);
          setCurrentPhase('converting');
          setEstimatedTimeRemaining('');
          setStartTime(Date.now());
          break;
          
        case 'start':
          setTotalCount(event.total && event.total > 0 ? event.total : (selectedFiles?.length ?? 0));
          setProcessedCount(0);
          setSuccessCount(0);
          setErrorCount(0);
          setStartTime(Date.now());
          finishedFilesRef.current.clear();
          break;

        case 'markdown_conversion':
          if (event.filename) {
            setCurrentFile(event.filename);
            setCurrentPhase('converting');
          }
          if (event.progress && event.total) {
            const progress = (event.progress / event.total) * 50; // 50% for conversion
            setOverallProgress(progress);
            updateTimeEstimate(event.progress, event.total, startTime);
          }
          break;

        case 'ai_analysis':
          if (event.filename) {
            setCurrentFile(event.filename);
            setCurrentPhase('analyzing');
          }
          if (event.progress && event.total) {
            const progress = 50 + (event.progress / event.total) * 50; // 50-100% for analysis
            setOverallProgress(progress);
            updateTimeEstimate(event.progress, event.total, startTime);
          }
          break;

        case 'result':
          {
            const fname = event.filename;
            if (!fname) {
              break;
            }
            if (!finishedFilesRef.current.has(fname)) {
              finishedFilesRef.current.add(fname);
              if (event.status === 'success') {
                setSuccessCount(prev => prev + 1);
              } else if (event.status === 'error') {
                setErrorCount(prev => prev + 1);
              }
              setProcessedCount(prev => prev + 1);
            }
            // no-op: logs removed from UI
          }
          break;

        case 'complete':
          setCurrentPhase('complete');
          setOverallProgress(100);
          setEstimatedTimeRemaining('');
          if (event.summary) {
            const summary = event.summary;
            // summary available; logs UI removed
          }
          break;

        case 'error':
          // no-op: logs removed from UI
          break;
      }
    };

    // Use Map to prevent duplicate handlers
    eventHandlers.set(handlerId, handleEvent);
    
    return () => {
      eventHandlers.delete(handlerId);
    };
  }, [startTime, handlerId]);

  const updateTimeEstimate = (current: number, total: number, startTime: number) => {
    const elapsed = Date.now() - startTime;
    const rate = current / elapsed;
    const remaining = (total - current) / rate;
    const seconds = Math.round(remaining / 1000);
    
    if (seconds > 60) {
      const minutes = Math.floor(seconds / 60);
      const secs = seconds % 60;
      setEstimatedTimeRemaining(`${minutes}m ${secs}s remaining`);
    } else if (seconds > 0) {
      setEstimatedTimeRemaining(`${seconds}s remaining`);
    } else {
      setEstimatedTimeRemaining('Almost done...');
    }
  };


  return (
    <Card className="shadow-lg border-gray-200" role="region" aria-label="File processing status">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          Processing Status
          {currentPhase !== 'complete' ? (
            <Badge variant="default" className="ml-auto">Processing</Badge>
          ) : (
            <Badge variant="secondary" className="ml-auto">Complete</Badge>
          )}
        </CardTitle>
        <CardDescription>
          Transforming your files into structured data
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Screen reader live region for progress updates */}
        <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          {currentPhase === 'converting' && `Converting files: ${Math.round(overallProgress)}% complete. ${currentFile ? `Currently processing ${currentFile}` : ''}`}
          {currentPhase === 'analyzing' && `Analyzing files with AI: ${Math.round(overallProgress)}% complete. ${currentFile ? `Currently processing ${currentFile}` : ''}`}
          {currentPhase === 'complete' && `Transformation complete. ${successCount} successful, ${errorCount} failed.`}
        </div>

        {/* Large Progress Bar with Phase Indicator */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={cn(
                "p-1.5 rounded-lg transition-colors",
                currentPhase === 'converting' && "bg-blue-100",
                currentPhase === 'analyzing' && "bg-purple-100",
                currentPhase === 'complete' && "bg-green-100"
              )}>
                {currentPhase === 'converting' && <FileText className="w-5 h-5 text-blue-600" />}
                {currentPhase === 'analyzing' && <Activity className="w-5 h-5 text-purple-600 animate-pulse" />}
                {currentPhase === 'complete' && <CheckCircle className="w-5 h-5 text-green-600" />}
              </div>
              <div>
                <h4 className="text-sm font-semibold">
                  {currentPhase === 'converting' && 'Converting to markdown...'}
                  {currentPhase === 'analyzing' && 'Analyzing with AI...'}
                  {currentPhase === 'complete' && 'Transformation Complete!'}
                </h4>
                <p className="text-xs text-muted-foreground">
                  {Math.min(processedCount, totalCount || processedCount)}/{totalCount} files processed
                </p>
              </div>
            </div>

            <div className="text-right">
              <div className="text-2xl font-bold">
                {Math.round(overallProgress)}%
              </div>
              {estimatedTimeRemaining && (
                <div className="text-xs text-muted-foreground flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{estimatedTimeRemaining}</span>
                </div>
              )}
            </div>
          </div>

          {/* Large Progress Bar - Unified Blue Color */}
          <div className="relative">
            <Progress
              value={overallProgress}
              className="h-3 transition-all duration-500"
              aria-label={`Overall progress: ${Math.round(overallProgress)}%`}
              aria-valuenow={Math.round(overallProgress)}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>

          {/* Current File Display */}
          {currentFile && currentPhase !== 'complete' && (
            <div className="flex items-center gap-2 text-sm">
              <Badge variant="outline" className="font-mono text-xs">
                {currentFile}
              </Badge>
              {currentPhase === 'converting' && (
                <span className="text-xs text-muted-foreground">({processedCount + 1} of {totalCount})</span>
              )}
            </div>
          )}
        </div>

        {/* Phase Pills */}
        <div className="flex items-center gap-2">
          <div className={cn(
            "flex-1 flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-all",
            currentPhase === 'converting'
              ? "border-blue-500 bg-blue-50"
              : overallProgress > 0
                ? "border-green-500 bg-green-50"
                : "border-gray-200 bg-gray-50"
          )}>
            {overallProgress > 0 && currentPhase !== 'converting' ? (
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
            ) : currentPhase === 'converting' ? (
              <AiLoader size={16} className="text-blue-600 flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border-2 border-gray-400 flex-shrink-0" />
            )}
            <span className="text-xs font-medium">Convert</span>
          </div>

          <div className="w-8 border-t-2 border-dashed border-gray-300" />

          <div className={cn(
            "flex-1 flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-all",
            currentPhase === 'analyzing'
              ? "border-purple-500 bg-purple-50"
              : currentPhase === 'complete'
                ? "border-green-500 bg-green-50"
                : "border-gray-200 bg-gray-50"
          )}>
            {currentPhase === 'complete' ? (
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
            ) : currentPhase === 'analyzing' ? (
              <AiLoader size={16} className="text-purple-600 flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border-2 border-gray-400 flex-shrink-0" />
            )}
            <span className="text-xs font-medium">Analyze</span>
          </div>

          <div className="w-8 border-t-2 border-dashed border-gray-300" />

          <div className={cn(
            "flex-1 flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-all",
            currentPhase === 'complete'
              ? "border-green-500 bg-green-50"
              : "border-gray-200 bg-gray-50"
          )}>
            {currentPhase === 'complete' ? (
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
            ) : (
              <div className="w-4 h-4 rounded-full border-2 border-gray-400 flex-shrink-0" />
            )}
            <span className="text-xs font-medium">Complete</span>
          </div>
        </div>

        {/* Error Summary */}
        {errorCount > 0 && currentPhase === 'complete' && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>
              {errorCount} file{errorCount > 1 ? 's' : ''} failed to process. 
              Review the failed files above for details.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
