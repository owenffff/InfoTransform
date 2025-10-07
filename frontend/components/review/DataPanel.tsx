'use client';

import { FileReviewStatus } from '@/types';
import { useReviewStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Save, X, Check } from 'lucide-react';

interface DataPanelProps {
  file: FileReviewStatus;
}

export function DataPanel({ file }: DataPanelProps) {
  const { 
    hasUnsavedChanges, 
    saveChanges, 
    discardChanges,
    approveFile,
    currentSession 
  } = useReviewStore();

  const handleApprove = async () => {
    if (hasUnsavedChanges) {
      await saveChanges();
    }
    await approveFile();
  };

  const approvedCount = currentSession?.files.filter(f => f.status === 'approved').length || 0;
  const totalFiles = currentSession?.files.length || 0;

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="border-b p-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Extracted Data</h2>
          <div className="flex items-center gap-2">
            {hasUnsavedChanges && (
              <>
                <Button variant="outline" size="sm" onClick={discardChanges}>
                  <X className="w-4 h-4 mr-1" />
                  Discard
                </Button>
                <Button size="sm" onClick={saveChanges}>
                  <Save className="w-4 h-4 mr-1" />
                  Save
                </Button>
              </>
            )}
            <Button 
              size="sm" 
              onClick={handleApprove}
              disabled={file.status === 'approved'}
              className="bg-green-600 hover:bg-green-700"
            >
              <Check className="w-4 h-4 mr-1" />
              Approve
            </Button>
          </div>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <TableView file={file} />
      </ScrollArea>

      {file.status === 'approved' && file.approval_metadata && (
        <div className="border-t p-3 bg-green-50">
          <div className="flex items-center gap-2 text-sm text-green-800">
            <Check className="w-4 h-4" />
            <span>
              Approved by {file.approval_metadata.approved_by} on{' '}
              {new Date(file.approval_metadata.approved_at).toLocaleString()}
            </span>
          </div>
          {file.approval_metadata.comments && (
            <p className="text-sm text-green-700 mt-1">{file.approval_metadata.comments}</p>
          )}
        </div>
      )}

      <div className="border-t p-3 bg-gray-50 text-xs text-gray-600">
        Progress: {approvedCount} of {totalFiles} approved
      </div>
    </div>
  );
}

function TableView({ file }: { file: FileReviewStatus }) {
  const data = file.extracted_data;
  const isArray = Array.isArray(data);
  
  if (isArray && data.length > 0) {
    const allKeys = new Set<string>();
    data.forEach(record => {
      Object.keys(record).forEach(key => allKeys.add(key));
    });
    const columns = Array.from(allKeys);
    
    return (
      <div className="p-6 overflow-auto">
        <div className="text-sm text-gray-600 mb-3">
          {data.length} record{data.length !== 1 ? 's' : ''} extracted
        </div>
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-2 px-3 font-medium text-sm text-gray-700">#</th>
              {columns.map(col => (
                <th key={col} className="text-left py-2 px-3 font-medium text-sm text-gray-700">
                  {formatFieldName(col)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((record, idx) => (
              <tr key={idx} className="border-b hover:bg-gray-50">
                <td className="py-2 px-3 text-sm text-gray-500">{idx + 1}</td>
                {columns.map(col => (
                  <td key={col} className="py-2 px-3 text-sm">
                    {formatValue(record[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  
  const entries = Object.entries(data);
  
  return (
    <div className="p-6">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b bg-gray-50">
            <th className="text-left py-2 px-3 font-medium text-sm text-gray-700">Field</th>
            <th className="text-left py-2 px-3 font-medium text-sm text-gray-700">Value</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([fieldName, value]) => (
            <tr key={fieldName} className="border-b hover:bg-gray-50">
              <td className="py-2 px-3 text-sm font-medium text-gray-700">
                {formatFieldName(fieldName)}
              </td>
              <td className="py-2 px-3 text-sm">
                {formatValue(value)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatFieldName(fieldName: string): string {
  return fieldName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatValue(value: any): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}
