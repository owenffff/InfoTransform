'use client';

import { FileReviewStatus } from '@/types';
import { Button } from '@/components/ui/button';
import { Download, FileText, FileSpreadsheet, Music } from 'lucide-react';
import { getDocumentUrl, getFileTypeLabel, getContextualMessage } from '@/lib/document-utils';

interface MarkdownInfoBannerProps {
  file: FileReviewStatus;
}

export function MarkdownInfoBanner({ file }: MarkdownInfoBannerProps) {
  const getFileIcon = () => {
    switch (file.document_type) {
      case 'office':
        return <FileSpreadsheet className="w-5 h-5 text-blue-600" />;
      case 'audio':
        return <Music className="w-5 h-5 text-blue-600" />;
      default:
        return <FileText className="w-5 h-5 text-blue-600" />;
    }
  };

  return (
    <div 
      role="status" 
      aria-live="polite" 
      className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg"
    >
      <div className="sr-only">
        {file.document_type === 'office' ? 'Office document' : 'This file'} 
        {' '}cannot be previewed. Showing extracted content.
      </div>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {getFileIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-medium text-sm text-gray-900">{file.filename}</span>
            <span className="text-xs text-gray-500">·</span>
            <span className="text-xs text-gray-600">{getFileTypeLabel(file.document_type)}</span>
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {getContextualMessage(file.document_type)}
          </p>
        </div>
        <Button 
          size="sm" 
          variant="outline"
          className="flex-shrink-0 border-blue-300 text-blue-700 hover:bg-blue-100"
          asChild
        >
          <a href={getDocumentUrl(file.document_url)} download={file.filename}>
            <Download className="w-4 h-4 mr-1.5" />
            Download
          </a>
        </Button>
      </div>
    </div>
  );
}
