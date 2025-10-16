'use client';

import { useEffect, useRef, useState, useMemo } from 'react';
import { CheckCircle, XCircle, Clock, Activity, ChevronDown, ChevronRight, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader as AiLoader } from '@/components/ai-elements/loader';
import { Progress } from '@/components/ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Separator } from '@/components/ui/separator';
import { useStore } from '@/lib/store';
import { cn } from '@/lib/utils';

export interface StreamingEvent {
  type: 'start' | 'markdown_conversion' | 'conversion_progress' | 'ai_analysis' | 'result' | 'complete' | 'error' | 'reset';
  filename?: string;
  status?: 'success' | 'error' | 'processing';
  message?: string;
  error?: string;
  progress?: number;
  current?: number;
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

// File task types
type FileTaskStatus = 'pending' | 'in_progress' | 'completed' | 'error';

interface FileTask {
  filename: string;
  status: FileTaskStatus;
  currentPhase: string;
  error?: string;
  startTime?: number;
  processingTime?: number;
}

// Timer component for live duration display
function Timer({ startTime }: { startTime: number }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const seconds = Math.floor((Date.now() - startTime) / 1000);
      setElapsed(seconds);
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return <span>{formatTime(elapsed)}</span>;
}

// FileStatusRow component - displays single file status
function FileStatusRow({ file }: { file: FileTask }) {
  const { status, filename, currentPhase, error, startTime, processingTime } = file;

  return (
    <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-muted/50 transition-colors text-sm">
      {/* Icon */}
      <div className="flex-shrink-0">
        {status === 'in_progress' && (
          <AiLoader size={16} className="text-blue-600" />
        )}
        {status === 'completed' && (
          <CheckCircle2 className="w-4 h-4 text-green-600" />
        )}
        {status === 'error' && (
          <XCircle className="w-4 h-4 text-red-600" />
        )}
        {status === 'pending' && (
          <Clock className="w-4 h-4 text-gray-400" />
        )}
      </div>

      {/* Filename */}
      <div className="flex-1 font-mono text-xs truncate min-w-0">
        {filename}
      </div>

      {/* Status Message */}
      <div className="flex-shrink-0 text-xs text-muted-foreground min-w-[180px]">
        {status === 'in_progress' && currentPhase}
        {status === 'completed' && 'Analyzed successfully'}
        {status === 'error' && (error || 'Processing failed')}
        {status === 'pending' && 'Waiting...'}
      </div>

      {/* Duration/Timer */}
      <div className="flex-shrink-0 text-xs text-muted-foreground font-mono w-14 text-right">
        {status === 'completed' && processingTime && `${processingTime}s`}
        {status === 'error' && '--'}
        {status === 'in_progress' && startTime && <Timer startTime={startTime} />}
        {status === 'pending' && '--'}
      </div>
    </div>
  );
}

export function ProcessingStatus() {
  // Existing state for progress tracking
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

  // NEW: File tracking state for detailed list
  const [tasks, setTasks] = useState<Record<string, FileTask>>({});

  // NEW: Collapsible state
  const [isFileDetailsOpen, setIsFileDetailsOpen] = useState(true);
  const [hasManuallyToggled, setHasManuallyToggled] = useState(false);
  const [hasAutoCollapsed, setHasAutoCollapsed] = useState(false);

  const ensureTask = (filename: string) => {
    setTasks((prev) => {
      if (prev[filename]) return prev;
      return {
        ...prev,
        [filename]: {
          filename,
          status: 'pending',
          currentPhase: 'Waiting...',
        },
      };
    });
  };

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
          // Reset file tracking
          setTasks({});
          setIsFileDetailsOpen(true);
          setHasManuallyToggled(false);
          setHasAutoCollapsed(false);
          break;

        case 'start':
          setTotalCount(event.total && event.total > 0 ? event.total : (selectedFiles?.length ?? 0));
          setProcessedCount(0);
          setSuccessCount(0);
          setErrorCount(0);
          setStartTime(Date.now());
          finishedFilesRef.current.clear();
          // Reset file details to expanded on new processing
          setIsFileDetailsOpen(true);
          setHasManuallyToggled(false);
          setHasAutoCollapsed(false);
          break;

        case 'markdown_conversion':
          if (event.filename) {
            setCurrentFile(event.filename);
            setCurrentPhase('converting');
            // Update file task
            ensureTask(event.filename);
            setTasks(prev => ({
              ...prev,
              [event.filename!]: {
                ...prev[event.filename!],
                status: 'in_progress',
                currentPhase: 'Converting to markdown',
                startTime: prev[event.filename!]?.startTime || Date.now(),
              }
            }));
          }
          if (event.progress && event.total) {
            const progress = (event.progress / event.total) * 50; // 50% for conversion
            setOverallProgress(progress);
            updateTimeEstimate(event.progress, event.total, startTime);
          }
          break;

        case 'conversion_progress':
          if (event.filename) {
            setCurrentFile(event.filename);
            // Update file task
            ensureTask(event.filename);
            setTasks(prev => ({
              ...prev,
              [event.filename!]: {
                ...prev[event.filename!],
                status: 'in_progress',
                currentPhase: 'Converting to markdown',
                startTime: prev[event.filename!]?.startTime || Date.now(),
              }
            }));
          }
          if (event.current && event.total) {
            const progress = (event.current / event.total) * 50; // 50% for conversion
            setOverallProgress(progress);
            updateTimeEstimate(event.current, event.total, startTime);
          }
          break;

        case 'ai_analysis':
          if (event.filename) {
            setCurrentFile(event.filename);
            setCurrentPhase('analyzing');
            // Update file task
            ensureTask(event.filename);
            setTasks(prev => ({
              ...prev,
              [event.filename!]: {
                ...prev[event.filename!],
                status: 'in_progress',
                currentPhase: 'Analyzing with AI',
                startTime: prev[event.filename!]?.startTime || Date.now(),
              }
            }));
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
                // Update file task to completed
                setTasks(prev => {
                  const startTime = prev[fname]?.startTime || Date.now();
                  const processingTime = Math.round((Date.now() - startTime) / 1000);

                  return {
                    ...prev,
                    [fname]: {
                      ...prev[fname],
                      status: 'completed',
                      currentPhase: 'Completed',
                      processingTime,
                    }
                  };
                });
              } else if (event.status === 'error') {
                setErrorCount(prev => prev + 1);
                // Update file task to error
                setTasks(prev => ({
                  ...prev,
                  [fname]: {
                    ...prev[fname],
                    status: 'error',
                    currentPhase: 'Failed',
                    error: event.error || 'Processing failed',
                  }
                }));
              }
              setProcessedCount(prev => prev + 1);
            }
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
  }, [startTime, handlerId, selectedFiles]);

  // Smart auto-collapse logic
  useEffect(() => {
    if (currentPhase === 'complete' && !hasAutoCollapsed && !hasManuallyToggled) {
      const allFiles = Object.values(tasks);
      const failedFiles = allFiles.filter(f => f.status === 'error');

      if (failedFiles.length === 0) {
        // No errors: auto-collapse
        setIsFileDetailsOpen(false);
      } else {
        // Has errors: ensure expanded
        setIsFileDetailsOpen(true);
      }
      setHasAutoCollapsed(true);
    }
  }, [currentPhase, tasks, hasAutoCollapsed, hasManuallyToggled]);

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

  // Handle manual collapse toggle
  const handleCollapseToggle = (open: boolean) => {
    setIsFileDetailsOpen(open);
    setHasManuallyToggled(true); // Prevent auto-collapse override
  };

  // Group files by status
  const { processingFiles, completedFiles, failedFiles, pendingFiles } = useMemo(() => {
    const allFiles = Object.values(tasks);
    return {
      processingFiles: allFiles.filter(f => f.status === 'in_progress'),
      completedFiles: allFiles.filter(f => f.status === 'completed'),
      failedFiles: allFiles.filter(f => f.status === 'error'),
      pendingFiles: allFiles.filter(f => f.status === 'pending'),
    };
  }, [tasks]);

  const totalFiles = Object.keys(tasks).length;

  return (
    <Card className="shadow-lg border-gray-200" role="region" aria-label="File processing status">
      <CardHeader className="pb-4">
        <CardTitle className="text-xl flex items-center gap-2">
          Processing Status
          {currentPhase !== 'complete' ? (
            <Badge variant="default" className="ml-auto">Processing</Badge>
          ) : (
            <Badge variant="secondary" className="ml-auto">Complete</Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Screen reader live region for progress updates */}
        <div className="sr-only" role="status" aria-live="polite" aria-atomic="true">
          {currentPhase === 'converting' && `Converting files: ${Math.round(overallProgress)}% complete. ${currentFile ? `Currently processing ${currentFile}` : ''}`}
          {currentPhase === 'analyzing' && `Analyzing files with AI: ${Math.round(overallProgress)}% complete. ${currentFile ? `Currently processing ${currentFile}` : ''}`}
          {currentPhase === 'complete' && `Transformation complete. ${successCount} successful, ${errorCount} failed.`}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-medium text-muted-foreground">
              {Math.round(overallProgress)}%
            </span>
          </div>
          <Progress
            value={overallProgress}
            className="h-2 transition-all duration-500"
            aria-label={`Overall progress: ${Math.round(overallProgress)}%`}
            aria-valuenow={Math.round(overallProgress)}
            aria-valuemin={0}
            aria-valuemax={100}
          />

          {/* One-line Summary */}
          <div className="flex items-center justify-between text-sm text-muted-foreground pt-1">
            <div className="flex items-center gap-3">
              <span>{Math.min(processedCount, totalCount || processedCount)}/{totalCount} files</span>
              {successCount > 0 && (
                <span className="text-green-600 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  {successCount} success
                </span>
              )}
              {errorCount > 0 && (
                <span className="text-red-600 flex items-center gap-1">
                  <XCircle className="w-3 h-3" />
                  {errorCount} failed
                </span>
              )}
            </div>
            {estimatedTimeRemaining && currentPhase !== 'complete' && (
              <span className="text-xs flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {estimatedTimeRemaining}
              </span>
            )}
          </div>
        </div>

        {/* Collapsible File Details Section */}
        {totalFiles > 0 && (
          <Collapsible open={isFileDetailsOpen} onOpenChange={handleCollapseToggle}>
            <div className="pt-3">
              <Separator className="mb-3" />

              <CollapsibleTrigger asChild>
                <button
                  className="w-full flex items-center justify-between text-sm font-medium hover:bg-muted/50 p-2 rounded-md transition-colors"
                  aria-expanded={isFileDetailsOpen}
                  aria-controls="file-details-content"
                  aria-label={`${isFileDetailsOpen ? 'Hide' : 'Show'} file details (${totalFiles} files)`}
                >
                  <div className="flex items-center gap-2">
                    {isFileDetailsOpen ? (
                      <ChevronDown className="w-4 h-4" />
                    ) : (
                      <ChevronRight className="w-4 h-4" />
                    )}
                    <span>File Details ({totalFiles})</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {isFileDetailsOpen ? 'Hide' : 'Show'}
                  </span>
                </button>
              </CollapsibleTrigger>

              <CollapsibleContent
                id="file-details-content"
                role="region"
                aria-label="File processing details"
                className="overflow-hidden data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0"
              >
                <div className="pt-3 space-y-4">
                  {/* Processing Section */}
                  {processingFiles.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-blue-600" />
                        Processing ({processingFiles.length})
                      </h4>
                      <div className="space-y-1">
                        {processingFiles.map(file => (
                          <FileStatusRow key={file.filename} file={file} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Pending Section */}
                  {pendingFiles.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-gray-400" />
                        Pending ({pendingFiles.length})
                      </h4>
                      <div className="space-y-1">
                        {pendingFiles.map(file => (
                          <FileStatusRow key={file.filename} file={file} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Failed Section - Always show if errors */}
                  {failedFiles.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-red-600 mb-2 flex items-center gap-2">
                        <XCircle className="w-4 h-4" />
                        Failed ({failedFiles.length})
                      </h4>
                      <div className="space-y-1">
                        {failedFiles.map(file => (
                          <FileStatusRow key={file.filename} file={file} />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Completed Section */}
                  {completedFiles.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600" />
                        Completed ({completedFiles.length})
                      </h4>
                      <div className="space-y-1">
                        {completedFiles.map(file => (
                          <FileStatusRow key={file.filename} file={file} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CollapsibleContent>
            </div>
          </Collapsible>
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
