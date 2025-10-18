# Enhanced Table View for Multi-Record Multi-Column Scenarios

**Document Version:** 1.0
**Date:** October 18, 2025
**Status:** Design Proposal
**Target:** Complex multi-record schemas with 10-20+ fields

---

## Executive Summary

This document outlines the design for an enhanced table view to handle complex multi-record scenarios in the Review Workspace. The design maintains the current table-based approach while adding smart features for usability, performance, and data management when dealing with documents that extract 5-50+ records with 10-20+ fields each.

**Key Principle:** Keep the table format, make it smarter and more powerful.

---

## Problem Statement

### Current State
The review workspace currently supports:
- ✅ **Simple schemas**: Single record per file (e.g., document metadata)
- ✅ **Basic multi-record**: Multiple records with 1-3 fields (e.g., report summaries)

### Gap
We need to support:
- ❌ **Complex multi-record**: 10-50 records per file
- ❌ **Many columns**: 10-20+ fields per record
- ❌ **Varied data types**: Short IDs, long descriptions, nested arrays
- ❌ **Efficient editing**: Quick navigation and bulk operations
- ❌ **Clear approval**: Individual record validation and approval

### Real-World Examples

| Schema | Records/File | Fields/Record | Challenges |
|--------|--------------|---------------|------------|
| IT Audit Findings | 5-15 | 9 + nested array | Long text fields, nested recommendations |
| Lease Agreements | 1-5 | 12 | Mixed field lengths, dates, validation |
| Loan Agreements | 1-3 | 11 | Complex validation rules, financial data |
| Meeting Summaries | 3-10 | 8 | Multiple attendees, nested arrays |
| Valuation Reports | 1-5 | 16 + nested comparables | Nested objects, currency fields |

---

## Design Goals

1. **Maintain Table Format**: Keep the familiar spreadsheet-like interface
2. **Smart Column Management**: Auto-size columns, sticky headers, horizontal scroll
3. **Efficient Editing**: Fast inline editing with keyboard navigation
4. **Record-Level Operations**: Individual record approval, validation, deletion
5. **Bulk Actions**: Select multiple records for batch operations
6. **Performance**: Handle 50+ records without lag
7. **Accessibility**: Keyboard shortcuts, screen reader support
8. **Progressive Enhancement**: Simple schemas stay simple

---

## Core Design Concepts

### 1. Intelligent Column Sizing

**Automatic Width Calculation**
```typescript
// Already implemented in DataPanel.tsx
type ColumnType = 'short' | 'medium' | 'long';

function getColumnType(fieldName: string, sampleValues: any[]): ColumnType {
  // Analyze field name and content
  if (/(id|num|count|age|year|code)$/.test(lowerField)) return 'short';
  if (/(name|email|phone|city)/.test(lowerField)) return 'medium';
  if (/(description|summary|comment)/.test(lowerField)) return 'long';

  // Analyze max content length
  const maxLength = Math.max(...sampleValues.map(v => String(v).length));
  if (maxLength <= 15) return 'short';
  if (maxLength <= 50) return 'medium';
  return 'long';
}
```

**Width Classes**
- **Short**: `min-w-[100px] max-w-[150px]` - IDs, codes, dates
- **Medium**: `min-w-[150px] max-w-[250px]` - Names, categories
- **Long**: `min-w-[200px] max-w-[400px]` - Descriptions, summaries

**User Override**
- Double-click column divider to resize manually
- "Fit to content" option in column header menu
- Save column preferences per schema type

### 2. Enhanced Row Management

**Row Number Column (Sticky Left)**
```
┌───┬──────────┬──────────┬──────────┐
│ # │ Agency   │ Title    │ Status   │
├───┼──────────┼──────────┼──────────┤
│ 1 │ MinFin   │ Access.. │ ✓ Valid  │
│ 2 │ MOH      │ Backup.. │ ⚠ Review │
│ 3 │ MOM      │ Procure..│ ✓ Valid  │
└───┴──────────┴──────────┴──────────┘
```

**Row Selection**
- Checkbox in row number column
- Click row number to select entire row
- Shift+Click for range selection
- Cmd/Ctrl+Click for multi-select
- Select All checkbox in header

**Row Actions Menu**
- Three-dot menu in row number column
- Actions: Edit, Approve, Reject, Duplicate, Delete
- Keyboard: Right-click on row number

