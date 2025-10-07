'use client';

import { useState, useEffect } from 'react';
import { FileReviewStatus, MarkdownResponse } from '@/types';
import { useReviewStore } from '@/lib/store';
import { getMarkdownContent } from '@/lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, FileText } from 'lucide-react';

interface DocumentViewerProps {
  file: FileReviewStatus;
}

export function DocumentViewer({ file }: DocumentViewerProps) {
  const { activeSourceTab, setActiveSourceTab, currentSession } = useReviewStore();
  const [markdown, setMarkdown] = useState<MarkdownResponse | null>(null);
  const [zoom, setZoom] = useState(100);

  useEffect(() => {
    if (currentSession && activeSourceTab === 'markdown') {
      getMarkdownContent(currentSession.session_id, file.file_id)
        .then(data => setMarkdown(data))
        .catch(err => console.error('Failed to load markdown:', err));
    }
  }, [file.file_id, activeSourceTab, currentSession]);

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="border-b p-3 flex items-center justify-between">
        <Tabs value={activeSourceTab} onValueChange={(v) => setActiveSourceTab(v as 'source' | 'markdown')} className="w-full">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="source">Source</TabsTrigger>
              <TabsTrigger value="markdown">Markdown</TabsTrigger>
            </TabsList>
            
            {activeSourceTab === 'source' && file.document_type !== 'audio' && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setZoom(Math.max(50, zoom - 25))}
                  disabled={zoom <= 50}
                >
                  <ZoomOut className="w-4 h-4" />
                </Button>
                <span className="text-sm text-gray-600 min-w-[60px] text-center">
                  {zoom}%
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setZoom(Math.min(200, zoom + 25))}
                  disabled={zoom >= 200}
                >
                  <ZoomIn className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>
        </Tabs>
      </div>

      <ScrollArea className="flex-1">
        {activeSourceTab === 'source' ? (
          <SourceViewer file={file} zoom={zoom} />
        ) : (
          <MarkdownViewer markdown={markdown} />
        )}
      </ScrollArea>
    </div>
  );
}

function SourceViewer({ file, zoom }: { file: FileReviewStatus; zoom: number }) {
  if (file.document_type === 'image') {
    return (
      <div className="p-4 flex items-center justify-center">
        <img
          src={file.document_url}
          alt={file.filename}
          style={{ width: `${zoom}%` }}
          className="max-w-full h-auto"
        />
      </div>
    );
  }

  if (file.document_type === 'audio') {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <FileText className="w-8 h-8 text-gray-600" />
              <div>
                <h3 className="font-medium">{file.filename}</h3>
                <p className="text-sm text-gray-600">Audio File</p>
              </div>
            </div>
            
            <audio controls className="w-full">
              <source src={file.document_url} />
              Your browser does not support the audio element.
            </audio>
          </div>
          
          <p className="text-sm text-gray-600 text-center">
            Switch to the Markdown tab to view the transcript
          </p>
        </div>
      </div>
    );
  }

  if (file.document_type === 'pdf') {
    return (
      <div className="p-4">
        <iframe
          src={file.document_url}
          className="w-full h-[calc(100vh-200px)] border-0"
          style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top left' }}
        />
      </div>
    );
  }

  return (
    <div className="p-8 text-center text-gray-600">
      <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
      <p>Preview not available for this file type.</p>
      <p className="text-sm mt-2">Switch to Markdown tab to view the extracted content.</p>
    </div>
  );
}

function MarkdownViewer({ markdown }: { markdown: MarkdownResponse | null }) {
  if (!markdown) {
    return (
      <div className="p-8 text-center text-gray-600">
        Loading markdown content...
      </div>
    );
  }

  return (
    <div className="p-6">
      {markdown.was_summarized && (
        <div className="mb-4 p-3 bg-yellow-50 rounded-lg text-sm">
          <p className="text-yellow-800">
            ⚠️ Content was summarized due to length
          </p>
        </div>
      )}
      
      <div className="prose prose-sm max-w-none">
        <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-lg text-sm">
          {markdown.markdown_content}
        </pre>
      </div>
    </div>
  );
}
