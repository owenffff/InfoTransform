/**
 * RecordNavigator Component
 *
 * Left sidebar for master-detail view showing list of records
 * with status indicators, selection, and quick navigation.
 */

import React, { useRef, useEffect } from 'react';
import { Check, X, Clock, AlertCircle, Pencil, Search } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface RecordStatus {
  approved: boolean;
  rejected: boolean;
  hasErrors: boolean;
  hasUnsavedChanges: boolean;
}

export interface RecordNavigatorProps {
  records: any[];
  currentRecordId: string | null;
  onRecordSelect: (recordId: string) => void;
  recordStatuses: Record<string, RecordStatus>;
  identifierField: string;      // Field to use as primary identifier
  titleField?: string;           // Optional secondary field for title
  showCheckboxes?: boolean;      // Enable multi-select
  selectedRecordIds?: Set<string>;
  onRecordToggle?: (recordId: string) => void;
  className?: string;
}

const STATUS_CONFIG = {
  approved: {
    icon: Check,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    label: 'Approved',
  },
  rejected: {
    icon: X,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    label: 'Rejected',
  },
  pending: {
    icon: Clock,
    color: 'text-gray-500',
    bgColor: 'bg-gray-50',
    label: 'Pending',
  },
  error: {
    icon: AlertCircle,
    color: 'text-amber-600',
    bgColor: 'bg-amber-50',
    label: 'Has errors',
  },
};

function getRecordStatus(status: RecordStatus): keyof typeof STATUS_CONFIG {
  if (status.rejected) return 'rejected';
  if (status.approved) return 'approved';
  if (status.hasErrors) return 'error';
  return 'pending';
}

function getRecordId(record: any, index: number): string {
  // Generate stable ID from record content or index
  return record.id || record._id || `record-${index}`;
}

interface RecordItemProps {
  record: any;
  recordId: string;
  index: number;
  isSelected: boolean;
  isChecked?: boolean;
  status: RecordStatus;
  identifierField: string;
  titleField?: string;
  onClick: () => void;
  onCheckboxChange?: (checked: boolean) => void;
  showCheckbox: boolean;
}