### 3. Record Status Indicators

**Visual Status System**
```typescript
type RecordStatus =
  | 'not_reviewed'    // ○ Gray circle
  | 'in_review'       // ● Orange filled circle
  | 'approved'        // ✓ Green checkmark
  | 'rejected'        // ✗ Red X
  | 'has_errors'      // ⚠ Yellow warning
  | 'needs_attention'; // ! Red exclamation

interface RecordMetadata {
  status: RecordStatus;
  validation_errors: string[];
  approved_by?: string;
  approved_at?: string;
  comments?: string;
}
```

**Status Column (Always Visible)**
- Positioned as first data column (after row number)
- Width: 80px fixed
- Shows icon + status text on hover
- Sortable by status

**Status Badge Colors**
- Not Reviewed: `bg-gray-100 text-gray-600`
- In Review: `bg-orange-100 text-orange-700`
- Approved: `bg-green-100 text-green-700`
- Rejected: `bg-red-100 text-red-700`
- Has Errors: `bg-yellow-100 text-yellow-700`

### 4. Column Header Enhancements

**Enhanced Header Bar**
```
┌──────────────────────────────────────────────────┐
│ 12 records • 3 selected • 8 approved             │
├───┬────────┬──────────────────┬─────────────────┤
│ □ │ Status │ Agency ↓         │ Title           │
│   │        │ [Filter: All]    │ [Search...]     │
└───┴────────┴──────────────────┴─────────────────┘
```

**Features per Column**
1. **Sort Indicators**: ↑↓ arrows, click to cycle (asc → desc → none)
2. **Filter Dropdown**: Click funnel icon for column-specific filters
3. **Search Box**: Text search within column (for string fields)
4. **Column Menu**: Three-dot menu with:
   - Hide column
   - Freeze column
   - Resize to fit
   - Show statistics (count, unique values)

**Sticky Headers**
- Header row stays fixed when scrolling vertically
- Row numbers stay fixed when scrolling horizontally
- Z-index layering for proper overlap

### 5. Smart Cell Editing

**Inline Editing (Current)**
```typescript
// Keep existing EditableCell component
<input
  type="text"
  value={displayValue}
  onChange={(e) => onEdit(e.target.value)}
  onDoubleClick={handleExpandEdit}
  className="w-full bg-transparent border-0 p-1 focus:ring-1 focus:ring-brand-orange-500"
/>
```

**Expanded Editing (Current)**
- Double-click opens popover with large textarea
- Better for long text fields
- Keep existing implementation

**New: Keyboard Navigation**
```typescript
// Navigate between cells like Excel/Google Sheets
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Tab') {
    // Tab: Move to next cell
    // Shift+Tab: Move to previous cell
    focusNextCell(e.shiftKey ? -1 : 1);
  } else if (e.key === 'Enter') {
    if (e.ctrlKey || e.metaKey) {
      // Ctrl+Enter: Move to next row, same column
      focusNextRow();
    } else {
      // Enter: Start editing current cell
      startEditing();
    }
  } else if (e.key === 'Escape') {
    // Esc: Cancel editing
    cancelEditing();
  } else if (['ArrowUp', 'ArrowDown'].includes(e.key)) {
    // Arrow keys: Navigate rows
    focusRow(e.key === 'ArrowUp' ? -1 : 1);
  }
};
```

**Field Type-Specific Editors**
- **Text**: Current text input
- **Long Text**: Textarea with character counter
- **Date**: Date picker (shadcn/ui Popover + Calendar)
- **Select**: Dropdown for enums (Literal types)
- **Number**: Number input with validation
- **Array**: See section 6 below

### 6. Nested Data Handling

**Problem**: Some schemas have nested arrays/objects (e.g., IT Audit recommendations)

**Solution: Inline Badge with Modal**

**Visual in Table Cell**
```
┌─────────────────────────────────┐
│ Recommendations                 │
├─────────────────────────────────┤
│ 🔗 3 items [View/Edit]          │
└─────────────────────────────────┘
```

