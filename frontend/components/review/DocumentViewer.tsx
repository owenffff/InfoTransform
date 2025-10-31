'use client';

import { useState, useEffect } from 'react';
import { FileReviewStatus, MarkdownResponse } from '@/types';
import { useReviewStore } from '@/lib/store';
import { getMarkdownContent } from '@/lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { FileText, Download, AlertCircle, Loader2, FileSpreadsheet, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { getDocumentUrl, canPreviewNatively } from '@/lib/document-utils';
import { SourceEmptyState } from './SourceEmptyState';
import { MarkdownInfoBanner } from './MarkdownInfoBanner';
import MarkdownRenderer from './MarkdownRenderer';

interface DocumentViewerProps {
  file: FileReviewStatus;
}

export function DocumentViewer({ file }: DocumentViewerProps) {
  const { activeSourceTab, setActiveSourceTab, currentSession } = useReviewStore();
  const [markdown, setMarkdown] = useState<MarkdownResponse | null>(null);

  useEffect(() => {
    if (!canPreviewNatively(file.document_type)) {
      setActiveSourceTab('markdown');
    }
  }, [file.file_id, file.document_type, setActiveSourceTab]);

  useEffect(() => {
    if (currentSession && activeSourceTab === 'markdown') {
      getMarkdownContent(currentSession.session_id, file.file_id)
        .then(data => setMarkdown(data))
        .catch(err => console.error('Failed to load markdown:', err));
    }
  }, [file.file_id, activeSourceTab, currentSession]);

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="border-b p-3">
        <Tabs value={activeSourceTab} onValueChange={(v) => setActiveSourceTab(v as 'source' | 'markdown')}>
          <TabsList>
            <TabsTrigger value="source">Source</TabsTrigger>
            <TabsTrigger value="markdown">Markdown</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          {activeSourceTab === 'source' ? (
            <SourceViewer 
              file={file} 
              onSwitchToMarkdown={() => setActiveSourceTab('markdown')}
            />
          ) : (
            <MarkdownViewer markdown={markdown} file={file} />
          )}
        </ScrollArea>
      </div>
    </div>
  );
}

