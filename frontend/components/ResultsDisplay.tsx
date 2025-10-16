'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import { Download, Table, Grid3X3, Search, RotateCcw, ChevronUp, ChevronDown, Loader2, ArrowDown, UserCheck } from 'lucide-react';
import { useStore } from '@/lib/store';
import { downloadResults, createReviewSession } from '@/lib/api';
import { showToast } from './Toast';
import { cn } from '@/lib/utils';
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from '@/components/ui/select';
import { useRouter } from 'next/navigation';

export function ResultsDisplay() {
  const {
    streamingResults,
    modelFields,
    editedData,
    updateEditedData,
    sortState,
    setSortState,
    viewMode,
    setViewMode,
    setEditedData,
    isProcessing
  } = useStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [downloadFormat, setDownloadFormat] = useState<'excel' | 'csv'>('excel');
  const [newResultIds, setNewResultIds] = useState<Set<string>>(new Set());
  const prevResultsCount = useRef(0);
  const tableRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  // Success/Failed panel state
  const [successOpen, setSuccessOpen] = useState(true);
  const [failedOpen, setFailedOpen] = useState(true);
  const prevSuccessCount = useRef(0);
  const prevFailedCount = useRef(0);
  
  // Track new results for animation and auto-scroll
  useEffect(() => {
    if (streamingResults.length > prevResultsCount.current) {
      const newIds = new Set<string>();
      for (let i = prevResultsCount.current; i < streamingResults.length; i++) {
        newIds.add(streamingResults[i].filename);
      }
      setNewResultIds(newIds);
      
      // Auto-scroll to show new results
      if (autoScroll && tableRef.current) {
        setTimeout(() => {
          tableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 100);
      }
      
      // Remove animation class after animation completes
      setTimeout(() => {
        setNewResultIds(new Set());
      }, 2000);
    }
    prevResultsCount.current = streamingResults.length;
  }, [streamingResults, autoScroll]);

  // Get data with edits applied
  const getDataWithEdits = () => {
    return streamingResults.map(result => {
      if (result.status !== 'success' || !result.structured_data) return result;
      
      const editedFields = editedData[result.filename] || {};
      return {
        ...result,
        structured_data: {
          ...result.structured_data,
          ...editedFields
        }
      };
    });
  };

  // Filter and sort results
  const filteredResults = useMemo(() => {
    let results = getDataWithEdits();
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      results = results.filter(result => {
        if (result.filename.toLowerCase().includes(query)) return true;
        if (result.status === 'success' && result.structured_data) {
          return Object.values(result.structured_data).some(value => 
            String(value).toLowerCase().includes(query)
          );
        }
        if (result.status === 'error' && result.error) {
          return String(result.error).toLowerCase().includes(query);
        }
        return false;
      });
    }

    // Sort if needed
    if (sortState.column && sortState.direction) {
      results = [...results].sort((a, b) => {
        let aValue: any = '';
        let bValue: any = '';

        if (sortState.column === 'filename') {
          aValue = a.filename;
          bValue = b.filename;
        } else if (a.status === 'success' && b.status === 'success' && a.structured_data && b.structured_data && sortState.column) {
          aValue = a.structured_data[sortState.column] || '';
          bValue = b.structured_data[sortState.column] || '';
        }

        if (aValue < bValue) return sortState.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortState.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return results;
  }, [streamingResults, editedData, searchQuery, sortState]);

  const successfulResults = filteredResults.filter(r => r.status === 'success');
  const failedResults = filteredResults.filter(r => r.status === 'error');

  // Heuristic classification for clearer badges/tips
  const classifyError = (err?: string) => {
    const e = (err || '').toLowerCase();
    if (/(password|protected|encrypt)/.test(e)) return { label: 'Password required', tip: 'Unlock the PDF and re-upload.' };
    if (/(corrupt|damaged|malformed)/.test(e)) return { label: 'Corrupted file', tip: 'Re-download or repair the file and try again.' };
    if (/(unsupported|format)/.test(e)) return { label: 'Unsupported format', tip: 'Upload a supported PDF or text-based document.' };
    if (/(timeout|too large|token|context)/.test(e)) return { label: 'Too large / timed out', tip: 'Try splitting the document or enabling summarization.' };
    return { label: '', tip: '' };
  };

  // Auto-open the failures panel when new failures arrive
  useEffect(() => {
    if (failedResults.length > prevFailedCount.current) {
      setFailedOpen(true);
    }
    prevFailedCount.current = failedResults.length;
  }, [failedResults.length]);

  // Auto-open successes when new items arrive
  useEffect(() => {
    if (successfulResults.length > prevSuccessCount.current) {
      setSuccessOpen(true);
    }
    prevSuccessCount.current = successfulResults.length;
  }, [successfulResults.length]);

  // Collapse failed panel by default after processing completes
  useEffect(() => {
    if (!isProcessing) {
      setFailedOpen(false);
    }
  }, [isProcessing]);

  const handleSort = (column: string) => {
    if (sortState.column === column) {
      // Toggle direction
      if (sortState.direction === 'asc') {
        setSortState({ column, direction: 'desc' });
      } else if (sortState.direction === 'desc') {
        setSortState({ column: null, direction: null });
      }
    } else {
      setSortState({ column, direction: 'asc' });
    }
  };

  const handleDownload = async () => {
    try {
      const dataToExport = getDataWithEdits()
        .filter(r => r.status === 'success' && r.structured_data)
        .map(r => ({
          filename: r.filename,
          ...r.structured_data
        }));

      await downloadResults(dataToExport, downloadFormat, ['filename', ...modelFields]);
      showToast('success', `Results exported as ${downloadFormat.toUpperCase()}`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Failed to download results';
      showToast('error', msg);
    }
  };

  const clearEdits = () => {
    setEditedData({});
    showToast('info', 'All edits cleared');
  };

  const router = useRouter();
  
  const handleOpenReviewWorkspace = async () => {
    try {
      const successfulResults = streamingResults.filter(
        r => r.status === 'success' && r.structured_data
      );
      
      if (successfulResults.length === 0) {
        showToast('error', 'No successful results to review');
        return;
      }

      const fileGroups = new Map<string, typeof successfulResults>();
      
      for (const result of successfulResults) {
        const key = result.source_file || result.filename;
        if (!fileGroups.has(key)) {
          fileGroups.set(key, []);
        }
        fileGroups.get(key)!.push(result);
      }

      const files = Array.from(fileGroups.entries()).map(([filename, results]) => {
        const firstResult = results[0];
        const allData = results.map(r => r.structured_data || {});

        return {
          filename: filename,
          extracted_data: allData.length === 1 ? allData[0] : allData,
          processing_metadata: {
            model_used: firstResult.model_fields?.join(', ') || '',
            processing_time: firstResult.processing_time,
            markdown_content: firstResult.markdown_content,
            was_summarized: firstResult.was_summarized,
            original_file_path: firstResult.file_path  // Add original file path
          },
          source_file: firstResult.source_file,
          record_count: results.length
        };
      });

      const sessionId = await createReviewSession(files);
      router.push(`/review-workspace/${sessionId}`);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Failed to open review workspace';
      showToast('error', msg);
    }
  };

  if (streamingResults.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-3">
              Transformation Results
              {isProcessing && (
                <span className="flex items-center gap-2 text-sm font-normal text-brand-orange-600 bg-brand-orange-50 px-3 py-1 rounded-full animate-pulse">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Live Streaming
                </span>
              )}
            </h2>
            <p className="text-sm text-black mt-1">
              {isProcessing 
                ? (
                  <span className="flex items-center gap-2">
                    <span className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    {streamingResults.filter(r => r.is_primary_result !== false).length} file(s) processed so far...
                  </span>
                )
                : `${streamingResults.filter(r => r.is_primary_result !== false).length} file(s) processed`}
            </p>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {/* View Toggle */}
            <div className="inline-flex rounded-md shadow-sm" role="group">
              <button
                onClick={() => setViewMode('table')}
                className={cn(
                  'inline-flex items-center px-4 py-2 text-sm font-medium border rounded-l-md',
                  viewMode === 'table'
                    ? 'text-brand-orange-700 bg-brand-orange-50 border-brand-orange-300'
                    : 'text-black bg-white border-brand-gray-200 hover:bg-brand-gray-100'
                )}
              >
                <Table className="w-4 h-4 mr-2" />
                Table
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={cn(
                  'inline-flex items-center px-4 py-2 text-sm font-medium border rounded-r-md',
                  viewMode === 'cards'
                    ? 'text-brand-orange-700 bg-brand-orange-50 border-brand-orange-300'
                    : 'text-black bg-white border-brand-gray-200 hover:bg-brand-gray-100'
                )}
              >
                <Grid3X3 className="w-4 h-4 mr-2" />
                Cards
              </button>
            </div>
            
            {/* Actions */}
            <div className="flex items-center gap-2">
              {isProcessing && (
                <button
                  onClick={() => setAutoScroll(!autoScroll)}
                  className={cn(
                    "inline-flex items-center px-3 py-2 text-sm font-medium rounded-md shadow-sm transition-all",
                    autoScroll 
                      ? "bg-brand-orange-500 text-white hover:bg-brand-orange-600"
                      : "bg-white text-black border border-brand-gray-300 hover:bg-brand-gray-50"
                  )}
                  title={autoScroll ? "Auto-scroll enabled" : "Auto-scroll disabled"}
                >
                  <ArrowDown className={cn("w-4 h-4", autoScroll && "animate-bounce")} />
                  <span className="ml-2 hidden sm:inline">Auto-scroll</span>
                </button>
              )}
              {successfulResults.length > 0 && !isProcessing && (
                <button
                  onClick={handleOpenReviewWorkspace}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-brand-orange-500 border border-transparent rounded-md shadow-sm hover:bg-brand-orange-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-orange-500"
                >
                  <UserCheck className="w-4 h-4 mr-2" />
                  Review Workspace
                </button>
              )}
              <Select value={downloadFormat} onValueChange={(v) => setDownloadFormat(v as 'excel' | 'csv')}>
                <SelectTrigger className="w-[180px] text-sm">
                  <SelectValue placeholder="Format" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="excel">Excel (.xlsx)</SelectItem>
                  <SelectItem value="csv">CSV (.csv)</SelectItem>
                </SelectContent>
              </Select>
              <button
                onClick={handleDownload}
                disabled={successfulResults.length === 0}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-black bg-white border border-brand-gray-300 rounded-md shadow-sm hover:bg-brand-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-brand-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Summary */}
      {streamingResults.length > 0 && (
        <div className="px-6 py-4 bg-brand-gray-50 border-b border-brand-gray-200">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg border border-brand-gray-200 px-4 py-3">
              <p className="text-sm font-medium text-brand-gray-500">Total Files</p>
              <p className="text-2xl font-semibold text-black">
                {(() => {
                  const primaryResults = streamingResults.filter(r => r.is_primary_result !== false);
                  console.log('Total files calculation:', {
                    totalResults: streamingResults.length,
                    primaryResults: primaryResults.length,
                    results: streamingResults.map(r => ({
                      filename: r.filename,
                      is_primary_result: r.is_primary_result,
                      status: r.status
                    }))
                  });
                  return primaryResults.length;
                })()}
              </p>
            </div>
            <div className="bg-white rounded-lg border border-green-200 px-4 py-3">
              <p className="text-sm font-medium text-green-600">Successful</p>
              <p className="text-2xl font-semibold text-green-600">
                {streamingResults.filter(r => r.status === 'success' && r.is_primary_result !== false).length}
              </p>
            </div>
            <div className="bg-white rounded-lg border border-red-200 px-4 py-3">
              <p className="text-sm font-medium text-red-600">Failed</p>
              <p className="text-2xl font-semibold text-red-600">
                {streamingResults.filter(r => r.status === 'error' && r.is_primary_result !== false).length}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Success header container */}
      {successfulResults.length > 0 && (
        <div className="px-6 py-4 border-b border-green-200 bg-green-50/50">
          <button
            onClick={() => setSuccessOpen(!successOpen)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-green-700">
                Successful files ({successfulResults.length})
              </span>
            </div>
            {successOpen ? (
              <ChevronUp className="w-4 h-4 text-green-700" />
            ) : (
              <ChevronDown className="w-4 h-4 text-green-700" />
            )}
          </button>
        </div>
      )}
      
      {successOpen && (
      <div className="p-6">
        {/* Search/Filter Bar */}
        <div className="mb-4 flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search results..."
              className="block w-full pl-10 pr-3 py-2 rounded-md border-brand-gray-300 shadow-sm focus:border-brand-orange-500 focus:ring-brand-orange-500 sm:text-sm"
            />
          </div>
          {Object.keys(editedData).length > 0 && (
            <button
              onClick={clearEdits}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-black bg-white border border-brand-gray-300 rounded-md shadow-sm hover:bg-brand-gray-50"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Clear Edits ({Object.keys(editedData).length})
            </button>
          )}
        </div>
        
        {/* Table View */}
        {viewMode === 'table' && successfulResults.length > 0 && (
          <div ref={tableRef}>
            <TableView
              results={successfulResults}
              fields={modelFields}
              onSort={handleSort}
              sortState={sortState}
              onEdit={updateEditedData}
              editedData={editedData}
              newResultIds={newResultIds}
            />
          </div>
        )}
        
        {/* Card View */}
        {viewMode === 'cards' && (
          <CardView
            results={successfulResults}
            fields={modelFields}
            onEdit={updateEditedData}
            editedData={editedData}
            newResultIds={newResultIds}
          />
        )}
        
        {/* No Results */}
        {filteredResults.length === 0 && searchQuery && (
          <div className="text-center py-8">
            <p className="text-brand-gray-500">No results found for "{searchQuery}"</p>
          </div>
        )}
      </div>
      )}
      
      {/* Failed container comes after successes */}
      {failedResults.length > 0 && (
        <div className="px-6 py-4 border-b border-red-200 bg-red-50/50">
          <button
            onClick={() => setFailedOpen(!failedOpen)}
            className="w-full flex items-center justify-between text-left"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-red-700">Failed files ({failedResults.length})</span>
            </div>
            {failedOpen ? <ChevronUp className="w-4 h-4 text-red-700" /> : <ChevronDown className="w-4 h-4 text-red-700" />}
          </button>
          {failedOpen && (
            <ul className="mt-3 space-y-2">
              {failedResults.map((r: any) => {
                const info = classifyError(r.error);
                return (
                  <li key={r.filename} className="p-3 rounded-md border border-red-200 bg-white">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                      <div>
                        <div className="text-sm font-medium text-black">{r.filename}</div>
                        <div className="text-sm text-red-600">{r.error || 'Processing failed'}</div>
                      </div>
                      {info.label && (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700 border border-red-200">
                          {info.label}
                        </span>
                      )}
                    </div>
                    {info.tip && (
                      <div className="mt-2 text-xs text-brand-gray-500">{info.tip}</div>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}

    </div>
  );
}

function TableView({ results, fields, onSort, sortState, onEdit, editedData, newResultIds }: any) {
  const handleCellEdit = (filename: string, field: string, value: string) => {
    onEdit(filename, field, value);
  };

  // Ensure fields is always an array
  const fieldArray = Array.isArray(fields) ? fields : [];

  return (
    <div className="overflow-x-auto rounded-lg border border-brand-gray-200 shadow-sm">
      <table className="min-w-full">
        <thead className="bg-brand-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-brand-gray-500 uppercase tracking-wider">#</th>
            <th
              onClick={() => onSort('filename')}
              className="px-6 py-3 text-left text-xs font-medium text-brand-gray-500 uppercase tracking-wider cursor-pointer hover:bg-brand-gray-100"
            >
              <div className="flex items-center gap-1">
                Filename
                <SortIcon column="filename" sortState={sortState} />
              </div>
            </th>
            {fieldArray.map((field: string) => (
              <th
                key={field}
                onClick={() => onSort(field)}
                className="px-6 py-3 text-left text-xs font-medium text-brand-gray-500 uppercase tracking-wider cursor-pointer hover:bg-brand-gray-100"
              >
                <div className="flex items-center gap-1">
                  {field}
                  <SortIcon column={field} sortState={sortState} />
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-brand-gray-200">
          {results.map((result: any, idx: number) => {
            const hasEdits = editedData[result.filename];
            const isNew = newResultIds?.has(result.filename);
            return (
              <tr 
                key={result.filename} 
                className={cn(
                  'transition-all duration-500',
                  hasEdits ? 'bg-brand-orange-50/30' : '',
                  isNew ? 'animate-fadeIn bg-gradient-to-r from-brand-orange-50 to-transparent' : ''
                )}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-brand-gray-500">
                  {idx + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-black">
                  {result.filename}
                </td>
                {fieldArray.map((field: string) => {
                  const value = result.structured_data?.[field];
                  console.log(`Field ${field} value:`, value, 'from:', result.structured_data);
                  return (
                    <td
                      key={field}
                      className="px-6 py-4 whitespace-nowrap text-sm text-black editable-cell"
                    >
                      <input
                        type="text"
                        value={value !== null && value !== undefined ? String(value) : ''}
                        onChange={(e) => handleCellEdit(result.filename, field, e.target.value)}
                        className="w-full bg-transparent border-0 p-0 focus:outline-none focus:ring-0"
                      />
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function CardView({ results, fields, onEdit, editedData, newResultIds }: any) {
  // Ensure fields is always an array
  const fieldArray = Array.isArray(fields) ? fields : [];
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {results.map((result: any) => {
        const hasEdits = editedData[result.filename];
        const isNew = newResultIds?.has(result.filename);
        return (
          <div
            key={result.filename}
            className={cn(
              'p-4 rounded-lg border transition-all duration-500',
              result.status === 'error'
                ? 'bg-red-50 border-red-200'
                : hasEdits
                ? 'bg-brand-orange-50/50 border-brand-orange-200'
                : 'bg-white border-brand-gray-200',
              isNew ? 'animate-fadeIn ring-2 ring-brand-orange-400 shadow-lg shadow-brand-orange-100' : ''
            )}
          >
            <h3 className="font-medium text-black mb-3 truncate" title={result.filename}>
              {result.filename}
            </h3>
            
            {result.status === 'error' ? (
              <p className="text-sm text-red-600">{result.error || 'Processing failed'}</p>
            ) : (
              <div className="space-y-2">
                {fieldArray.map((field: string) => (
                  <div key={field}>
                    <label className="text-xs font-medium text-brand-gray-500">{field}</label>
                    <input
                      type="text"
                      value={result.structured_data?.[field] || ''}
                      onChange={(e) => onEdit(result.filename, field, e.target.value)}
                      className="mt-1 block w-full text-sm bg-white border border-brand-gray-200 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-orange-500"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function SortIcon({ column, sortState }: { column: string; sortState: any }) {
  if (sortState.column !== column) {
    return <div className="w-4 h-4" />;
  }
  
  if (sortState.direction === 'asc') {
    return <ChevronUp className="w-4 h-4" />;
  }
  
  if (sortState.direction === 'desc') {
    return <ChevronDown className="w-4 h-4" />;
  }
  
  return <div className="w-4 h-4" />;
}
