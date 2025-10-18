# Implementation Example: Refactoring DataPanel for Adaptive Views

This document provides a step-by-step example of how to refactor your existing `DataPanel.tsx` to support the new adaptive multi-view system.

---

## Before: Current Implementation

Your current `DataPanel.tsx` (lines 282-377) has a single `TableView` function that handles both single records and arrays:

```typescript
// Current: Lines 314-377
if (isArray && data.length > 0) {
  // Multi-record table view
  return <table>...</table>;
}

// Single record view
return <table>...</table>;
```

**This works well for simple schemas**, but struggles with complex multi-record data (10+ fields with nesting).

---

## After: Adaptive View Router

The refactored version will:
1. Analyze schema complexity
2. Route to the appropriate view component
3. Maintain backwards compatibility for simple schemas

---

## Step 1: Update Imports

Add new imports to `DataPanel.tsx`:

```typescript
// Add these imports at the top
import { analyzeSchema, isMultiRecordSchema, getPrimaryIdentifier, getTitleField } from '@/lib/schema-analyzer';
import { useMemo } from 'react';

// Later, when components are created:
// import { CompactTableView } from './CompactTableView';
// import { TableWithDrawerView } from './TableWithDrawerView';
// import { MasterDetailView } from './MasterDetailView';
```

---

## Step 2: Create CompactTableView Component

First, extract your existing multi-record table into a separate component:

**File:** `/frontend/components/review/CompactTableView.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { FieldMetadata } from '@/lib/schema-analyzer';

interface CompactTableViewProps {
  records: any[];
  fieldMetadata: FieldMetadata[];
  pendingEdits: Record<string, any>;
  onFieldUpdate: (fieldName: string, value: any, recordIndex: number) => void;
}

export function CompactTableView({
  records,
  fieldMetadata,
  pendingEdits,
  onFieldUpdate,
}: CompactTableViewProps) {
  // Reuse your existing EditableCell component
  // Copy the EditableCell component from DataPanel.tsx here
  // ... (implementation same as current lines 177-228)

  const columnTypes = fieldMetadata.map(field => ({
    name: field.name,
    type: field.type === 'long' ? 'long' : field.type === 'short' ? 'short' : 'medium'
  }));

  const hasEdit = (fieldName: string, recordIndex: number): boolean => {
    const editKey = `${recordIndex}.${fieldName}`;
    return editKey in pendingEdits;
  };

  const getFieldValue = (fieldName: string, recordIndex: number): any => {
    const editKey = `${recordIndex}.${fieldName}`;
    if (pendingEdits[editKey]) {
      return pendingEdits[editKey];
    }
    return records[recordIndex]?.[fieldName];
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-black">
          {records.length} record{records.length !== 1 ? 's' : ''} extracted
        </div>
        {records.length > 1 && (
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
                <th className="sticky left-0 z-10 bg-gray-50 text-left py-2 px-3 font-medium text-sm text-gray-700 border-r">
                  #
                </th>
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
              {records.map((record, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50">
                  <td className="sticky left-0 z-10 bg-white py-2 px-3 text-sm text-gray-500 border-r">
                    {idx + 1}
                  </td>
                  {columnTypes.map(({ name, type }) => (
                    <EditableCell
                      key={name}
                      value={getFieldValue(name, idx)}
                      fieldName={name}
                      recordIndex={idx}
                      hasEdit={hasEdit(name, idx)}
                      onEdit={(val) => onFieldUpdate(name, val, idx)}
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

// Helper functions (copy from DataPanel.tsx)
function getColumnWidthClass(columnType: string): string {
  switch (columnType) {
    case 'short': return 'min-w-[100px] max-w-[150px]';
    case 'medium': return 'min-w-[150px] max-w-[250px]';
    case 'long': return 'min-w-[200px] max-w-[400px]';
    default: return 'min-w-[150px]';
  }
}

function formatFieldName(fieldName: string): string {
  return fieldName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
```