function SourceViewer({ file, onSwitchToMarkdown }: { file: FileReviewStatus; onSwitchToMarkdown: () => void }) {
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const [imageErrorDetails, setImageErrorDetails] = useState<{ status?: number; message: string }>({ message: 'Unknown error' });
  const [imageRetryKey, setImageRetryKey] = useState(0);
  const [pdfError, setPdfError] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(true);
  const [audioError, setAudioError] = useState(false);
  const [audioLoading, setAudioLoading] = useState(true);

  // Reset all states when file changes
  useEffect(() => {
    setImageLoading(true);
    setImageError(false);
    setImageErrorDetails({ message: 'Unknown error' });
    setPdfLoading(true);
    setPdfError(false);
    setAudioLoading(true);
    setAudioError(false);
  }, [file.file_id]);

  // Timeout mechanism for image loading
  useEffect(() => {
    if (file.document_type !== 'image') return;

    const timeout = setTimeout(() => {
      if (imageLoading && !imageError) {
        setImageLoading(false);
        setImageError(true);
        setImageErrorDetails({
          message: 'Image loading timed out after 10 seconds'
        });
      }
    }, 10000); // 10 second timeout

    return () => clearTimeout(timeout);
  }, [file.file_id, file.document_type, imageLoading, imageError]);

  // Timeout mechanism for PDF loading
  useEffect(() => {
    if (file.document_type !== 'pdf') return;

    const timeout = setTimeout(() => {
      if (pdfLoading && !pdfError) {
        setPdfLoading(false);
        setPdfError(true);
      }
    }, 15000); // 15 second timeout

    return () => clearTimeout(timeout);
  }, [file.file_id, file.document_type, pdfLoading, pdfError]);

  // Timeout mechanism for audio loading
  useEffect(() => {
    if (file.document_type !== 'audio') return;

    const timeout = setTimeout(() => {
      if (audioLoading && !audioError) {
        setAudioLoading(false);
        setAudioError(true);
      }
    }, 8000); // 8 second timeout

    return () => clearTimeout(timeout);
  }, [file.file_id, file.document_type, audioLoading, audioError]);

  if (!canPreviewNatively(file.document_type) && file.document_type !== 'audio') {
    return <SourceEmptyState file={file} onSwitchToMarkdown={onSwitchToMarkdown} />;
  }

  if (file.document_type === 'image') {
    return (
      <div className="p-4 flex items-center justify-center">
        {imageLoading && (
          <div className="w-full max-w-2xl space-y-3">
            <Skeleton className="h-[400px] w-full rounded-lg" />
            <Skeleton className="h-4 w-[200px] mx-auto" />
          </div>
        )}
        {imageError && (
          <div className="w-full max-w-2xl">
            <Card className="border-destructive/50">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
                  <div className="flex-1">
                    <CardTitle className="text-destructive">Failed to Load Image</CardTitle>
                    <CardDescription className="mt-2">
                      {imageErrorDetails.status === 404
                        ? 'The file could not be found on the server. It may have been moved or deleted.'
                        : imageErrorDetails.status === 403
                        ? 'Access to this file was denied by the server.'
                        : imageErrorDetails.message === 'Network error - cannot reach server'
                        ? 'Unable to connect to the server. Please check your network connection.'
                        : 'The image preview could not be displayed.'}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <FileText className="h-4 w-4" />
                  <AlertTitle>Document Details</AlertTitle>
                  <AlertDescription>
                    <div className="space-y-1">
                      <div><span className="font-medium">{file.filename}</span></div>
                      <div className="text-xs">Type: {file.document_type}</div>
                      {imageErrorDetails.status && (
                        <div className="text-xs text-destructive">
                          Status: {imageErrorDetails.status} - {imageErrorDetails.message}
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setImageError(false);
                      setImageLoading(true);
                      setImageErrorDetails({ message: 'Unknown error' });
                      setImageRetryKey(prev => prev + 1); // Force image to reload
                    }}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                  <Button asChild className="bg-brand-orange-500 hover:bg-brand-orange-600">
                    <a href={getDocumentUrl(file.document_url)} download={file.filename}>
                      <Download className="w-4 h-4 mr-2" />
                      Download File
                    </a>
                  </Button>
                </div>

                {process.env.NODE_ENV === 'development' && (
                  <Alert>
                    <AlertTitle className="text-xs">Debug Information</AlertTitle>
                    <AlertDescription className="font-mono text-xs space-y-1">
                      <div>URL: {getDocumentUrl(file.document_url)}</div>
                      <div>Session: {file.document_url}</div>
                      <div>Error: {imageErrorDetails.message}</div>
                    </AlertDescription>
                  </Alert>
                )}

                <p className="text-xs text-muted-foreground">
                  Tip: Switch to the Markdown tab to view extracted content
                </p>
              </CardContent>
            </Card>
          </div>
        )}
        <img
          key={`image-${file.file_id}-${imageRetryKey}`}
          src={getDocumentUrl(file.document_url)}
          alt={file.filename}
          style={{ display: imageLoading || imageError ? 'none' : 'block' }}
          className="max-w-full h-auto"
          onLoad={() => {
            console.log('[DocumentViewer] Image loaded successfully:', getDocumentUrl(file.document_url));
            setImageLoading(false);
          }}
          onError={async () => {
            console.error('[DocumentViewer] Image failed to load:', getDocumentUrl(file.document_url));
            setImageLoading(false);
            setImageError(true);

            // Try to get error details
            const url = getDocumentUrl(file.document_url);
            try {
              const response = await fetch(url, { method: 'HEAD' });
              console.log('[DocumentViewer] HEAD response:', response.status, response.statusText);
              if (!response.ok) {
                setImageErrorDetails({
                  status: response.status,
                  message: response.status === 404
                    ? 'File not found on server'
                    : response.status === 403
                    ? 'Access denied'
                    : response.status === 500
                    ? 'Server error'
                    : `HTTP ${response.status}`
                });
              }
            } catch (err) {
              console.error('[DocumentViewer] HEAD request failed:', err);
              setImageErrorDetails({
                message: 'Network error - cannot reach server'
              });
            }
          }}
        />
      </div>
    );
  }

  if (file.document_type === 'audio') {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-brand-orange-50 rounded-lg">
                  <FileText className="w-6 h-6 text-brand-orange-500" />
                </div>
                <div>
                  <CardTitle>{file.filename}</CardTitle>
                  <CardDescription>Audio File</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {audioLoading && !audioError && (
                <div className="flex items-center justify-center p-4 bg-gray-50 rounded-lg">
                  <Loader2 className="w-5 h-5 animate-spin text-brand-orange-500 mr-2" />
                  <span className="text-sm text-gray-600">Loading audio...</span>
                </div>
              )}

              {audioError && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Audio Playback Failed</AlertTitle>
                  <AlertDescription>
                    The audio file could not be loaded. This may be due to an unsupported format, network error, or the file may be corrupted.
                  </AlertDescription>
                </Alert>
              )}

              <audio
                key={`audio-${file.file_id}`}
                controls
                className="w-full"
                style={{ display: audioError ? 'none' : 'block' }}
                onLoadedData={() => {
                  console.log('[DocumentViewer] Audio loaded successfully');
                  setAudioLoading(false);
                }}
                onError={(e) => {
                  console.error('[DocumentViewer] Audio failed to load:', e);
                  setAudioLoading(false);
                  setAudioError(true);
                }}
                onCanPlayThrough={() => {
                  setAudioLoading(false);
                }}
              >
                <source src={getDocumentUrl(file.document_url)} />
                Your browser does not support the audio element.
              </audio>

              {audioError && (
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setAudioError(false);
                      setAudioLoading(true);
                    }}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry
                  </Button>
                  <Button asChild className="bg-brand-orange-500 hover:bg-brand-orange-600">
                    <a href={getDocumentUrl(file.document_url)} download={file.filename}>
                      <Download className="w-4 h-4 mr-2" />
                      Download Audio
                    </a>
                  </Button>
                </div>
              )}

              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  💡 Switch to the Markdown tab to view the audio transcript
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (file.document_type === 'pdf') {
    return (
      <div className="p-4">
        {pdfLoading && !pdfError && (
          <div className="space-y-3">
            <Skeleton className="h-[calc(100vh-250px)] w-full rounded-lg" />
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <Skeleton className="h-4 w-[150px]" />
            </div>
          </div>
        )}
        {pdfError && (
          <div className="max-w-2xl mx-auto">
            <Card className="border-destructive/50">
              <CardHeader>
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-destructive mt-0.5" />
                  <div className="flex-1">
                    <CardTitle className="text-destructive">PDF Preview Failed</CardTitle>
                    <CardDescription className="mt-2">
                      The PDF could not be displayed. This may be due to:
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        <li>Browser doesn't support inline PDF viewing</li>
                        <li>PDF took too long to load (timeout after 15 seconds)</li>
                        <li>Network connection issue</li>
                        <li>File may be corrupted or password-protected</li>
                      </ul>
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <Alert>
                  <FileText className="h-4 w-4" />
                  <AlertTitle>Document Information</AlertTitle>
                  <AlertDescription>
                    <span className="font-medium">{file.filename}</span>
                  </AlertDescription>
                </Alert>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setPdfError(false);
                      setPdfLoading(true);
                    }}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry Preview
                  </Button>
                  <Button asChild className="bg-brand-orange-500 hover:bg-brand-orange-600">
                    <a href={getDocumentUrl(file.document_url)} download={file.filename} target="_blank" rel="noopener noreferrer">
                      <Download className="w-4 h-4 mr-2" />
                      Open in New Tab
                    </a>
                  </Button>
                </div>

                <p className="text-xs text-muted-foreground">
                  💡 Tip: Switch to the Markdown tab to view extracted text content, or open the PDF in a new tab for better compatibility
                </p>
              </CardContent>
            </Card>
          </div>
        )}
        {!pdfError && (
          <iframe
            key={`pdf-${file.file_id}`}
            src={getDocumentUrl(file.document_url)}
            className="w-full h-[calc(100vh-200px)] border border-gray-200 rounded-lg"
            style={{ display: pdfLoading ? 'none' : 'block' }}
            title={`PDF: ${file.filename}`}
            onLoad={() => {
              console.log('[DocumentViewer] PDF iframe loaded successfully');
              setPdfLoading(false);
            }}
            onError={() => {
              console.error('[DocumentViewer] PDF iframe failed to load');
              setPdfLoading(false);
              setPdfError(true);
            }}
          />
        )}
      </div>
    );
  }

  if (file.document_type === 'office') {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="p-4 bg-brand-orange-50 rounded-xl">
                  <FileSpreadsheet className="w-12 h-12 text-brand-orange-500" />
                </div>
              </div>
              <CardTitle>{file.filename}</CardTitle>
              <CardDescription>
                Office documents cannot be previewed directly in the browser
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button asChild className="w-full bg-brand-orange-500 hover:bg-brand-orange-600">
                <a href={getDocumentUrl(file.document_url)} download={file.filename}>
                  <Download className="w-4 h-4 mr-2" />
                  Download File
                </a>
              </Button>
              
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  Tip: Switch to the Markdown tab to view the extracted content
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="p-4 bg-brand-gray-100 rounded-xl">
                <FileText className="w-12 h-12 text-brand-gray-500" />
              </div>
            </div>
            <CardTitle>Preview Not Available</CardTitle>
            <CardDescription>
              This file type cannot be previewed directly in the browser
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button asChild className="w-full bg-brand-orange-500 hover:bg-brand-orange-600">
              <a href={getDocumentUrl(file.document_url)} download={file.filename}>
                <Download className="w-4 h-4 mr-2" />
                Download File
              </a>
            </Button>
            
            <Alert>
              <FileText className="h-4 w-4" />
              <AlertDescription>
                Switch to the Markdown tab to view the extracted content
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MarkdownViewer({ markdown, file }: { markdown: MarkdownResponse | null; file: FileReviewStatus }) {
  if (!markdown) {
    return (
      <div className="p-8">
        <div className="space-y-3 max-w-2xl mx-auto">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {!canPreviewNatively(file.document_type) && (
        <MarkdownInfoBanner file={file} />
      )}
      
      {markdown.was_summarized && (
        <div className="mb-4 p-3 bg-yellow-50 rounded-lg text-sm">
          <p className="text-yellow-800">
            ⚠️ Content was summarized due to length
          </p>
        </div>
      )}

      <MarkdownRenderer
        content={markdown.markdown_content}
        className="bg-white rounded-lg"
      />
    </div>
  );
}
