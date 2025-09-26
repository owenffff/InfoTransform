'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { useStore } from '@/lib/store';
import { showToast } from './Toast';
import { formatFileSize, getFileTypeIcon } from '@/lib/utils';
import { cn } from '@/lib/utils';

const ACCEPTED_EXTENSIONS = [
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
  '.pdf', '.docx', '.pptx', '.xlsx',
  '.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm',
  '.zip', '.md', '.txt'
];

export function FileUpload() {
  const { selectedFiles, setSelectedFiles } = useStore();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) {
      showToast('error', 'No valid files selected');
      return;
    }

    setSelectedFiles(acceptedFiles);
    showToast('success', `${acceptedFiles.length} file(s) selected`);
  }, [setSelectedFiles]);

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

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <span className="text-brand-orange-500">1.</span>
        Upload Files
      </h2>
      
      <div
        {...getRootProps()}
        className={cn(
          'relative border-2 border-dashed border-gray-300 rounded-xl p-16 text-center cursor-pointer',
          'transition-all duration-300 hover:border-brand-orange-500',
          'hover:bg-gradient-to-br hover:from-brand-orange-50 hover:to-brand-orange-100',
          'hover:shadow-inner group',
          isDragActive && 'drop-zone-active'
        )}
      >
        <input {...getInputProps()} />
        
        <Upload className="w-20 h-20 text-gray-400 mb-6 mx-auto group-hover:text-brand-orange-500 transition-all duration-300 group-hover:scale-110" />
        
        <p className="text-2xl font-semibold text-gray-800 mb-3 group-hover:text-brand-orange-700">
          {isDragActive ? 'Drop files here...' : 'Drop files here or click to browse'}
        </p>
        
        <p className="text-base text-gray-600 group-hover:text-gray-700">
          Supported: Images, PDFs, Documents, Audio, ZIP archives
        </p>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Selected Files ({selectedFiles.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200"
              >
                <span className="text-2xl">{getFileTypeIcon(file.name)}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => {
              setSelectedFiles([]);
              showToast('info', 'Files cleared');
            }}
            className="mt-3 text-sm text-gray-600 hover:text-brand-orange-600"
          >
            Clear all files
          </button>
        </div>
      )}
    </div>
  );
}