**On Click: Full-Screen Modal**
```typescript
<Dialog>
  <DialogContent className="max-w-4xl max-h-[90vh]">
    <DialogHeader>
      <DialogTitle>Recommendations (Record #2)</DialogTitle>
    </DialogHeader>

    <div className="space-y-4">
      {recommendations.map((rec, idx) => (
        <Card key={idx}>
          <CardHeader>
            <CardTitle>Recommendation {idx + 1}</CardTitle>
            <Button onClick={() => removeItem(idx)}>Remove</Button>
          </CardHeader>
          <CardContent>
            <Label>Recommendation</Label>
            <Textarea
              value={rec.recommendation}
              onChange={(e) => updateItem(idx, 'recommendation', e.target.value)}
            />

            <Label>Management Comment</Label>
            <Textarea
              value={rec.management_comment}
              onChange={(e) => updateItem(idx, 'management_comment', e.target.value)}
            />
          </CardContent>
        </Card>
      ))}

      <Button onClick={addNewItem}>+ Add Recommendation</Button>
    </div>

    <DialogFooter>
      <Button variant="outline" onClick={cancel}>Cancel</Button>
      <Button onClick={save}>Save Changes</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

**For Simple Objects**
- Show as formatted JSON string in cell
- Click to view/edit in modal with JSON editor or form fields

---

## Advanced Features

### 7. Bulk Operations Toolbar

**Appears when records are selected**
```
┌─────────────────────────────────────────────────┐
│ 3 records selected                              │
│ [Approve Selected] [Reject Selected] [Delete]   │
│ [Copy] [Export to Excel] [Clear Selection]     │
└─────────────────────────────────────────────────┘
```

**Actions Available**
- **Approve Selected**: Bulk approve valid records
- **Reject Selected**: Bulk reject with shared reason
- **Delete Selected**: Remove records from review
- **Copy**: Copy to clipboard (TSV format)
- **Export**: Download selected records as Excel/CSV
- **Apply Transformation**: Bulk edit field (e.g., uppercase all agencies)

### 8. Filtering and Search

**Global Search Bar**
```typescript
<Input
  placeholder="Search across all fields..."
  value={globalSearch}
  onChange={(e) => setGlobalSearch(e.target.value)}
  className="w-full mb-4"
/>
```

**Column-Specific Filters**
```typescript
// For string fields
type StringFilter = {
  contains?: string;
  equals?: string;
  startsWith?: string;
  endsWith?: string;
};

// For status/enum fields
type EnumFilter = {
  in?: string[];  // Multiple selection
};

// For date fields
type DateFilter = {
  from?: Date;
  to?: Date;
  equals?: Date;
};
```

**Filter UI**
- Click filter icon in column header
- Opens popover with filter controls
- Shows active filter count badge
- "Clear all filters" button

### 9. Validation and Error Display

**Real-Time Validation**
```typescript
interface FieldValidation {
  field_name: string;
  record_index: number;
  errors: string[];
  warnings: string[];
}

// Validate on blur
const validateField = (fieldName: string, value: any, recordIndex: number) => {
  const schema = AVAILABLE_MODELS[currentSchema];
  const fieldSchema = schema.shape[fieldName];

  try {
    fieldSchema.parse(value);
    return { valid: true };
  } catch (error) {
    return {
      valid: false,
      errors: error.errors.map(e => e.message)
    };
  }
};
```

**Visual Indicators**
- **Valid**: Green checkmark in status column
- **Warning**: Yellow triangle, edits pending save
- **Error**: Red X, validation failed
- **Cell Border**: Red border on invalid field
- **Tooltip**: Hover to see error message

**Validation Summary Panel**
```
┌─────────────────────────────────────┐
│ ⚠ 2 records have validation errors  │
│                                      │
│ Record #2: Agency required           │
│ Record #5: Invalid date format       │
│                                      │
│ [Fix Issues] [Approve Valid Only]   │
└─────────────────────────────────────┘
```

### 10. Performance Optimizations

**Virtual Scrolling**
```typescript
// Use @tanstack/react-virtual for large datasets
import { useVirtualizer } from '@tanstack/react-virtual';

const rowVirtualizer = useVirtualizer({
  count: data.length,
  getScrollElement: () => scrollElementRef.current,
  estimateSize: () => 48, // Row height in pixels
  overscan: 10, // Render 10 extra rows
});

