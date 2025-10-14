'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ReviewSession } from '@/types';
import { useReviewStore } from '@/lib/store';
import { FileListSidebar } from './FileListSidebar';
import { DocumentViewer } from './DocumentViewer';
import { DataPanel } from './DataPanel';
import { ArrowLeft, Download, FileSpreadsheet, FileText, Loader2 } from 'lucide-react';
import { downloadResults } from '@/lib/api';
import { showToast } from '../Toast';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface ReviewWorkspaceProps {
  session: ReviewSession;
}

export function ReviewWorkspace({ session }: ReviewWorkspaceProps) {
  const router = useRouter();
  const { currentSession, currentFileIndex, setCurrentSession, isSidebarCollapsed, hasUnsavedChanges, pendingEdits } = useReviewStore();
  const [downloadFormat, setDownloadFormat] = useState<'excel' | 'csv'>('excel');
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const [previewData, setPreviewData] = useState<{ data: any[], columns: string[] } | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    if (session) {
      setCurrentSession(session);
    }
  }, [session, setCurrentSession]);

  const handleBack = () => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm('You have unsaved changes. Do you want to leave without saving?');
      if (!confirmed) return;
    }
    router.push('/');
  };

  const prepareExportData = () => {
    if (!currentSession) return null;

    const dataToExport: any[] = [];
    const allColumns = new Set<string>();

    currentSession.files.forEach((file, fileIdx) => {
      const data = file.extracted_data;
      const isArray = Array.isArray(data);
      const isCurrentFile = fileIdx === currentFileIndex;

      if (isArray) {
        data.forEach((record, idx) => {
          const editedRecord = { ...record };
          
          if (file.edits) {
            file.edits.forEach(edit => {
              if (edit.record_index === idx) {
                editedRecord[edit.field_name] = edit.edited_value;
              }
            });
          }

          if (isCurrentFile && pendingEdits) {
            Object.entries(pendingEdits).forEach(([key, edit]) => {
              if (edit.record_index === idx) {
                editedRecord[edit.field_name] = edit.edited_value;
              }
            });
          }

          Object.keys(editedRecord).forEach(key => allColumns.add(key));
          dataToExport.push({
            filename: file.filename,
            ...editedRecord
          });
        });
      } else {
        const editedRecord = { ...data };
        
        if (file.edits) {
          file.edits.forEach(edit => {
            if (edit.record_index === undefined) {
              editedRecord[edit.field_name] = edit.edited_value;
            }
          });
        }

        if (isCurrentFile && pendingEdits) {
          Object.entries(pendingEdits).forEach(([key, edit]) => {
            if (edit.record_index === undefined) {
              editedRecord[edit.field_name] = edit.edited_value;
            }
          });
        }

        Object.keys(editedRecord).forEach(key => allColumns.add(key));
        dataToExport.push({
          filename: file.filename,
          ...editedRecord
        });
      }
    });

    const columns = ['filename', ...Array.from(allColumns)];
    return { data: dataToExport, columns };
  };

  const handleOpenExportDialog = () => {
    const exportData = prepareExportData();
    if (exportData) {
      setPreviewData(exportData);
      setIsExportDialogOpen(true);
    }
  };

  const handleExportFromDialog = async () => {
    if (!previewData) return;

    try {
      setIsExporting(true);
      await downloadResults(previewData.data, downloadFormat, previewData.columns);
      showToast('success', `${previewData.data.length} record${previewData.data.length !== 1 ? 's' : ''} exported as ${downloadFormat.toUpperCase()}`);
      setIsExportDialogOpen(false);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Failed to export results';
      showToast('error', msg);
    } finally {
      setIsExporting(false);
    }
  };

  if (!currentSession) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-orange-500 mx-auto mb-4"></div>
          <p className="text-black">Loading review session...</p>
        </div>
      </div>
    );
  }

  const currentFile = currentSession.files[currentFileIndex];

  if (!currentFile) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-black">No files to review</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-brand-gray-100">
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleBack}
              className="inline-flex items-center px-3 py-2 text-sm font-medium text-black bg-white border border-brand-gray-300 rounded-md shadow-sm hover:bg-brand-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-orange-500"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </button>
            <div>
              <h1 className="text-2xl font-bold text-black">Review Workspace</h1>
              <p className="text-sm text-black mt-1">
                {currentFile.filename} ({currentFileIndex + 1} of {currentSession.files.length})
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-sm">
              <span className="font-medium text-green-600">
                {currentSession.batch_metadata?.approved_count || 0}
              </span>
              <span className="text-black"> approved</span>
            </div>
            <button
              onClick={handleOpenExportDialog}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-brand-orange-500 border border-transparent rounded-md shadow-sm hover:bg-brand-orange-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-orange-500"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Results
            </button>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <FileListSidebar files={currentSession.files} />
        
        <div className={cn(
          'flex-1 flex transition-all duration-300',
          isSidebarCollapsed ? 'ml-0' : ''
        )}>
          <div className="flex-1 overflow-hidden">
            <DocumentViewer file={currentFile} />
          </div>
          
          <div className="w-1/2 border-l overflow-hidden">
            <DataPanel file={currentFile} />
          </div>
        </div>
      </div>

      <Dialog open={isExportDialogOpen} onOpenChange={setIsExportDialogOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] flex flex-col">
          <DialogHeader className="px-6 pt-6 pb-4">
            <DialogTitle className="text-xl font-semibold">Export Results</DialogTitle>
            <DialogDescription className="text-sm text-black">
              Review your extracted data below, select your preferred format, and download when ready.
            </DialogDescription>
          </DialogHeader>

          {/* Export Configuration Bar */}
          <div className="bg-brand-gray-50 border-y px-6 py-4">
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
                <div className="flex flex-col">
                  <label className="text-xs font-medium text-black uppercase tracking-wide mb-1">
                    Export Format
                  </label>
                  <Select 
                    value={downloadFormat} 
                    onValueChange={(v) => setDownloadFormat(v as 'excel' | 'csv')}
                  >
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="excel">
                        <div className="flex items-center gap-2">
                          <FileSpreadsheet className="w-4 h-4" />
                          <span>Excel (.xlsx)</span>
                        </div>
                      </SelectItem>
                      <SelectItem value="csv">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          <span>CSV (.csv)</span>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="hidden sm:block h-10 w-px bg-brand-gray-300" />
                
                <div className="flex flex-col justify-center">
                  <span className="text-2xl font-bold text-black">
                    {previewData?.data.length || 0}
                  </span>
                  <span className="text-xs text-black">
                    record{previewData?.data.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
              
              <button
                onClick={handleExportFromDialog}
                disabled={isExporting || !previewData || previewData.data.length === 0}
                className={cn(
                  "inline-flex items-center justify-center px-6 py-3 text-base font-medium rounded-md shadow-sm",
                  "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-orange-500",
                  "transition-colors duration-150",
                  isExporting || !previewData || previewData.data.length === 0
                    ? "bg-brand-orange-300 text-white cursor-not-allowed"
                    : "bg-brand-orange-500 text-white hover:bg-brand-orange-600"
                )}
              >
                {isExporting ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5 mr-2" />
                    Download as {downloadFormat === 'excel' ? 'Excel' : 'CSV'}
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Data Preview Section */}
          <div className="px-6 pb-6 flex-1 overflow-hidden flex flex-col">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-medium text-black">Data Preview</h3>
              {previewData && previewData.columns.length > 6 && (
                <span className="text-xs text-brand-gray-500">
                  Scroll horizontally to see all {previewData.columns.length} columns
                </span>
              )}
            </div>
            
            <div className="border rounded-md overflow-hidden flex-1">
              <div className="overflow-auto max-h-[400px]">
                {previewData && previewData.data.length > 0 ? (
                  <table className="w-full text-sm">
                    <thead className="bg-brand-gray-50 sticky top-0">
                      <tr>
                        {previewData.columns.map((column) => (
                          <th
                            key={column}
                            className="px-4 py-3 text-left text-xs font-medium text-black uppercase tracking-wider border-b whitespace-nowrap"
                          >
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-brand-gray-200">
                      {previewData.data.map((row, idx) => (
                        <tr key={idx} className="hover:bg-brand-gray-50">
                          {previewData.columns.map((column) => (
                            <td
                              key={`${idx}-${column}`}
                              className="px-4 py-3 text-sm text-black border-b whitespace-nowrap"
                            >
                              {row[column] !== undefined && row[column] !== null
                                ? String(row[column])
                                : ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="flex items-center justify-center h-32 text-brand-gray-500">
                    No data to export
                  </div>
                )}
              </div>
            </div>
          </div>

          <DialogFooter className="px-6 pb-6 flex justify-start">
            <button
              onClick={() => setIsExportDialogOpen(false)}
              disabled={isExporting}
              className="text-sm font-medium text-black disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ');
}