---

## Step 3: Update DataPanel TableView Function

Modify the `TableView` function in `DataPanel.tsx` to use complexity analysis:

```typescript
function TableView({ file }: { file: FileReviewStatus }) {
  const { updateField, pendingEdits } = useReviewStore();
  const data = file.extracted_data;
  const isArray = Array.isArray(data);

  // NEW: Analyze schema complexity
  const complexity = useMemo(() => {
    if (!isArray || !data.length) return null;
    return analyzeSchema(data, null);
  }, [data, isArray]);

  const handleCellEdit = (fieldName: string, value: any, recordIndex?: number) => {
    updateField(fieldName, value, recordIndex);
  };

  // ... (keep existing getFieldValue and hasEdit functions)

  // MODIFIED: Add complexity-based routing for multi-record
  if (isArray && data.length > 0) {
    // For now, use existing table for simple/moderate
    // Later, we'll add routing here
    if (complexity && complexity.level === 'complex') {
      // TODO: Use MasterDetailView when ready
      // return <MasterDetailView ... />;

      // For now, show a message
      return (
        <div className="p-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
              <strong>Complex schema detected:</strong> {complexity.fieldCount} fields,
              {complexity.nestedFields > 0 && ` ${complexity.nestedFields} nested fields`}
            </p>
            <p className="text-xs text-blue-600 mt-1">
              Recommended view: {complexity.recommendedView}
            </p>
          </div>

          {/* Fall back to existing table for now */}
          <CompactTableView
            records={data}
            fieldMetadata={complexity.fieldMetadata}
            pendingEdits={pendingEdits}
            onFieldUpdate={handleCellEdit}
          />
        </div>
      );
    }

    // Existing table view for simple/moderate complexity
    // (Keep your current implementation lines 315-377)
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
        {/* ... existing implementation ... */}
      </div>
    );
  }

  // Single record view (no changes)
  const entries = Object.entries(data);
  return (
    <div className="p-6">
      {/* ... existing implementation ... */}
    </div>
  );
}
```

---

## Step 4: Test with IT Audit Example

Create a test file with complex schema to see the detection in action:

```typescript
// Example IT Audit data structure
const complexData = [
  {
    reference: 'ISMC-2024-001',
    category: 'Access Control',
    agency: 'IT Department',
    title: 'Critical gap in user access management',
    subtitle: 'Inadequate segregation of duties',
    description: 'The current access control framework lacks proper segregation of duties, allowing users to have conflicting permissions that could lead to unauthorized actions.',
    risk_statement: 'Without proper segregation of duties, there is significant risk of fraud, data breaches, and compliance violations.',
    root_cause: 'Inadequate training and lack of automated controls',
    root_cause_category: 'People',
    recommendations: [
      {
        description: 'Implement multi-factor authentication',
        priority: 'high',
        timeline: '30 days'
      },
      {
        description: 'Update access control policies',
        priority: 'medium',
        timeline: '60 days'
      }
    ]
  },
  // ... more records
];
```

When you process this data, you should see:
- Blue info box showing "Complex schema detected: 10 fields, 1 nested fields"
- "Recommended view: master-detail"
- Table view displayed (fallback until MasterDetailView is implemented)

---

## Step 5: Progressive Enhancement Plan

### Week 1: Detection Only (Current Step)
- ✅ Schema analyzer integrated
- ✅ Complexity detection showing in UI
- ✅ Existing table still used for all schemas
- **Result:** No user-facing changes yet, just detection

### Week 2: Add Master-Detail for Complex Schemas
```typescript
// In TableView function, replace TODO with:
if (complexity && complexity.level === 'complex') {
  const identifierField = getPrimaryIdentifier(complexity.fieldMetadata) || 'id';
  const titleField = getTitleField(complexity.fieldMetadata);

  return (
    <MasterDetailView
      records={data}
      fieldMetadata={complexity.fieldMetadata}
      identifierField={identifierField}
      titleField={titleField}
      pendingEdits={pendingEdits}
      onFieldUpdate={handleCellEdit}
    />
  );
}
```