// Only render visible rows
{rowVirtualizer.getVirtualItems().map((virtualRow) => {
  const record = data[virtualRow.index];
  return <TableRow key={virtualRow.key} record={record} />;
})}
```

**Benefits**
- Smooth scrolling with 500+ records
- Reduced initial render time
- Lower memory usage

**Lazy Loading Nested Data**
- Don't load nested arrays until modal is opened
- Fetch recommendations on-demand
- Cache in component state

**Memoization**
```typescript
// Memoize expensive calculations
const columnTypes = useMemo(() =>
  columns.map(col => ({
    name: col,
    type: getColumnType(col, data.map(r => r[col]))
  })),
  [columns, data]
);

const filteredData = useMemo(() =>
  applyFilters(data, filters),
  [data, filters]
);

const sortedData = useMemo(() =>
  applySorting(filteredData, sortState),
  [filteredData, sortState]
);
```

---

## Approval Workflow

### 11. Record-Level Approval

**Current State**
- File-level approval: Approve all records at once
- Works well for simple schemas

**Enhanced State**
- **Default**: File-level approval (backwards compatible)
- **Option**: Per-record approval for complex schemas
- **Toggle**: User can switch between modes

**Per-Record Approval UI**

**In Table**
```
┌───┬──────────┬────────┬──────────────┬─────────┐
│ # │ Status   │ Agency │ Title        │ Actions │
├───┼──────────┼────────┼──────────────┼─────────┤
│ 1 │ ✓ Appr.. │ MinFin │ Access Ctrl..│ [Edit]  │
│ 2 │ ○ Pend.. │ MOH    │ Backup Pol.. │ [Approve]│
│ 3 │ ⚠ Error  │ MOM    │ Procurement..│ [Fix]   │
└───┴──────────┴────────┴──────────────┴─────────┘
```

**Approval Actions Column**
- **Pending**: [Approve] [Reject] buttons
- **Approved**: ✓ badge, [Undo] button
- **Rejected**: ✗ badge, [Re-review] button
- **Error**: ⚠ badge, [Fix] button (focuses on error field)

**Quick Approve Keyboard Shortcut**
- Focus on row
- Press `Cmd/Ctrl + Enter` to approve current record
- Automatically moves to next unapproved record

### 12. Bulk Approval Options

**Approve All Valid**
```typescript
const approveAllValid = () => {
  const validRecords = data.filter(record => {
    const validation = validateRecord(record);
    return validation.valid;
  });

  batchApproveRecords(validRecords.map(r => r.id));
};
```

**Button in Toolbar**
```
[Approve All Valid (8)] [Approve Selected (3)] [Approve All]
```

**Confirmation Dialog**
```
┌─────────────────────────────────────────────────┐
│ Approve 8 valid records?                        │
│                                                 │
│ • 8 records will be approved                    │
│ • 2 records with errors will be skipped         │
│ • 2 records need review                         │
│                                                 │
│ [Cancel] [Approve Valid Records]                │
└─────────────────────────────────────────────────┘
```

---

## UI Layout Specifications

### 13. DataPanel Component Structure

```tsx
<div className="h-full flex flex-col bg-white">
  {/* Header Bar */}
  <div className="border-b p-3">
    <RecordSummary /> {/* "12 records • 3 selected • 8 approved" */}
    <ActionButtons /> {/* Approve, Export, etc. */}
  </div>

  {/* Bulk Actions Toolbar (conditional) */}
  {selectedRecords.length > 0 && (
    <BulkActionsToolbar selectedRecords={selectedRecords} />
  )}

  {/* Global Search & Filters */}
  <div className="p-3 border-b bg-gray-50">
    <GlobalSearch />
    <ActiveFilters />
  </div>

  {/* Table Container */}
  <ScrollArea className="flex-1">
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <StickyTableHeader />
        <VirtualizedTableBody />
      </table>
    </div>
  </ScrollArea>

  {/* Status Footer */}
  <div className="border-t p-3 bg-gray-50">
    <ValidationSummary /> {/* Error count, warnings */}
    <ProgressIndicator /> {/* "8/12 approved" */}
  </div>
