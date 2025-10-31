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
  const [pdfErrorReason, setPdfErrorReason] = useState<string>('');
  const [pdfLoading, setPdfLoading] = useState(true);
  const [pdfVerifying, setPdfVerifying] = useState(false);
  const [audioError, setAudioError] = useState(false);
  const [audioLoading, setAudioLoading] = useState(true);

  // Reset all states when file changes
  useEffect(() => {
    setImageLoading(true);
    setImageError(false);
    setImageErrorDetails({ message: 'Unknown error' });
    setPdfLoading(true);
    setPdfError(false);
    setPdfErrorReason('');
    setPdfVerifying(false);
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
        console.log('[DocumentViewer] PDF loading timed out after 15 seconds');
        setPdfLoading(false);
        setPdfVerifying(false);
        setPdfError(true);
        setPdfErrorReason('timeout');
      }
    }, 15000); // 15 second timeout

    return () => clearTimeout(timeout);
  }, [file.file_id, file.document_type, pdfLoading, pdfError]);

  // Check backend validation headers
  const checkPdfValidationHeaders = async (url: string): Promise<{ issues?: string; encrypted?: boolean }> => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const issues = response.headers.get('X-PDF-Issues');
      const encrypted = response.headers.get('X-PDF-Encrypted');

      return {
        issues: issues || undefined,
        encrypted: encrypted === 'true',
      };
    } catch (error) {
      console.warn('[DocumentViewer] Could not check PDF validation headers:', error);
      return {};
    }
  };

  // Verify PDF content after iframe loads
  const verifyPdfContent = async (iframeElement: HTMLIFrameElement) => {
    console.log('[DocumentViewer] Verifying PDF content...');
    setPdfVerifying(true);

    // First, check backend validation headers
    const url = getDocumentUrl(file.document_url);
    const backendValidation = await checkPdfValidationHeaders(url);

    if (backendValidation.issues) {
      console.warn('[DocumentViewer] Backend detected PDF issues:', backendValidation.issues);

      // Check if backend flagged it as encrypted
      if (backendValidation.encrypted) {
        setPdfLoading(false);
        setPdfVerifying(false);
        setPdfError(true);
        setPdfErrorReason('encrypted');
        return;
      }

      // For other issues, log but continue verification
      console.log('[DocumentViewer] Continuing with frontend verification despite backend warnings');
    }

    // Wait a moment for PDF to fully render
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
      // Check if we can access the iframe's document
      const iframeDoc = iframeElement.contentDocument || iframeElement.contentWindow?.document;

      if (!iframeDoc) {
        console.warn('[DocumentViewer] Cannot access iframe document (possible CORS)');
        // If backend detected issues but we can't verify, show error
        if (backendValidation.issues) {
          setPdfLoading(false);
          setPdfVerifying(false);
          setPdfError(true);
          setPdfErrorReason('corrupted');
          return;
        }
        // Otherwise can't verify - assume it's okay
        setPdfVerifying(false);
        return;
      }

      // Check for common PDF viewer error indicators
      const bodyText = iframeDoc.body?.innerText || '';
      const bodyHTML = iframeDoc.body?.innerHTML || '';

      // Check for blank or minimal content
      if (bodyText.trim().length < 10 && !bodyHTML.includes('embed')) {
        console.error('[DocumentViewer] PDF appears to be blank or failed to render');
        setPdfLoading(false);
        setPdfVerifying(false);
        setPdfError(true);
        setPdfErrorReason('blank');
        return;
      }

      // Check for common error messages
      const errorIndicators = [
        'failed to load',
        'cannot be displayed',
        'error occurred',
        'corrupted',
        'encrypted',
        'password',
      ];

      const lowerBodyText = bodyText.toLowerCase();
      for (const indicator of errorIndicators) {
        if (lowerBodyText.includes(indicator)) {
          console.error('[DocumentViewer] PDF error detected:', indicator);
          setPdfLoading(false);
          setPdfVerifying(false);
          setPdfError(true);
          setPdfErrorReason(indicator.includes('password') || indicator.includes('encrypted') ? 'encrypted' : 'corrupted');
          return;
        }
      }

      console.log('[DocumentViewer] PDF verification passed');
      setPdfVerifying(false);
    } catch (error) {
      // CORS or other access error - can't verify
      console.warn('[DocumentViewer] PDF verification failed (likely CORS):', error);

      // If backend detected issues and we couldn't verify, show error
      if (backendValidation.issues) {
        setPdfLoading(false);
        setPdfVerifying(false);
        setPdfError(true);
        setPdfErrorReason('corrupted');
      } else {
        // Otherwise assume OK
        setPdfVerifying(false);
      }
    }
  };

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
    const getPdfErrorMessage = () => {
      switch (pdfErrorReason) {
        case 'blank':
          return {
            title: 'PDF Shows Blank Page',
            description: 'The PDF file loaded but appears to show a blank page. This could be due to:',
            reasons: [
              'PDF is corrupted or malformed',
              'PDF uses an unsupported encoding',
              'Browser PDF viewer encountered an error',
              'PDF requires special plugins to display',
            ],
          };
        case 'encrypted':
          return {
            title: 'PDF is Password Protected',
            description: 'This PDF file is encrypted and requires a password to view:',
            reasons: [
              'PDF is password-protected or encrypted',
              'You need the password to view this file',
              'Try opening in external PDF viewer with password',
            ],
          };
        case 'corrupted':
          return {
            title: 'PDF May Be Corrupted',
            description: 'The PDF file appears to be damaged or corrupted:',
            reasons: [
              'File may have been corrupted during upload',
              'PDF structure is malformed',
              'File may not be a valid PDF document',
            ],
          };
        case 'timeout':
          return {
            title: 'PDF Loading Timed Out',
            description: 'The PDF took too long to load (15 second timeout):',
            reasons: [
              'PDF file may be very large',
              'Network connection is slow',
              'Server is taking too long to respond',
            ],
          };
        default:
          return {
            title: 'PDF Preview Failed',
            description: 'The PDF could not be displayed. This may be due to:',
            reasons: [
              'Browser doesn\'t support inline PDF viewing',
              'Network connection issue',
              'File may be corrupted or password-protected',
              'PDF uses unsupported features',
            ],
          };
      }
    };

    const errorInfo = getPdfErrorMessage();

    return (
      <div className="p-4">
        {(pdfLoading || pdfVerifying) && !pdfError && (
          <div className="space-y-3">
            <Skeleton className="h-[calc(100vh-250px)] w-full rounded-lg" />
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm text-gray-600">
                {pdfVerifying ? 'Verifying PDF content...' : 'Loading PDF...'}
              </span>
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
                    <CardTitle className="text-destructive">{errorInfo.title}</CardTitle>
                    <CardDescription className="mt-2">
                      {errorInfo.description}
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        {errorInfo.reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
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
                      setPdfErrorReason('');
                      setPdfLoading(true);
                      setPdfVerifying(false);
                    }}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Retry Preview
                  </Button>
                  <Button
                    variant="outline"
                    onClick={onSwitchToMarkdown}
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    View Markdown
                  </Button>
                  <Button asChild className="bg-brand-orange-500 hover:bg-brand-orange-600">
                    <a href={getDocumentUrl(file.document_url)} download={file.filename} target="_blank" rel="noopener noreferrer">
                      <Download className="w-4 h-4 mr-2" />
                      Open in New Tab
                    </a>
                  </Button>
                </div>

                {pdfErrorReason === 'blank' && (
                  <Alert className="bg-blue-50 border-blue-200">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertTitle className="text-blue-900">Recommended Action</AlertTitle>
                    <AlertDescription className="text-blue-800">
                      Since the PDF shows a blank page, we recommend switching to the Markdown tab to view the extracted text content, or opening the PDF in an external viewer.
                    </AlertDescription>
                  </Alert>
                )}

                <p className="text-xs text-muted-foreground">
                  💡 Tip: Switch to the Markdown tab to view extracted text content, or download the PDF to open in an external viewer
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
            style={{ display: pdfLoading || pdfVerifying ? 'none' : 'block' }}
            title={`PDF: ${file.filename}`}
            onLoad={(e) => {
              console.log('[DocumentViewer] PDF iframe loaded, starting verification...');
              setPdfLoading(false);
              // Verify PDF content to detect blank pages
              const iframe = e.currentTarget;
              verifyPdfContent(iframe);
            }}
            onError={() => {
              console.error('[DocumentViewer] PDF iframe failed to load');
              setPdfLoading(false);
              setPdfVerifying(false);
              setPdfError(true);
              setPdfErrorReason('network');
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