### Week 3: Add Table-Drawer for Moderate Schemas
```typescript
if (complexity && complexity.level === 'moderate') {
  return (
    <TableWithDrawerView
      records={data}
      fieldMetadata={complexity.fieldMetadata}
      pendingEdits={pendingEdits}
      onFieldUpdate={handleCellEdit}
    />
  );
}
```

### Week 4: User Preference Toggle
```typescript
// Add view mode selector to header
<div className="flex items-center gap-2">
  <span className="text-xs text-gray-600">View:</span>
  <Select value={viewMode} onValueChange={setViewMode}>
    <SelectItem value="auto">Auto ({complexity.recommendedView})</SelectItem>
    <SelectItem value="table">Compact Table</SelectItem>
    <SelectItem value="table-drawer">Table + Drawer</SelectItem>
    <SelectItem value="master-detail">Master-Detail</SelectItem>
  </Select>
</div>
```

---

## Step 6: Store Updates for Record-Level State

When you're ready to implement MasterDetailView, update the store:

**File:** `/frontend/lib/store.ts`

Add these interfaces:

```typescript
interface RecordApproval {
  approved: boolean;
  rejected: boolean;
  rejectedReason?: string;
  approvedAt?: Date;
}

interface ReviewStore {
  // ... existing fields ...

  // NEW: Record-level state
  currentRecordId: string | null;
  recordApprovals: Record<string, RecordApproval>;
  recordValidationErrors: Record<string, Record<string, string>>;

  // NEW: Actions
  setCurrentRecord: (recordId: string | null) => void;
  approveRecord: (fileId: string, recordId: string) => void;
  rejectRecord: (fileId: string, recordId: string, reason: string) => void;
}
```

Implementation:

```typescript
export const useReviewStore = create<ReviewStore>((set, get) => ({
  // ... existing state ...

  currentRecordId: null,
  recordApprovals: {},
  recordValidationErrors: {},

  setCurrentRecord: (recordId) => {
    set({ currentRecordId: recordId });
  },

  approveRecord: (fileId, recordId) => {
    const { recordApprovals } = get();
    set({
      recordApprovals: {
        ...recordApprovals,
        [`${fileId}:${recordId}`]: {
          approved: true,
          rejected: false,
          approvedAt: new Date(),
        },
      },
    });
  },

  rejectRecord: (fileId, recordId, reason) => {
    const { recordApprovals } = get();
    set({
      recordApprovals: {
        ...recordApprovals,
        [`${fileId}:${recordId}`]: {
          approved: false,
          rejected: true,
          rejectedReason: reason,
        },
      },
    });
  },
}));
```

---

## Step 7: Update Approval Logic

When using record-level approvals (complex schemas), update the `handleApprove` function:

```typescript
const handleApprove = async () => {
  try {
    setIsApproving(true);

    // Check if we have record-level approvals
    const hasRecordApprovals = Object.keys(recordApprovals).some(key =>
      key.startsWith(`${file.file_path}:`)
    );

    if (hasRecordApprovals) {
      // Count approved vs total records
      const fileRecords = data.length;
      const approvedRecords = Object.entries(recordApprovals)
        .filter(([key, status]) =>
          key.startsWith(`${file.file_path}:`) && status.approved
        ).length;

      if (approvedRecords < fileRecords) {
        // Show confirmation dialog
        const shouldContinue = window.confirm(
          `Only ${approvedRecords} of ${fileRecords} records are approved. ` +
          `Continue approving the file?`
        );
        if (!shouldContinue) {
          setIsApproving(false);
          return;
        }
      }
    }

    // Save changes and approve
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
```

---

## Testing Checklist