</div>
```

### 14. Responsive Breakpoints

**Desktop (>1200px)**
- Full table view
- All columns visible
- Side-by-side document viewer + data panel

**Tablet (768-1200px)**
- Scrollable table
- Some columns may auto-hide (least important)
- Collapsed sidebar option

**Mobile (<768px)**
- Switch to card view automatically
- Stack records vertically
- Tap to expand full record

---

## Implementation Plan

### Phase 1: Foundation Enhancements (Week 1)

**Tasks**
1. Add record status tracking to ReviewSession type
2. Add per-record metadata (status, validation, approval)
3. Update API endpoints to support record-level operations
4. Add status column to table view

**Files to Modify**
- `frontend/types/index.ts`: Add RecordMetadata interface
- `backend/infotransform/api/review_api.py`: Add per-record approval endpoint
- `frontend/components/review/DataPanel.tsx`: Add status column

**Acceptance Criteria**
- Each record has its own status (not_reviewed, approved, etc.)
- Status column shows appropriate icons
- Backend persists per-record status

### Phase 2: Row Management (Week 1-2)

**Tasks**
1. Add row selection (checkboxes)
2. Implement bulk actions toolbar
3. Add row action menu (three dots)
4. Keyboard navigation (Tab, Enter, Arrows)

**New Components**
- `RowSelector.tsx`: Checkbox component with shift-click support
- `BulkActionsToolbar.tsx`: Toolbar shown when records selected
- `RowActionMenu.tsx`: Dropdown menu in row number column

**Acceptance Criteria**
- Can select individual records via checkbox
- Can select range with Shift+Click
- Can select all with header checkbox
- Bulk actions work on selected records
- Keyboard shortcuts navigate cells

### Phase 3: Column Enhancements (Week 2)

**Tasks**
1. Add sort indicators to column headers
2. Implement column filtering (dropdown)
3. Add column menu (hide, freeze, resize)
4. Global search across all fields

**New Components**
- `ColumnHeader.tsx`: Enhanced header with sort, filter, menu
- `ColumnFilterPopover.tsx`: Filter UI per column type
- `GlobalSearchBar.tsx`: Search across all columns

**Acceptance Criteria**
- Can sort by any column (asc/desc)
- Can filter by column-specific criteria
- Can hide/show columns
- Global search highlights matching cells

### Phase 4: Validation & Approval (Week 3)

**Tasks**
1. Real-time field validation using Pydantic schemas
2. Visual error indicators (red borders, tooltips)
3. Validation summary panel
4. Per-record approval workflow

**New Components**
- `ValidationIndicator.tsx`: Shows validation status per cell
- `ValidationSummary.tsx`: Panel showing all errors
- `RecordApprovalButtons.tsx`: Approve/reject buttons per row

**Acceptance Criteria**
- Fields validate on blur
- Invalid fields show red border + tooltip
- Can approve individual records
- Can bulk approve valid records
- Validation errors prevent approval

### Phase 5: Nested Data Support (Week 3-4)

**Tasks**
1. Detect nested arrays/objects in schema
2. Show badge with count in table cell
3. Modal editor for nested data
4. Add/remove items in nested arrays

**New Components**
- `NestedDataBadge.tsx`: Clickable badge showing "3 items"
- `NestedArrayEditor.tsx`: Modal with card-based editor
- `NestedObjectEditor.tsx`: Modal with form fields

**Acceptance Criteria**
- Nested arrays show as "🔗 X items [View/Edit]"
- Modal opens on click
- Can add/remove nested items
- Changes save to main record

### Phase 6: Performance & Polish (Week 4)

**Tasks**
1. Implement virtual scrolling (@tanstack/react-virtual)
2. Memoize expensive calculations
3. Lazy load nested data
4. Add loading states and skeletons
5. Accessibility audit (WCAG 2.1 AA)

**Optimizations**
- Virtual scrolling for 50+ records
- Debounced search and filter
- Lazy nested data loading
- Request animation frame for smooth scrolling

**Acceptance Criteria**
- Smooth scrolling with 100+ records
- Search/filter responds in <100ms
- No layout shift on load
- Keyboard navigation works throughout
- Screen reader announces status changes

---

## Technical Specifications

### Data Structures

```typescript
// Enhanced FileReviewStatus with per-record metadata
interface FileReviewStatus {
  file_id: string;
  filename: string;
  status: FileStatus; // Overall file status
  extracted_data: RecordData[] | SingleRecordData;

  // New: Per-record metadata
  record_metadata?: RecordMetadata[];

  edits?: FieldEdit[];
  approval_metadata?: ApprovalMetadata;
}

interface RecordMetadata {
  record_index: number;
  status: RecordStatus;
  validation_errors: ValidationError[];
  approved_by?: string;
  approved_at?: string;
  rejected_reason?: string;
  comments?: string;
}

