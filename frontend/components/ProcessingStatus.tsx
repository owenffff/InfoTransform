'use client';

import { useEffect, useRef, useState } from 'react';
import { CheckCircle, XCircle, Clock, FileText, Activity } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Task, TaskContent, TaskItem, TaskTrigger } from '@/components/ai-elements/task';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader as AiLoader } from '@/components/ai-elements/loader';
import { useStore } from '@/lib/store';

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
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <span className="text-primary">3.</span>
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
        {/* Overall Pipeline */}
        <Task defaultOpen>
          <TaskTrigger title={`Overall processing — ${Math.min(processedCount, totalCount || processedCount)}/${totalCount} files • ${Math.round(overallProgress)}%`} />
          <TaskContent aria-live="polite" role="status">
            {estimatedTimeRemaining && (
              <div className="text-xs text-muted-foreground mb-2 flex items-center gap-2">
                <Clock className="w-3 h-3" />
                <span>{estimatedTimeRemaining}</span>
              </div>
            )}
            <TaskItem aria-busy={currentPhase === 'converting'}>
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                <span>Converting</span>
                {currentPhase === 'converting' && <AiLoader size={14} className="text-blue-600" />}
                {currentPhase !== 'converting' && overallProgress > 0 && <CheckCircle className="w-4 h-4 text-green-600" />}
              </div>
            </TaskItem>
            <TaskItem aria-busy={currentPhase === 'analyzing'}>
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4" />
                <span>Analyzing</span>
                {currentPhase === 'analyzing' && <AiLoader size={14} className="text-blue-600" />}
                {currentPhase === 'complete' && <CheckCircle className="w-4 h-4 text-green-600" />}
              </div>
            </TaskItem>
            <TaskItem>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                <span>Complete</span>
                {currentPhase === 'complete' && <span className="text-green-700 text-xs font-medium">Done</span>}
              </div>
            </TaskItem>
          </TaskContent>
        </Task>


        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center justify-center gap-2 mb-1">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-900">Success</span>
            </div>
            <p className="text-2xl font-bold text-green-700">{successCount}</p>
          </div>
          
          <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-center gap-2 mb-1">
              <span className="text-sm font-medium text-blue-900">Processing</span>
            </div>
            <p className="text-2xl font-bold text-blue-700">
              {Math.max(0, processedCount - successCount - errorCount)}
            </p>
          </div>
          
          <div className="text-center p-3 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center justify-center gap-2 mb-1">
              <XCircle className="w-4 h-4 text-red-600" />
              <span className="text-sm font-medium text-red-900">Failed</span>
            </div>
            <p className="text-2xl font-bold text-red-700">{errorCount}</p>
          </div>
        </div>

        {/* Current File */}
        {currentFile && (
          <Alert className="border-primary/20 bg-primary/5">
            <Activity className="h-4 w-4 text-primary animate-pulse" />
            <AlertDescription className="text-sm">
              <strong>Processing:</strong> {currentFile}
            </AlertDescription>
          </Alert>
        )}


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
