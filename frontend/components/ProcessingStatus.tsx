'use client';

import { useEffect, useState } from 'react';
import { Loader2, CheckCircle, XCircle, Clock, FileText, Activity, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

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

interface ProcessingLog {
  timestamp: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
  filename?: string;
}

let eventHandlers: Map<string, (event: StreamingEvent) => void> = new Map();

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
  const [processingLogs, setProcessingLogs] = useState<ProcessingLog[]>([]);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [showLogs, setShowLogs] = useState(false);
  const [handlerId] = useState(() => `handler-${Date.now()}-${Math.random()}`);

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
          setProcessingLogs([]);
          setStartTime(Date.now());
          break;
          
        case 'start':
          setTotalCount(event.total || 0);
          setProcessedCount(0);
          setSuccessCount(0);
          setErrorCount(0);
          setStartTime(Date.now());
          setProcessingLogs(prev => [...prev, {
            timestamp,
            type: 'info',
            message: `Starting processing of ${event.total} file(s)`
          }]);
          break;

        case 'markdown_conversion':
          if (event.filename) {
            setCurrentFile(event.filename);
            setCurrentPhase('converting');
            setProcessingLogs(prev => [...prev, {
              timestamp,
              type: 'info',
              message: `Converting to markdown`,
              filename: event.filename
            }]);
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
            setProcessingLogs(prev => [...prev, {
              timestamp,
              type: 'info',
              message: `Analyzing with AI`,
              filename: event.filename
            }]);
          }
          if (event.progress && event.total) {
            const progress = 50 + (event.progress / event.total) * 50; // 50-100% for analysis
            setOverallProgress(progress);
            updateTimeEstimate(event.progress, event.total, startTime);
          }
          break;

        case 'result':
          if (event.status === 'success') {
            setSuccessCount(prev => prev + 1);
            setProcessingLogs(prev => [...prev, {
              timestamp,
              type: 'success',
              message: event.was_summarized 
                ? `Processed successfully (summarized to fit context)`
                : `Processed successfully`,
              filename: event.filename
            }]);
          } else if (event.status === 'error') {
            setErrorCount(prev => prev + 1);
            setProcessingLogs(prev => [...prev, {
              timestamp,
              type: 'error',
              message: event.error || 'Processing failed',
              filename: event.filename
            }]);
          }
          setProcessedCount(prev => prev + 1);
          break;

        case 'complete':
          setCurrentPhase('complete');
          setOverallProgress(100);
          setEstimatedTimeRemaining('');
          if (event.summary) {
            const summary = event.summary;
            setProcessingLogs(prev => [...prev, {
              timestamp,
              type: 'info',
              message: `Processing complete: ${summary.successful_files} succeeded, ${summary.failed_files} failed (${Math.round(summary.total_time)}s total)`
            }]);
          }
          break;

        case 'error':
          setProcessingLogs(prev => [...prev, {
            timestamp,
            type: 'error',
            message: event.error || 'An error occurred'
          }]);
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

  const getPhaseIcon = (phase: string) => {
    switch (phase) {
      case 'converting':
        return <FileText className="w-4 h-4" />;
      case 'analyzing':
        return <Activity className="w-4 h-4" />;
      case 'complete':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Loader2 className="w-4 h-4 animate-spin" />;
    }
  };

  const getPhaseColor = (phase: string) => {
    if (phase === currentPhase) return 'default';
    if (phase === 'complete' && currentPhase === 'complete') return 'default';
    return 'secondary';
  };

  return (
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <span className="text-primary">3.</span>
          Processing Status
          <Badge variant="default" className="ml-auto animate-pulse">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Processing
          </Badge>
        </CardTitle>
        <CardDescription>
          Transforming your files into structured data
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Progress Overview */}
        <div className="space-y-3">
          <div className="flex justify-between items-center text-sm">
            <span className="font-medium">Overall Progress</span>
            <span className="text-muted-foreground">
              {processedCount}/{totalCount} files • {Math.round(overallProgress)}%
            </span>
          </div>
          <Progress value={overallProgress} className="h-3" />
          {estimatedTimeRemaining && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="w-3 h-3" />
              {estimatedTimeRemaining}
            </div>
          )}
        </div>

        {/* Phase Indicators */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 flex-1">
            <Badge variant={getPhaseColor('converting')} className="flex items-center gap-1">
              {getPhaseIcon('converting')}
              Converting
            </Badge>
            <Separator className="flex-1" />
            <Badge variant={getPhaseColor('analyzing')} className="flex items-center gap-1">
              {getPhaseIcon('analyzing')}
              Analyzing
            </Badge>
            <Separator className="flex-1" />
            <Badge variant={getPhaseColor('complete')} className="flex items-center gap-1">
              {getPhaseIcon('complete')}
              Complete
            </Badge>
          </div>
        </div>

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
              <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
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

        {/* Processing Logs */}
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="logs">
            <AccordionTrigger className="text-sm hover:no-underline">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                Processing Logs
                <Badge variant="secondary" className="ml-2">
                  {processingLogs.length} entries
                </Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent>
              <ScrollArea className="h-48 w-full rounded-lg border bg-muted/20 p-3">
                <div className="space-y-1">
                  {processingLogs.map((log, index) => (
                    <div
                      key={index}
                      className={`flex items-start gap-2 text-xs font-mono ${
                        log.type === 'error' ? 'text-red-600' :
                        log.type === 'success' ? 'text-green-600' :
                        log.type === 'warning' ? 'text-yellow-600' :
                        'text-gray-600'
                      }`}
                    >
                      <span className="text-gray-400">[{log.timestamp}]</span>
                      {log.filename && (
                        <span className="text-gray-500">{log.filename}:</span>
                      )}
                      <span>{log.message}</span>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        {/* Error Summary */}
        {errorCount > 0 && currentPhase === 'complete' && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>
              {errorCount} file{errorCount > 1 ? 's' : ''} failed to process. 
              Check the logs above for details.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}