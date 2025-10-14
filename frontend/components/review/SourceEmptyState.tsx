'use client';

import { FileReviewStatus } from '@/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Download, FileText, FileSpreadsheet, Music, File } from 'lucide-react';
import { getDocumentUrl, getFileTypeLabel } from '@/lib/document-utils';

interface SourceEmptyStateProps {
  file: FileReviewStatus;
  onSwitchToMarkdown: () => void;
}

export function SourceEmptyState({ file, onSwitchToMarkdown }: SourceEmptyStateProps) {
  const getFileIcon = () => {
    switch (file.document_type) {
      case 'office':
        return <FileSpreadsheet className="w-16 h-16 text-gray-500" />;
      case 'audio':
        return <Music className="w-16 h-16 text-gray-500" />;
      default:
        return <File className="w-16 h-16 text-gray-500" />;
    }
  };

  return (
    <div className="p-8 h-full flex items-center justify-center">
      <div className="max-w-md text-center space-y-6">
        <div className="flex justify-center">
          <div className="p-4 bg-gray-100 rounded-2xl">
            {getFileIcon()}
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-gray-900">
            Source Preview Not Available
          </h3>
          <Badge variant="secondary" className="text-xs">
            {getFileTypeLabel(file.document_type)}
          </Badge>
        </div>
        
        <p className="text-sm text-gray-600 leading-relaxed">
          This document type doesn&apos;t support in-browser preview. 
          The <span className="font-medium">Markdown tab</span> shows 
          AI-extracted content for review and editing.
        </p>
        
        <div className="space-y-3 pt-2">
          <Button 
            onClick={onSwitchToMarkdown}
            className="w-full bg-brand-orange-500 hover:bg-brand-orange-600"
          >
            <FileText className="w-4 h-4 mr-2" />
            View Extracted Content
          </Button>
          
          <Button 
            variant="outline"
            className="w-full"
            asChild
          >
            <a href={getDocumentUrl(file.document_url)} download={file.filename}>
              <Download className="w-4 h-4 mr-2" />
              Download Original File
            </a>
          </Button>
        </div>
      </div>
    </div>
  );
}
