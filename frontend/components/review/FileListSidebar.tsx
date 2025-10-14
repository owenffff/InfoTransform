'use client';

import { useState } from 'react';
import { FileReviewStatus } from '@/types';
import { useReviewStore } from '@/lib/store';
import { FileText, Image, FileAudio, FileArchive, Check, X, Circle, ChevronDown, ChevronRight, Menu, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface FileListSidebarProps {
  files: FileReviewStatus[];
}

export function FileListSidebar({ files }: FileListSidebarProps) {
  const { currentFileIndex, setCurrentFile, isSidebarCollapsed, toggleSidebar } = useReviewStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedZips, setExpandedZips] = useState<Set<string>>(new Set());

  const truncateFilename = (filename: string, maxLength = 30) => {
    if (filename.length <= maxLength) return filename;
    const ext = filename.substring(filename.lastIndexOf('.'));
    const nameOnly = filename.substring(0, filename.lastIndexOf('.'));
    const charsForName = maxLength - ext.length - 3;
    if (charsForName <= 0) return filename.substring(0, maxLength - 3) + '...';
    const partLength = Math.floor(charsForName / 2);
    return nameOnly.substring(0, partLength) + '...' + nameOnly.substring(nameOnly.length - partLength) + ext;
  };

  const groupedFiles = files.reduce((acc, file, index) => {
    if (file.source_file) {
      if (!acc[file.source_file]) {
        acc[file.source_file] = [];
      }
      acc[file.source_file].push({ file, index });
    } else {
      acc[file.filename] = [{ file, index }];
    }
    return acc;
  }, {} as Record<string, Array<{ file: FileReviewStatus; index: number }>>);

  const filteredGroups = Object.entries(groupedFiles).filter(([key, items]) => {
    if (!searchQuery) return true;
    return key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      items.some(({ file }) => file.filename.toLowerCase().includes(searchQuery.toLowerCase()));
  });

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText className="w-4 h-4" />;
      case 'image':
        return <Image className="w-4 h-4" />;
      case 'audio':
        return <FileAudio className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <Check className="w-4 h-4 text-green-500" />;
      case 'rejected':
      case 'has_errors':
        return <X className="w-4 h-4 text-red-500" />;
      case 'in_review':
        return <Circle className="w-4 h-4 text-amber-500 fill-amber-500" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const toggleZip = (zipName: string) => {
    const newExpanded = new Set(expandedZips);
    if (newExpanded.has(zipName)) {
      newExpanded.delete(zipName);
    } else {
      newExpanded.add(zipName);
    }
    setExpandedZips(newExpanded);
  };

  const approvedCount = files.filter(f => f.status === 'approved').length;

  if (isSidebarCollapsed) {
    return (
      <div className="w-12 bg-brand-gray-50 border-r flex flex-col items-center py-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSidebar}
          className="w-8 h-8 p-0"
        >
          <Menu className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="w-80 bg-brand-gray-50 border-r flex flex-col">
      <div className="p-4 border-b bg-white">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-sm">Files</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="w-8 h-8 p-0"
          >
            <Menu className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-9"
          />
        </div>
        
        <div className="mt-3 text-xs text-black">
          {approvedCount} of {files.length} approved
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {filteredGroups.map(([groupKey, items]) => {
            const isZip = items.length > 1 || items[0].file.is_zip_content;
            const isExpanded = expandedZips.has(groupKey);

            if (isZip && items.length > 1) {
              return (
                <div key={groupKey} className="mb-1">
                  <button
                    onClick={() => toggleZip(groupKey)}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded hover:bg-brand-gray-100 text-sm"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4" />
                    ) : (
                      <ChevronRight className="w-4 h-4" />
                    )}
                    <FileArchive className="w-4 h-4 text-gray-600" />
                    <span className="flex-1 text-left" title={groupKey}>{truncateFilename(groupKey)}</span>
                    <span className="text-xs text-brand-gray-500">({items.length})</span>
                  </button>
                  
                  {isExpanded && (
                    <div className="ml-6 mt-1 space-y-1">
                      {items.map(({ file, index }) => (
                        <button
                          key={file.file_id}
                          onClick={() => setCurrentFile(index)}
                          className={cn(
                            'w-full flex items-center gap-2 px-3 py-2 rounded text-sm transition-colors',
                            currentFileIndex === index
                              ? 'bg-brand-orange-100 text-black'
                              : 'hover:bg-brand-gray-100'
                          )}
                        >
                          {getStatusIcon(file.status)}
                          {getFileIcon(file.document_type)}
                          <span className="flex-1 text-left text-xs" title={file.filename}>
                            {truncateFilename(file.filename, 25)}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            } else {
              const { file, index } = items[0];
              return (
                <button
                  key={file.file_id}
                  onClick={() => setCurrentFile(index)}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 rounded text-sm transition-colors',
                    currentFileIndex === index
                      ? 'bg-brand-orange-100 text-black'
                      : 'hover:bg-brand-gray-100'
                  )}
                >
                  {getStatusIcon(file.status)}
                  {getFileIcon(file.document_type)}
                  <span className="flex-1 text-left" title={file.filename}>
                    {truncateFilename(file.filename)}
                  </span>
                </button>
              );
            }
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
