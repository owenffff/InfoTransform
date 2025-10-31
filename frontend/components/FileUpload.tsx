'use client';

import React, { useCallback, useMemo, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  FileText,
  Image,
  Music,
  FileArchive,
  File,
  X,
  Search,
  Trash2
} from 'lucide-react';
import { useStore } from '@/lib/store';
import { showToast } from './Toast';
import { formatFileSize, getFileTypeIcon } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

const ACCEPTED_EXTENSIONS = [
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
  '.pdf', '.docx', '.pptx', '.xlsx',
  '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm',
  '.zip', '.md', '.txt'
];

// Maximum total upload size per session (1 GB)
const MAX_TOTAL_UPLOAD_SIZE = 1024 * 1024 * 1024; // 1 GB in bytes

interface FileGroup {
  type: string;
  icon: React.ReactNode;
  files: File[];
  totalSize: number;
}

export function FileUpload() {
  const { selectedFiles, setSelectedFiles, isProcessing } = useStore();
  const [searchQuery, setSearchQuery] = useState('');
  // Toggle for grouping files by type (replaces "Summary/List" dropdown)
  const [groupByType, setGroupByType] = useState<boolean>(true);
  // Track if component is mounted on client side
  const [isMounted, setIsMounted] = useState(false);

  // Ensure dropzone is only fully interactive after client-side hydration
  useEffect(() => {
    setIsMounted(true);
  }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      showToast('error', 'No valid files selected');
      return;
    }

    // Check for duplicates
    const existingNames = new Set(selectedFiles.map(f => f.name));
    const newFiles = acceptedFiles.filter(f => !existingNames.has(f.name));
    const duplicates = acceptedFiles.length - newFiles.length;

    if (duplicates > 0) {
      showToast('info', `${duplicates} duplicate file(s) ignored`);
    }

    if (newFiles.length > 0) {
      // Calculate current total size
      const currentSize = selectedFiles.reduce((acc, f) => acc + f.size, 0);
      const newSize = newFiles.reduce((acc, f) => acc + f.size, 0);
      const totalSize = currentSize + newSize;

      // Check if adding these files would exceed the limit
      if (totalSize > MAX_TOTAL_UPLOAD_SIZE) {
        const remainingSpace = MAX_TOTAL_UPLOAD_SIZE - currentSize;
        showToast(
          'error',
          `Upload limit exceeded. You can add up to ${formatFileSize(remainingSpace)} more (1 GB max per session)`
        );
        return;
      }

      setSelectedFiles([...selectedFiles, ...newFiles]);
      showToast('success', `${newFiles.length} file(s) added`);
    }
  }, [selectedFiles, setSelectedFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'],
      'application/zip': ['.zip'],
      'text/markdown': ['.md'],
      'text/plain': ['.txt']
    },
    multiple: true,
    disabled: isProcessing || !isMounted,
    noClick: !isMounted,
    noDrag: !isMounted
  });

  // Filter files by search; preserve insertion order (recently added last)
  const filteredFiles = useMemo(() => {
    if (!searchQuery) return selectedFiles;
    return selectedFiles.filter(file =>
      file.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [selectedFiles, searchQuery]);

  // Group files by type (driven by filteredFiles so search affects groups)
  const fileGroups = useMemo(() => {
    const groups: Record<string, FileGroup> = {};
    
    filteredFiles.forEach(file => {
      const extension = file.name.split('.').pop()?.toLowerCase() || '';
      let type = 'Other';
      let icon = <File className="w-4 h-4" />;
      
      if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(extension)) {
        type = 'Images';
        icon = <Image className="w-4 h-4" />;
      } else if (extension === 'pdf') {
        type = 'PDFs';
        icon = <FileText className="w-4 h-4" />;
      } else if (['docx', 'pptx', 'xlsx'].includes(extension)) {
        type = 'Documents';
        icon = <FileText className="w-4 h-4" />;
      } else if (['mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm'].includes(extension)) {
        type = 'Audio';
        icon = <Music className="w-4 h-4" />;
      } else if (extension === 'zip') {
        type = 'Archives';
        icon = <FileArchive className="w-4 h-4" />;
      } else if (['md', 'txt'].includes(extension)) {
        type = 'Text';
        icon = <FileText className="w-4 h-4" />;
      }
      
      if (!groups[type]) {
        groups[type] = { type, icon, files: [], totalSize: 0 };
      }
      
      groups[type].files.push(file);
      groups[type].totalSize += file.size;
    });
    
    return Object.values(groups);
  }, [filteredFiles]);

  const totalSize = useMemo(() =>
    selectedFiles.reduce((acc, file) => acc + file.size, 0),
    [selectedFiles]
  );

  // Calculate upload limit usage
  const uploadLimitPercentage = useMemo(() =>
    Math.round((totalSize / MAX_TOTAL_UPLOAD_SIZE) * 100),
    [totalSize]
  );

  // Determine badge variant based on usage
  const getLimitBadgeVariant = (percentage: number) => {
    if (percentage >= 90) return 'destructive';
    if (percentage >= 75) return 'default';
    return 'secondary';
  };

  const handleClearAll = () => {
    setSelectedFiles([]);
    showToast('info', 'All files cleared');
  };

  return (
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          Upload Files
          {selectedFiles.length > 0 && (
            <>
              <Badge variant="secondary" className="ml-2">
                {selectedFiles.length} files • {formatFileSize(totalSize)}
              </Badge>
              <Badge variant={getLimitBadgeVariant(uploadLimitPercentage)}>
                {uploadLimitPercentage}% of 1 GB
              </Badge>
            </>
          )}
        </CardTitle>
        <CardDescription>
          Drag and drop files or click to browse. Maximum 1 GB total per upload session.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div
          {...getRootProps()}
          className={cn(
            'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer',
            'transition-all duration-300 hover:border-primary hover:bg-secondary/50',
            isDragActive && 'border-primary bg-secondary',
            isProcessing && 'opacity-60 cursor-not-allowed pointer-events-none'
          )}
        >
          <input {...getInputProps()} />

          <Upload className={cn(
            "w-12 h-12 text-muted-foreground mb-4 mx-auto transition-all duration-300",
            isDragActive && "text-primary scale-110"
          )} />

          <p className="text-lg font-semibold text-foreground mb-2">
            {isProcessing ? 'Processing files...' : isDragActive ? 'Drop files here...' : 'Drop files here or click to browse'}
          </p>

          <p className="text-sm text-muted-foreground">
            {isProcessing ? 'Upload disabled during processing' : 'Supported: Images, PDFs, Documents, Audio, ZIP archives'}
          </p>
        </div>

        {selectedFiles.length > 0 && (
          <>
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center" onClick={(e) => e.stopPropagation()}>
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  className="pl-9"
                />
              </div>

              <div className="flex gap-3 items-center ml-auto">
                <div className="flex items-center gap-2">
                  <Label htmlFor="groupByType" className="whitespace-nowrap text-sm">
                    Group by type
                  </Label>
                  <Switch
                    id="groupByType"
                    checked={groupByType}
                    onCheckedChange={(checked) => setGroupByType(!!checked)}
                    aria-label="Group by file type"
                  />
                </div>

                <Button
                  variant="destructive"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleClearAll();
                  }}
                  className="shadow-md hover:shadow-lg"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear All
                </Button>
              </div>
            </div>

            <Separator />

            {groupByType ? (
              <Accordion type="multiple" className="w-full">
                {fileGroups.map((group) => (
                  <AccordionItem key={group.type} value={group.type}>
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center gap-3 flex-1">
                        {group.icon}
                        <span className="font-medium">{group.type}</span>
                        <Badge variant="secondary">
                          {group.files.length} files
                        </Badge>
                        <span className="text-sm text-muted-foreground ml-auto mr-4">
                          {formatFileSize(group.totalSize)}
                        </span>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <ScrollArea className="h-[200px]">
                        {group.files.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center gap-3 p-2 hover:bg-brand-gray-50 rounded"
                          >
                            <span className="text-sm">{getFileTypeIcon(file.name)}</span>
                            <span className="flex-1 text-sm truncate">{file.name}</span>
                            <span className="text-xs text-muted-foreground">
                              {formatFileSize(file.size)}
                            </span>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={(e) => {
                                e.stopPropagation();
                                const newFiles = selectedFiles.filter(f => f !== file);
                                setSelectedFiles(newFiles);
                              }}
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        ))}
                      </ScrollArea>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            ) : (
              <div className="border rounded-lg">
                <ScrollArea className="h-[400px]">
                  {filteredFiles.map((file, index) => {
                      const originalIndex = selectedFiles.indexOf(file);
                      return (
                        <div
                          key={index}
                          className="flex items-center gap-3 px-4 py-2 hover:bg-brand-gray-50"
                        >
                          <span className="text-lg">{getFileTypeIcon(file.name)}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-black truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-brand-gray-500">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              const newFiles = selectedFiles.filter((_, i) => i !== originalIndex);
                              setSelectedFiles(newFiles);
                            }}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      );
                    })}
                </ScrollArea>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