interface ValidationError {
  field_name: string;
  error_type: 'required' | 'invalid_format' | 'out_of_range' | 'custom';
  message: string;
}

type RecordStatus =
  | 'not_reviewed'
  | 'in_review'
  | 'approved'
  | 'rejected'
  | 'has_errors'
  | 'needs_attention';
```

### API Endpoints

```python
# New endpoints in review_api.py

@router.post("/api/review/{session_id}/files/{file_id}/records/{record_index}/approve")
async def approve_record(
    session_id: str,
    file_id: str,
    record_index: int,
    approval: ApprovalMetadata
):
    """Approve a single record within a file"""
    pass

@router.post("/api/review/{session_id}/files/{file_id}/records/bulk-approve")
async def bulk_approve_records(
    session_id: str,
    file_id: str,
    record_indices: List[int],
    approval: ApprovalMetadata
):
    """Approve multiple records at once"""
    pass

@router.post("/api/review/{session_id}/files/{file_id}/records/{record_index}/validate")
async def validate_record(
    session_id: str,
    file_id: str,
    record_index: int,
    data: Dict[str, Any]
):
    """Validate a record against its Pydantic schema"""
    pass
```

### Component Props

```typescript
// Enhanced TableView props
interface TableViewProps {
  file: FileReviewStatus;
  onRecordSelect?: (indices: number[]) => void;
  onRecordApprove?: (index: number) => Promise<void>;
  onBulkApprove?: (indices: number[]) => Promise<void>;
  enablePerRecordApproval?: boolean;
  enableBulkActions?: boolean;
}

// New ColumnHeader props
interface ColumnHeaderProps {
  column: string;
  type: ColumnType;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: (direction: 'asc' | 'desc' | null) => void;
  onFilter?: (filter: ColumnFilter) => void;
  onHide?: () => void;
  onResize?: (width: number) => void;
}

// New RecordRow props
interface RecordRowProps {
  record: any;
  recordIndex: number;
  columns: ColumnDefinition[];
  isSelected: boolean;
  metadata: RecordMetadata;
  onSelect: (index: number) => void;
  onEdit: (fieldName: string, value: any) => void;
  onApprove: () => void;
  onReject: (reason: string) => void;
}
```

---

## Configuration & Settings

### User Preferences

```typescript
interface TablePreferences {
  // Column visibility
  hiddenColumns: string[];

  // Column widths (override auto-sizing)
  columnWidths: Record<string, number>;

  // Frozen columns (sticky horizontal)
  frozenColumns: string[];

  // Default sort
  defaultSort: { column: string; direction: 'asc' | 'desc' } | null;

  // Approval mode
  approvalMode: 'file-level' | 'record-level';

  // Performance
  enableVirtualScrolling: boolean;
  rowsPerPage: number;
}

// Store in localStorage per schema type
const key = `table-prefs-${schemaName}`;
localStorage.setItem(key, JSON.stringify(preferences));
```

### Schema-Level Configuration

```python
# In document_schemas.py, add UI hints
class ITAudit_response(BaseModel):
    item: List[Issue]
    model_config = ConfigDict(
        extra="forbid",
        ui_hints={
            "approval_mode": "record-level",  # Force per-record approval
            "enable_bulk_actions": True,
            "highlight_fields": ["description", "risk_statement"],
            "frozen_columns": ["reference", "title"],
            "default_sort": ("reference", "asc"),
        }
    )
```

---

## Accessibility Considerations

### Keyboard Navigation

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next cell |
| `Shift+Tab` | Move to previous cell |
| `Enter` | Start editing current cell |
| `Ctrl/Cmd+Enter` | Approve current record, move to next |
| `Esc` | Cancel editing / Clear selection |
| `↑↓` | Navigate rows |
| `←→` | Navigate columns (when not editing) |
| `Space` | Toggle row selection |
| `Ctrl/Cmd+A` | Select all rows |
| `Ctrl/Cmd+F` | Focus global search |
| `Ctrl/Cmd+S` | Save changes |

### Screen Reader Support

```tsx
// ARIA labels for table structure
<table role="grid" aria-label="Record review table">
  <thead>
    <tr role="row">
      <th role="columnheader" aria-sort={sortDirection}>
        Agency
      </th>
    </tr>
  </thead>
  <tbody>
    <tr role="row" aria-selected={isSelected}>
      <td role="gridcell" aria-readonly={!isEditing}>
        {value}
      </td>
    </tr>
  </tbody>