### Phase 1: Detection Only
- [ ] Simple schema (< 5 fields) → Shows "Simple" in blue box
- [ ] Moderate schema (6-10 fields) → Shows "Moderate" in blue box
- [ ] Complex schema (10+ fields or nested) → Shows "Complex" in blue box
- [ ] Nested array detected → Shows nested field count
- [ ] All existing functionality still works

### Phase 2: MasterDetailView
- [ ] Complex schema → Shows master-detail view
- [ ] Can select records in left navigator
- [ ] Can edit fields in right detail panel
- [ ] Unsaved changes tracked per-record
- [ ] Keyboard navigation works (↑↓ arrows)
- [ ] Search filters records

### Phase 3: TableWithDrawerView
- [ ] Moderate schema → Shows table with drawer
- [ ] Clicking row action [⋮] opens drawer
- [ ] Can edit in drawer
- [ ] Changes persist when closing drawer

### Phase 4: User Preference
- [ ] View mode selector appears in header
- [ ] Can manually override auto-selected view
- [ ] Preference persists between file navigations

---

## Quick Start: Minimal Implementation

If you want to start **right now** with minimal code changes:

1. **Copy** `/frontend/lib/schema-analyzer.ts` (already created ✓)
2. **Copy** `/frontend/components/review/RecordNavigator.tsx` (already created ✓)
3. **Install** missing shadcn components:
   ```bash
   npx shadcn-ui@latest add badge
   npx shadcn-ui@latest add checkbox
   ```
4. **Add** to `DataPanel.tsx` (around line 285):
   ```typescript
   import { analyzeSchema } from '@/lib/schema-analyzer';

   // Inside TableView function, after line 284:
   const complexity = useMemo(() => {
     if (isArray && data.length > 0) {
       return analyzeSchema(data);
     }
     return null;
   }, [data, isArray]);

   // After line 313, add this before the existing table render:
   if (complexity) {
     console.log('Schema Complexity:', complexity);
     // You can now see complexity info in browser console
   }
   ```

That's it! Now when you process files, check the browser console to see complexity analysis.

---

## File Structure Summary

After full implementation, you'll have:

```
frontend/components/review/
├── DataPanel.tsx                 # Router (modified)
├── CompactTableView.tsx          # Extracted from DataPanel (new)
├── TableWithDrawerView.tsx       # Moderate complexity (new)
├── MasterDetailView.tsx          # Complex schemas (new)
├── RecordNavigator.tsx           # Left sidebar (created ✓)
├── RecordDetailView.tsx          # Form editor (new)
├── NestedFieldRenderer.tsx       # Arrays/objects (new)
└── ApprovalControls.tsx          # Approval buttons (new)

frontend/lib/
├── schema-analyzer.ts            # Complexity detection (created ✓)
└── store.ts                      # Add record state (modify)
```

---

## Troubleshooting

### Issue: "analyzeSchema is not defined"
**Solution:** Make sure you imported it:
```typescript
import { analyzeSchema } from '@/lib/schema-analyzer';
```

### Issue: "complexity is null"
**Solution:** Check that you're calling it on multi-record data:
```typescript
const complexity = useMemo(() => {
  if (isArray && data.length > 0) {
    return analyzeSchema(data);  // Pass the array
  }
  return null;
}, [data, isArray]);
```

### Issue: "RecordNavigator component not found"
**Solution:** Verify the file exists at `/frontend/components/review/RecordNavigator.tsx`

### Issue: TypeScript errors in RecordNavigator
**Solution:** Install missing shadcn components:
```bash
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add scroll-area
```

---

## Next Steps

1. ✅ Schema analyzer created
2. ✅ RecordNavigator created
3. **Current step:** Test complexity detection with your IT Audit schema
4. **Next:** Create MasterDetailView component
5. **Then:** Integrate approval workflow

Refer to `/docs/UI_DESIGN_MULTI_RECORD_REVIEW.md` for the complete design specification.