const RecordItem = React.memo<RecordItemProps>(({
  record,
  recordId,
  index,
  isSelected,
  isChecked,
  status,
  identifierField,
  titleField,
  onClick,
  onCheckboxChange,
  showCheckbox,
}) => {
  const statusKey = getRecordStatus(status);
  const statusConfig = STATUS_CONFIG[statusKey];
  const StatusIcon = statusConfig.icon;

  const identifier = record[identifierField] || `Record ${index + 1}`;
  const title = titleField ? record[titleField] : null;

  return (
    <div
      className={cn(
        'group relative flex items-start gap-3 p-3 cursor-pointer transition-colors',
        'border-b border-gray-200 hover:bg-gray-50',
        isSelected && 'bg-blue-50 hover:bg-blue-100 border-l-4 border-l-blue-500'
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      aria-label={`Select record ${identifier}`}
      aria-selected={isSelected}
    >
      {/* Checkbox for multi-select */}
      {showCheckbox && onCheckboxChange && (
        <div
          className="flex items-center pt-0.5"
          onClick={(e) => e.stopPropagation()}
        >
          <Checkbox
            checked={isChecked}
            onCheckedChange={onCheckboxChange}
            aria-label={`Select ${identifier} for bulk actions`}
          />
        </div>
      )}

      {/* Status icon */}
      <div className={cn('flex-shrink-0 mt-0.5', statusConfig.color)}>
        <StatusIcon className="h-4 w-4" />
      </div>

      {/* Record content */}
      <div className="flex-1 min-w-0">
        {/* Identifier (reference/ID) */}
        <div className="flex items-center gap-2">
          <span className="font-medium text-sm text-gray-900 truncate">
            {identifier}
          </span>

          {/* Unsaved changes indicator */}
          {status.hasUnsavedChanges && (
            <Badge
              variant="outline"
              className="text-xs bg-amber-50 text-amber-700 border-amber-200"
            >
              <Pencil className="w-3 h-3 mr-1" />
              Edited
            </Badge>
          )}
        </div>

        {/* Title/subtitle */}
        {title && (
          <div className="text-xs text-gray-600 truncate mt-1">
            {title}
          </div>
        )}

        {/* Status badge (only show if not pending) */}
        {statusKey !== 'pending' && (
          <Badge
            variant="outline"
            className={cn(
              'text-xs mt-2',
              statusConfig.bgColor,
              statusConfig.color,
              'border-transparent'
            )}
          >
            {statusConfig.label}
          </Badge>
        )}
      </div>
    </div>
  );
});

RecordItem.displayName = 'RecordItem';

export function RecordNavigator({
  records,
  currentRecordId,
  onRecordSelect,
  recordStatuses,
  identifierField,
  titleField,
  showCheckboxes = false,
  selectedRecordIds,
  onRecordToggle,
  className,
}: RecordNavigatorProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  const listRef = useRef<HTMLDivElement>(null);
  const selectedItemRef = useRef<HTMLDivElement>(null);

  // Filter records based on search
  const filteredRecords = React.useMemo(() => {
    if (!searchQuery.trim()) return records;

    const query = searchQuery.toLowerCase();
    return records.filter((record, index) => {
      const identifier = record[identifierField]?.toString().toLowerCase() || '';
      const title = titleField ? record[titleField]?.toString().toLowerCase() || '' : '';
      return identifier.includes(query) || title.includes(query);
    });
  }, [records, searchQuery, identifierField, titleField]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!currentRecordId) return;

      const currentIndex = filteredRecords.findIndex(
        (_, idx) => getRecordId(filteredRecords[idx], idx) === currentRecordId
      );

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const nextIndex = Math.min(currentIndex + 1, filteredRecords.length - 1);
        const nextId = getRecordId(filteredRecords[nextIndex], nextIndex);
        onRecordSelect(nextId);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prevIndex = Math.max(currentIndex - 1, 0);
        const prevId = getRecordId(filteredRecords[prevIndex], prevIndex);
        onRecordSelect(prevId);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentRecordId, filteredRecords, onRecordSelect]);

  // Auto-scroll to selected item
  useEffect(() => {
    if (selectedItemRef.current) {
      selectedItemRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [currentRecordId]);

  // Count records by status
  const statusCounts = React.useMemo(() => {
    return filteredRecords.reduce(
      (acc, _, index) => {
        const recordId = getRecordId(filteredRecords[index], index);
        const status = recordStatuses[recordId] || {
          approved: false,
          rejected: false,
          hasErrors: false,
          hasUnsavedChanges: false,
        };

        if (status.approved) acc.approved++;
        else if (status.rejected) acc.rejected++;
        else if (status.hasErrors) acc.error++;
        else acc.pending++;

        return acc;
      },
      { approved: 0, rejected: 0, error: 0, pending: 0 }
    );
  }, [filteredRecords, recordStatuses]);

  return (
    <div className={cn('flex flex-col h-full bg-white border-r', className)}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-900">
            Records ({filteredRecords.length})
          </h3>

          {/* Status summary */}
          <div className="flex gap-1">
            {statusCounts.approved > 0 && (
              <Badge variant="outline" className="text-xs bg-green-50 text-green-700">
                {statusCounts.approved}
              </Badge>
            )}
            {statusCounts.error > 0 && (
              <Badge variant="outline" className="text-xs bg-amber-50 text-amber-700">
                {statusCounts.error}
              </Badge>
            )}
            {statusCounts.rejected > 0 && (
              <Badge variant="outline" className="text-xs bg-red-50 text-red-700">
                {statusCounts.rejected}
              </Badge>
            )}
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search records..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9 text-sm"
          />
        </div>
      </div>

      {/* Record list */}
      <ScrollArea className="flex-1" ref={listRef}>
        {filteredRecords.length === 0 ? (
          <div className="p-8 text-center text-sm text-gray-500">
            {searchQuery ? 'No matching records found' : 'No records available'}
          </div>
        ) : (
          <div role="listbox" aria-label="Record list">
            {filteredRecords.map((record, index) => {
              const recordId = getRecordId(record, index);
              const isSelected = recordId === currentRecordId;
              const isChecked = selectedRecordIds?.has(recordId);
              const status = recordStatuses[recordId] || {
                approved: false,
                rejected: false,
                hasErrors: false,
                hasUnsavedChanges: false,
              };

              return (
                <div
                  key={recordId}
                  ref={isSelected ? selectedItemRef : null}
                >
                  <RecordItem
                    record={record}
                    recordId={recordId}
                    index={index}
                    isSelected={isSelected}
                    isChecked={isChecked}
                    status={status}
                    identifierField={identifierField}
                    titleField={titleField}
                    onClick={() => onRecordSelect(recordId)}
                    onCheckboxChange={
                      onRecordToggle
                        ? (checked) => onRecordToggle(recordId)
                        : undefined
                    }
                    showCheckbox={showCheckboxes}
                  />
                </div>
              );
            })}
          </div>
        )}
      </ScrollArea>

      {/* Footer actions */}
      {showCheckboxes && selectedRecordIds && selectedRecordIds.size > 0 && (
        <div className="p-3 border-t bg-gray-50">
          <div className="text-xs text-gray-600 mb-2">
            {selectedRecordIds.size} record(s) selected
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              className="flex-1 text-xs"
              onClick={() => {
                // Bulk approve handler (implement in parent)
              }}
            >
              Approve Selected
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="flex-1 text-xs"
              onClick={() => {
                // Clear selection handler (implement in parent)
              }}
            >
              Clear
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