</table>

// Status announcements
<div role="status" aria-live="polite" className="sr-only">
  {statusMessage} {/* e.g., "Record 3 approved" */}
</div>

// Error announcements
<div role="alert" aria-live="assertive" className="sr-only">
  {errorMessage} {/* e.g., "Validation failed: Agency required" */}
</div>
```

### Focus Management

- Focus trap in modals (nested data editor)
- Focus visible indicators (outline on keyboard focus)
- Skip to content links
- Focus returns to trigger after modal close

---

## Testing Strategy

### Unit Tests

```typescript
// DataPanel.test.tsx
describe('Enhanced TableView', () => {
  it('renders all records', () => {
    const file = mockFileWithMultipleRecords(10);
    render(<TableView file={file} />);
    expect(screen.getAllByRole('row')).toHaveLength(11); // 10 + header
  });

  it('handles row selection', () => {
    const onSelect = jest.fn();
    render(<TableView file={file} onRecordSelect={onSelect} />);

    const checkbox = screen.getAllByRole('checkbox')[1]; // First row
    fireEvent.click(checkbox);
    expect(onSelect).toHaveBeenCalledWith([0]);
  });

  it('validates fields on blur', async () => {
    render(<TableView file={file} />);
    const input = screen.getByDisplayValue('Original Value');

    fireEvent.change(input, { target: { value: '' } }); // Required field
    fireEvent.blur(input);

    await waitFor(() => {
      expect(screen.getByText(/required/i)).toBeInTheDocument();
    });
  });

  it('approves valid records in bulk', async () => {
    const onBulkApprove = jest.fn();
    render(<TableView file={file} onBulkApprove={onBulkApprove} />);

    // Select valid records
    fireEvent.click(screen.getByLabelText('Select record 1'));
    fireEvent.click(screen.getByLabelText('Select record 2'));

    // Click bulk approve
    fireEvent.click(screen.getByText('Approve Selected'));

    expect(onBulkApprove).toHaveBeenCalledWith([0, 1]);
  });
});
```

### Integration Tests

```typescript
// ReviewWorkspace.integration.test.tsx
describe('Review Workspace Integration', () => {
  it('completes full review workflow', async () => {
    // 1. Load session with 5 records
    const { session } = await loadMockSession();
    render(<ReviewWorkspace session={session} />);

    // 2. Edit a field
    const input = screen.getAllByRole('textbox')[0];
    fireEvent.change(input, { target: { value: 'Updated Value' } });

    // 3. Save changes
    fireEvent.click(screen.getByText('Save'));
    await waitFor(() => {
      expect(screen.getByText('Changes saved')).toBeInTheDocument();
    });

    // 4. Approve record
    fireEvent.click(screen.getByText('Approve'));
    await waitFor(() => {
      expect(screen.getByText(/approved/i)).toBeInTheDocument();
    });

    // 5. Navigate to next record
    fireEvent.click(screen.getByLabelText('Next record'));

    // 6. Verify state persists
    expect(mockAPI.updateFileFields).toHaveBeenCalled();
    expect(mockAPI.approveRecord).toHaveBeenCalled();
  });
});
```

### Performance Tests

```typescript
describe('Performance', () => {
  it('renders 100 records in under 1 second', async () => {
    const file = mockFileWithMultipleRecords(100);
    const startTime = performance.now();

    render(<TableView file={file} />);

    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(1000);
  });

  it('handles search filtering quickly', async () => {
    const file = mockFileWithMultipleRecords(50);
    render(<TableView file={file} />);

    const searchInput = screen.getByPlaceholderText(/search/i);
    const startTime = performance.now();

    fireEvent.change(searchInput, { target: { value: 'test query' } });

    await waitFor(() => {
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(100); // <100ms response
    });
  });
});
```

---

## Migration Strategy

### Backwards Compatibility

**Goal**: Existing workflows continue working without changes

**Strategy**
1. **Feature Flags**: Enable new features opt-in
   ```typescript
   const ENABLE_RECORD_LEVEL_APPROVAL = false; // Default off
   const ENABLE_BULK_ACTIONS = false;
   ```

2. **Gradual Rollout**
   - Phase 1: Add features, keep disabled
   - Phase 2: Enable for internal testing
   - Phase 3: Enable for complex schemas only
   - Phase 4: Enable for all schemas (user can opt-out)

3. **Schema-Specific Defaults**
   ```typescript
   const getDefaultTableConfig = (schemaName: string) => {
     const complexSchemas = ['it_audit', 'lease_agreement', 'loan_agreement'];

     return {
       enableRecordApproval: complexSchemas.includes(schemaName),
       enableBulkActions: complexSchemas.includes(schemaName),
       enableVirtualScrolling: true,
     };
   };
   ```

### Data Migration

**No database migration needed** - all enhancements work with existing data structures.

**Optional Migration**: Add per-record metadata to existing sessions
```python
# Migration script
def add_record_metadata_to_sessions():
    """Add empty record_metadata to existing review sessions"""
    for session_file in REVIEW_SESSIONS_DIR.glob("*/session.json"):
        with open(session_file, 'r') as f:
            session = json.load(f)

        for file in session['files']:
            if isinstance(file['extracted_data'], list):
                # Add metadata for each record
                file['record_metadata'] = [
                    {
                        'record_index': idx,
                        'status': 'not_reviewed',
                        'validation_errors': []
                    }
                    for idx in range(len(file['extracted_data']))
                ]

        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
