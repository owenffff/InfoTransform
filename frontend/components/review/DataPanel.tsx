'use client';

import { FileReviewStatus } from '@/types';
import { useReviewStore } from '@/lib/store';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Check, Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { showToast } from '../Toast';

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
  
  const [isApproving, setIsApproving] = useState(false);

  const handleApprove = async () => {
    try {
      setIsApproving(true);
      if (hasUnsavedChanges) {
        await saveChanges();
      }
      await approveFile();
      showToast('success', 'File approved successfully');
    } catch (error) {
      showToast('error', 'Failed to approve file');
    } finally {
      setIsApproving(false);
    }
  };
  
  const handleSave = async () => {
    try {
      await saveChanges();
      showToast('success', 'Changes saved');
    } catch (error) {
      showToast('error', 'Failed to save changes');
    }
  };
  
  const handleRevert = () => {
    discardChanges();
    showToast('info', 'Changes reverted');
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+S or Cmd+S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (hasUnsavedChanges) {
          handleSave();
        }
      }
      // Ctrl+Enter or Cmd+Enter to approve
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        handleApprove();
      }
      // Esc to revert
      if (e.key === 'Escape' && hasUnsavedChanges) {
        e.preventDefault();
        handleRevert();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [hasUnsavedChanges]);

  const approvedCount = currentSession?.files.filter(f => f.status === 'approved').length || 0;
  const totalFiles = currentSession?.files.length || 0;

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="border-b p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="font-semibold">Extracted Data</h2>
            {hasUnsavedChanges && (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 px-2 py-1 bg-orange-50 border border-orange-200 rounded-md">
                  <div className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse" />
                  <span className="text-xs font-medium text-orange-700">Unsaved changes</span>
                </div>
                <span className="text-xs text-brand-gray-500">
                  Press <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs font-mono">Esc</kbd> to revert
                </span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button 
              size="sm" 
              onClick={handleApprove}
              disabled={isApproving}
              className="bg-brand-orange-500 hover:bg-brand-orange-600"
              title={hasUnsavedChanges ? 'Will save changes before approving' : 'Approve this file'}
            >
              {isApproving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  {hasUnsavedChanges ? 'Saving...' : 'Approving...'}
                </>
              ) : (
                <>
                  <Check className="w-4 h-4 mr-1" />
                  {file.status === 'approved' ? 'Re-approve' : 'Approve'}
                </>
              )}
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

      <div className="border-t p-3 bg-brand-gray-50 text-xs text-black">
        Progress: {approvedCount} of {totalFiles} approved
      </div>
    </div>
  );
}

type ColumnType = 'short' | 'medium' | 'long';

function getColumnType(fieldName: string, sampleValues: any[]): ColumnType {
  const lowerField = fieldName.toLowerCase();
  
  if (/(id|num|count|age|year|code)$/.test(lowerField)) return 'short';
  if (/(date|time|status|type|category)/.test(lowerField)) return 'short';
  if (/(name|email|phone|city|state|country)/.test(lowerField)) return 'medium';
  if (/(address|description|summary|comment|note|content|text)/.test(lowerField)) return 'long';
  
  const maxLength = Math.max(...sampleValues.map(v => String(v || '').length));
  if (maxLength <= 15) return 'short';
  if (maxLength <= 50) return 'medium';
  return 'long';
}

function getColumnWidthClass(columnType: ColumnType): string {
  switch (columnType) {
    case 'short': return 'min-w-[100px] max-w-[150px]';
    case 'medium': return 'min-w-[150px] max-w-[250px]';
    case 'long': return 'min-w-[200px] max-w-[400px]';
  }
}

interface EditableCellProps {
  value: any;
  fieldName: string;
  recordIndex?: number;
  hasEdit: boolean;
  onEdit: (value: string) => void;
  columnType: ColumnType;
}

function EditableCell({ value, fieldName, recordIndex, hasEdit, onEdit, columnType }: EditableCellProps) {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const displayValue = formatValue(value);
  
  const handleDoubleClick = () => {
    setIsPopoverOpen(true);
  };
  
  return (
    <td className={`py-2 px-3 text-sm ${getColumnWidthClass(columnType)}`}>
      <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
        <PopoverTrigger asChild>
          <input
            type="text"
            value={displayValue}
            onChange={(e) => onEdit(e.target.value)}
            onDoubleClick={handleDoubleClick}
            className={`w-full bg-transparent border-0 p-1 focus:outline-none focus:ring-1 focus:ring-brand-orange-500 focus:bg-white rounded cursor-text ${
              hasEdit ? 'border-l-2 border-l-orange-500 pl-2' : ''
            }`}
            title="Double-click to edit in expanded view"
          />
        </PopoverTrigger>
        <PopoverContent className="w-96 max-h-96 overflow-y-auto">
          <div className="space-y-2">
            <div className="font-medium text-sm">{formatFieldName(fieldName)}</div>
            <textarea
              value={displayValue}
              onChange={(e) => onEdit(e.target.value)}
              className="w-full min-h-[200px] p-2 text-sm border rounded resize-none focus:outline-none focus:ring-2 focus:ring-brand-orange-500"
              autoFocus
            />
            <div className="flex justify-end">
              <Button size="sm" onClick={() => setIsPopoverOpen(false)}>
                Done
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>
    </td>
  );
}

