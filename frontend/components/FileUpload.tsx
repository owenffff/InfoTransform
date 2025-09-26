'use client';

import React, { useCallback, useMemo, useState } from 'react';
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
  ChevronDown,
  ChevronRight,
  Filter,
  Trash2,
  CheckSquare,
  Square
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
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Separator } from '@/components/ui/separator';

const ACCEPTED_EXTENSIONS = [
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
  '.pdf', '.docx', '.pptx', '.xlsx',
  '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm',
  '.zip', '.md', '.txt'
];

interface FileGroup {
  type: string;
  icon: React.ReactNode;
  files: File[];
  totalSize: number;
}

type SortOption = 'name' | 'size' | 'type' | 'date';
type ViewMode = 'summary' | 'list' | 'grid';

export function FileUpload() {
  const { selectedFiles, setSelectedFiles } = useStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('name');
  const [viewMode, setViewMode] = useState<ViewMode>('summary');
  const [selectedFileIndices, setSelectedFileIndices] = useState<Set<number>>(new Set());
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set());

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
    multiple: true
  });

  // Group files by type
  const fileGroups = useMemo(() => {
    const groups: Record<string, FileGroup> = {};
    
    selectedFiles.forEach(file => {
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
  }, [selectedFiles]);

  // Filter and sort files
  const filteredAndSortedFiles = useMemo(() => {
    let files = [...selectedFiles];
    
    // Filter by search query
    if (searchQuery) {
      files = files.filter(file => 
        file.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Sort files
    files.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'size':
          return b.size - a.size;
        case 'type':
          return a.type.localeCompare(b.type);
        case 'date':
          return (b.lastModified || 0) - (a.lastModified || 0);
        default:
          return 0;
      }
    });
    
    return files;
  }, [selectedFiles, searchQuery, sortBy]);

  const totalSize = useMemo(() => 
    selectedFiles.reduce((acc, file) => acc + file.size, 0),
    [selectedFiles]
  );

  const handleSelectAll = () => {
    if (selectedFileIndices.size === selectedFiles.length) {
      setSelectedFileIndices(new Set());
    } else {
      setSelectedFileIndices(new Set(selectedFiles.map((_, i) => i)));
    }
  };

  const handleRemoveSelected = () => {
    const indicesToRemove = Array.from(selectedFileIndices).sort((a, b) => b - a);
    const newFiles = [...selectedFiles];
    indicesToRemove.forEach(index => {
      newFiles.splice(index, 1);
    });
    setSelectedFiles(newFiles);
    setSelectedFileIndices(new Set());
    showToast('info', `${indicesToRemove.length} file(s) removed`);
  };

  const handleClearAll = () => {
    setSelectedFiles([]);
    setSelectedFileIndices(new Set());
    showToast('info', 'All files cleared');
  };

  const toggleGroup = (type: string) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(type)) {
      newExpanded.delete(type);
    } else {
      newExpanded.add(type);
    }
    setExpandedGroups(newExpanded);
  };

  return (
    <Card className="shadow-lg border-gray-200">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <span className="text-primary">1.</span>
          Upload Files
          {selectedFiles.length > 0 && (
            <Badge variant="secondary" className="ml-2">
              {selectedFiles.length} files • {formatFileSize(totalSize)}
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Drag and drop files or click to browse. Supports bulk uploads of 100+ files.
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div
          {...getRootProps()}
          className={cn(
            'relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer',
            'transition-all duration-300 hover:border-primary hover:bg-secondary/50',
            isDragActive && 'border-primary bg-secondary'
          )}
        >
          <input {...getInputProps()} />
          
          <Upload className={cn(
            "w-12 h-12 text-muted-foreground mb-4 mx-auto transition-all duration-300",
            isDragActive && "text-primary scale-110"
          )} />
          
          <p className="text-lg font-semibold text-foreground mb-2">
            {isDragActive ? 'Drop files here...' : 'Drop files here or click to browse'}
          </p>
          
          <p className="text-sm text-muted-foreground">
            Supported: Images, PDFs, Documents, Audio, ZIP archives
          </p>
        </div>

        {selectedFiles.length > 0 && (
          <>
            <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              
              <div className="flex gap-2">
                <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
                  <SelectTrigger className="w-[130px]">
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="name">Name</SelectItem>
                    <SelectItem value="size">Size</SelectItem>
                    <SelectItem value="type">Type</SelectItem>
                    <SelectItem value="date">Date</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select value={viewMode} onValueChange={(value) => setViewMode(value as ViewMode)}>
                  <SelectTrigger className="w-[130px]">
                    <SelectValue placeholder="View" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="summary">Summary</SelectItem>
                    <SelectItem value="list">List</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {selectedFiles.length > 10 && (
              <div className="flex gap-2 items-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSelectAll}
                >
                  {selectedFileIndices.size === selectedFiles.length ? (
                    <>
                      <CheckSquare className="h-4 w-4 mr-2" />
                      Deselect All
                    </>
                  ) : (
                    <>
                      <Square className="h-4 w-4 mr-2" />
                      Select All
                    </>
                  )}
                </Button>
                
                {selectedFileIndices.size > 0 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRemoveSelected}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Remove Selected ({selectedFileIndices.size})
                  </Button>
                )}
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearAll}
                  className="ml-auto"
                >
                  Clear All
                </Button>
              </div>
            )}

            <Separator />

            {viewMode === 'summary' ? (
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
                            className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded"
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
                              onClick={() => {
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
                  {filteredAndSortedFiles.map((file, index) => {
                      const originalIndex = selectedFiles.indexOf(file);
                      const isSelected = selectedFileIndices.has(originalIndex);
                      
                      return (
                        <div
                          key={index}
                          className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50"
                        >
                          <Checkbox
                            checked={isSelected}
                            onCheckedChange={() => {
                              const newSelected = new Set(selectedFileIndices);
                              if (isSelected) {
                                newSelected.delete(originalIndex);
                              } else {
                                newSelected.add(originalIndex);
                              }
                              setSelectedFileIndices(newSelected);
                            }}
                          />
                          <span className="text-lg">{getFileTypeIcon(file.name)}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => {
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