```

---

## Success Metrics

### User Experience Metrics

1. **Time to Review**: Average time to review & approve one record
   - **Target**: <30 seconds per record for simple schemas
   - **Target**: <2 minutes per record for complex schemas

2. **Error Rate**: Validation errors caught before submission
   - **Target**: >95% of errors caught in review phase

3. **Approval Efficiency**: Records approved per hour
   - **Baseline**: Current file-level workflow
   - **Goal**: 20% improvement with per-record workflow

4. **User Satisfaction**: Survey score after 2 weeks
   - **Questions**: Ease of use, efficiency, clarity
   - **Target**: >4.0/5.0 average rating

### Technical Metrics

1. **Performance**: Initial render time for 50 records
   - **Target**: <500ms

2. **Responsiveness**: Search/filter response time
   - **Target**: <100ms

3. **Memory Usage**: Browser memory with 100 records
   - **Target**: <50MB increase from baseline

4. **Crash Rate**: Client-side errors during review
   - **Target**: <0.1% of sessions

---

## Future Enhancements (Out of Scope)

### Advanced Features for v2

1. **AI-Powered Validation**
   - LLM checks for logical consistency
   - Flags suspicious values
   - Suggests corrections

2. **Collaborative Review**
   - Multi-user review sessions
   - Real-time collaboration (WebSockets)
   - Assignment of records to reviewers

3. **Custom Workflows**
   - Define review stages (1st review, 2nd review, final approval)
   - Configurable approval chains
   - Conditional routing based on field values

4. **Advanced Analytics**
   - Review time heatmaps
   - Error pattern analysis
   - Reviewer performance metrics

5. **Export Templates**
   - Custom Excel templates per schema
   - Auto-generate audit reports
   - Integration with external systems

6. **Undo/Redo History**
   - Full edit history with timestamps
   - Visual diff of changes
   - Revert to any previous state

---

## Conclusion

This design maintains the **table-based interface** while adding powerful features to handle complex multi-record scenarios efficiently. Key principles:

1. **Progressive Enhancement**: Simple schemas stay simple, complex ones get powerful tools
2. **User Control**: Users can override auto-selections and customize views
3. **Performance First**: Virtual scrolling and optimization for large datasets
4. **Accessibility**: Full keyboard navigation and screen reader support
5. **Backwards Compatible**: Existing workflows continue working without changes

**Implementation Timeline**: 4 weeks for full feature set, with incremental rollout per phase.

**Next Steps**:
1. Review this design with stakeholders
2. Gather feedback from end users (audit teams)
3. Create detailed mockups for complex scenarios
4. Begin Phase 1 implementation

---

**Document Owner**: Claude Code
**Last Updated**: October 18, 2025
**Status**: Awaiting Approval
**Related Docs**:
- `.claude/docs/interactive-document-review-feature.md` (Original review feature spec)
- `.claude/docs/color_guideline.md` (Brand colors and styling)