interface EditableFieldRowProps {
  fieldName: string;
  value: any;
  hasEdit: boolean;
  onEdit: (value: string) => void;
}

function EditableFieldRow({ fieldName, value, hasEdit, onEdit }: EditableFieldRowProps) {
  const [isPopoverOpen, setIsPopoverOpen] = useState(false);
  const displayValue = formatValue(value);

  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="py-2 px-3 text-sm font-medium text-black align-top">
        {formatFieldName(fieldName)}
      </td>
      <td className="py-2 px-3 text-sm">
        <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
          <PopoverTrigger asChild>
            <input
              type="text"
              value={displayValue}
              onChange={(e) => onEdit(e.target.value)}
              onDoubleClick={() => setIsPopoverOpen(true)}
              className={`w-full bg-transparent border-0 p-1 focus:outline-none focus:ring-1 focus:ring-brand-orange-500 focus:bg-white rounded cursor-text ${
                hasEdit ? 'border-l-2 border-l-orange-500 pl-2' : ''
              }`}
              title="Double-click to edit in expanded view"
            />
          </PopoverTrigger>
          <PopoverContent className="w-96 max-h-96 overflow-y-auto">
            <div className="space-y-2">
              <div className="font-medium text-sm">{formatFieldName(fieldName)}</div>
              <textarea
                value={displayValue}
                onChange={(e) => onEdit(e.target.value)}
                className="w-full min-h-[200px] p-2 text-sm border rounded resize-none focus:outline-none focus:ring-2 focus:ring-brand-orange-500"
                autoFocus
              />
              <div className="flex justify-end">
                <Button size="sm" onClick={() => setIsPopoverOpen(false)}>
                  Done
                </Button>
              </div>
            </div>
          </PopoverContent>
        </Popover>
      </td>
    </tr>
  );
}

function TableView({ file }: { file: FileReviewStatus }) {
  const { updateField, pendingEdits } = useReviewStore();
  const data = file.extracted_data;
  const isArray = Array.isArray(data);

  const handleCellEdit = (fieldName: string, value: any, recordIndex?: number) => {
    updateField(fieldName, value, recordIndex);
  };

  const getFieldValue = (fieldName: string, recordIndex?: number): any => {
    const editKey = recordIndex !== undefined
      ? `${recordIndex}.${fieldName}`
      : fieldName;

    if (pendingEdits[editKey]) {
      return pendingEdits[editKey].edited_value;
    }

    if (recordIndex !== undefined && isArray) {
      return (data as Record<string, any>[])[recordIndex]?.[fieldName];
    }

    return (data as Record<string, any>)[fieldName];
  };

  const hasEdit = (fieldName: string, recordIndex?: number): boolean => {
    const editKey = recordIndex !== undefined
      ? `${recordIndex}.${fieldName}`
      : fieldName;
    return editKey in pendingEdits;
  };

  if (isArray && data.length > 0) {
    const allKeys = new Set<string>();
    data.forEach(record => {
      Object.keys(record).forEach(key => allKeys.add(key));
    });
    const columns = Array.from(allKeys);

    const columnTypes = columns.map(col => ({
      name: col,
      type: getColumnType(col, data.map(r => r[col]))
    }));

    return (
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm text-black">
            {data.length} record{data.length !== 1 ? 's' : ''} extracted
          </div>
          {data.length > 1 && (
            <div className="text-xs text-brand-gray-500 bg-brand-gray-100 px-2 py-1 rounded">
              Multiple records from one file
            </div>
          )}
        </div>
        <div className="relative">
          <div className="overflow-x-auto border rounded-lg shadow-sm">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="sticky left-0 z-10 bg-gray-50 text-left py-2 px-3 font-medium text-sm text-gray-700 border-r">#</th>
                  {columnTypes.map(({ name, type }) => (
                    <th
                      key={name}
                      className={`text-left py-2 px-3 font-medium text-sm text-black ${getColumnWidthClass(type)}`}
                    >
                      {formatFieldName(name)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((record, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="sticky left-0 z-10 bg-white py-2 px-3 text-sm text-gray-500 border-r">{idx + 1}</td>
                    {columnTypes.map(({ name, type }) => (
                      <EditableCell
                        key={name}
                        value={getFieldValue(name, idx)}
                        fieldName={name}
                        recordIndex={idx}
                        hasEdit={hasEdit(name, idx)}
                        onEdit={(val) => handleCellEdit(name, val, idx)}
                        columnType={type}
                      />
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  const entries = Object.entries(data);

  return (
    <div className="p-6">
      <div className="border rounded-lg shadow-sm overflow-hidden">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b bg-gray-50">
              <th className="text-left py-2 px-3 font-medium text-sm text-black w-[200px]">Field</th>
              <th className="text-left py-2 px-3 font-medium text-sm text-black">Value</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([fieldName, value]) => (
              <EditableFieldRow
                key={fieldName}
                fieldName={fieldName}
                value={getFieldValue(fieldName)}
                hasEdit={hasEdit(fieldName)}
                onEdit={(val) => handleCellEdit(fieldName, val)}
              />
            ))}
          </tbody>
        </table>
      </div>
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
