# Multi-Record Review Workspace - UI/UX Design Guide

**Version:** 1.0
**Date:** 2025-10-18
**Status:** Implementation Ready

---

## Executive Summary

This document defines the UI/UX design for InfoTransform's document review workspace when handling multiple complex records per file. The solution uses an **adaptive multi-view system** that automatically selects the optimal presentation based on schema complexity.

### Key Innovations

1. **Adaptive Complexity Detection**: Automatically analyzes schemas to choose the best UI pattern
2. **Progressive Disclosure**: Simple schemas stay simple, complex schemas get rich tooling
3. **Hybrid Approval System**: Supports both per-file and per-record approval workflows
4. **Graceful Nested Data Handling**: Accordion-based editors for arrays/objects

### View Modes

| Complexity | Default View | Use Case | Schema Example |
|------------|--------------|----------|----------------|
| **Simple** | Compact Table | 1-5 fields, no nesting | Document metadata |
| **Moderate** | Table + Drawer | 6-10 fields, 1-2 long text | Report summaries |
| **Complex** | Master-Detail | 10+ fields, nested arrays | IT audit findings |

---

## Design Philosophy

### 1. Efficiency Over Simplicity

**Target Users:** Professional reviewers (audit teams, compliance officers, data analysts)

**Key Principle:** Optimize for speed and throughput, not for minimizing cognitive load. These users:
- Review 50-200+ documents per day
- Need to quickly identify errors and anomalies
- Value information density over whitespace
- Require keyboard shortcuts and bulk operations

### 2. Context-Aware Adaptation

The UI automatically adapts based on:
- **Field count**: More fields → more structured view
- **Data types**: Long text → collapsible sections
- **Nesting depth**: Arrays/objects → dedicated editors
- **Record count**: Many records → virtual scrolling

### 3. Visual Hierarchy

```
High Priority (Always Visible):
├─ Record status indicators (approved/pending/error)
├─ Primary identifiers (ID, reference numbers)
└─ Action buttons (approve/reject)

Medium Priority (Visible but Collapsed):
├─ Long text fields (expand on focus)
├─ Nested arrays (show count, expand to edit)
└─ Optional fields

Low Priority (Hidden Until Needed):
├─ Field descriptions/tooltips
├─ Validation rules
└─ Historical changes
```

---

## Component Architecture

### File Structure

```
frontend/components/review/
├── DataPanel.tsx                    # Main router (MODIFY)
├── CompactTableView.tsx             # Simple schemas (EXTRACT from DataPanel)
├── TableWithDrawerView.tsx          # Moderate complexity (NEW)
├── MasterDetailView.tsx             # Complex schemas (NEW)
├── RecordNavigator.tsx              # Record list sidebar (CREATED)
├── RecordDetailView.tsx             # Form-based detail editor (NEW)
├── NestedFieldRenderer.tsx          # Array/object editor (NEW)
└── ApprovalControls.tsx             # Approval buttons (NEW)

frontend/lib/
├── schema-analyzer.ts               # Complexity detection (CREATED)
└── store.ts                         # Add record-level state (MODIFY)
```

---

## Implementation Guide

### Phase 1: Schema Analyzer (COMPLETED ✓)

**File:** `/frontend/lib/schema-analyzer.ts`

The schema analyzer automatically detects:
- Field types (short/medium/long text, enum, date, nested)
- Complexity level (simple/moderate/complex)
- Recommended view mode (table/table-drawer/master-detail)

**Usage:**
```typescript
import { analyzeSchema } from '@/lib/schema-analyzer';

const complexity = analyzeSchema(data, schema);
// complexity.level → 'simple' | 'moderate' | 'complex'
// complexity.recommendedView → 'table' | 'table-drawer' | 'master-detail'
// complexity.fieldMetadata → Array of field definitions
```

**Scoring Algorithm:**
- Base: 1 point per field
- Long text fields: +3 points
- Nested fields: +4 points
- Many records (>10): +2 points

**Thresholds:**
- Simple: ≤8 points
- Moderate: 9-20 points
- Complex: 21+ points

---

### Phase 2: Record Navigator (COMPLETED ✓)

**File:** `/frontend/components/review/RecordNavigator.tsx`

Left sidebar component for master-detail view.

**Features:**
- Status indicators with icons (approved ✓, pending ○, error ⚠)
- Search/filter within records
- Keyboard navigation (↑↓ arrows)
- Multi-select with checkboxes (optional)
- Auto-scroll to selected record
- Unsaved changes badges

**Props Interface:**
```typescript
interface RecordNavigatorProps {
  records: any[];
  currentRecordId: string | null;
  onRecordSelect: (recordId: string) => void;
  recordStatuses: Record<string, RecordStatus>;
  identifierField: string;        // e.g., "reference"
  titleField?: string;            // e.g., "title"
  showCheckboxes?: boolean;
  selectedRecordIds?: Set<string>;
  onRecordToggle?: (recordId: string) => void;
}
```

**Usage Example:**
```typescript
<RecordNavigator
  records={fileData.item}
  currentRecordId={currentRecordId}
  onRecordSelect={setCurrentRecordId}
  recordStatuses={recordStatuses}
  identifierField="reference"
  titleField="title"
  showCheckboxes={true}
/>
```

---

### Phase 3: Master-Detail View (TODO)

**File:** `/frontend/components/review/MasterDetailView.tsx`

Combines RecordNavigator + RecordDetailView with resizable split panel.

**Layout:**
```tsx
<ResizablePanelGroup direction="horizontal">
  <ResizablePanel defaultSize={30} minSize={20} maxSize={40}>
    <RecordNavigator {...navigatorProps} />
  </ResizablePanel>

  <ResizableHandle />

  <ResizablePanel defaultSize={70}>
    <RecordDetailView
      record={currentRecord}
      schema={complexity.fieldMetadata}
      onFieldUpdate={handleFieldUpdate}
    />
  </ResizablePanel>
</ResizablePanelGroup>
```

**Install Required Component:**
```bash
npx shadcn-ui@latest add resizable
```

---

### Phase 4: Record Detail View (TODO)

**File:** `/frontend/components/review/RecordDetailView.tsx`

Form-based editor with automatic layout based on field types.

**Field Rendering Rules:**

| Field Type | Component | Layout |
|------------|-----------|--------|
| short | `<Input />` | Single line, max-width: 300px |
| medium | `<Input />` | Single line, max-width: 500px |
| long | `<Textarea autoResize />` | Full width, min-height: 100px |
| enum (2-4 options) | `<RadioGroup />` | Horizontal inline |
| enum (5+ options) | `<Select />` | Dropdown |
| date | `<DatePicker />` | Calendar picker |
| boolean | `<Checkbox />` | Single checkbox |
| nested (array) | `<Accordion />` | Collapsible section |
| nested (object) | `<Card />` | Grouped fields |

**Grouping Strategy:**
1. Header fields (IDs, references) → Horizontal row at top
2. Title fields → Full width
3. Short/medium text → Two-column grid
4. Long text → Full width
5. Enums/dates → Inline or grid
6. Nested data → Collapsible sections at bottom

**Example Layout:**
```tsx
<div className="space-y-6 p-6">
  {/* Header row */}
  <div className="grid grid-cols-3 gap-4">
    <FormField name="reference" />
    <FormField name="category" />
    <FormField name="agency" />
  </div>

  {/* Title */}
  <FormField name="title" fullWidth />

  {/* Two-column grid */}
  <div className="grid grid-cols-2 gap-4">
    <FormField name="root_cause" />
    <FormField name="root_cause_category" />
  </div>

  {/* Long text (full width) */}
  <FormField name="description" fullWidth />
  <FormField name="risk_statement" fullWidth />

  {/* Nested array */}
  <NestedFieldRenderer
    fieldName="recommendations"
    value={record.recommendations}
    onChange={updateRecommendations}
  />
</div>
```

---

### Phase 5: Nested Field Renderer (TODO)

**File:** `/frontend/components/review/NestedFieldRenderer.tsx`

Handles arrays and objects with add/remove functionality.

**Array Rendering (Example: Recommendations):**
```tsx
<Accordion type="single" collapsible>
  <AccordionItem value="recommendations">
    <AccordionTrigger>
      Recommendations
      <Badge variant="outline" className="ml-2">
        {recommendations.length} items
      </Badge>
    </AccordionTrigger>

    <AccordionContent>
      <div className="space-y-3">
        {recommendations.map((item, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-sm">
                Recommendation {index + 1}
              </CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeItem(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>

            <CardContent className="space-y-3">
              <div>
                <Label>Description</Label>
                <Textarea
                  value={item.description}
                  onChange={(e) => updateNestedField(index, 'description', e.target.value)}
                />
              </div>

              <div>
                <Label>Priority</Label>
                <Select
                  value={item.priority}
                  onValueChange={(val) => updateNestedField(index, 'priority', val)}
                >
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </Select>
              </div>
            </CardContent>
          </Card>
        ))}

        <Button
          variant="outline"
          onClick={addRecommendation}
          className="w-full"
        >
          + Add Recommendation
        </Button>
      </div>
    </AccordionContent>
  </AccordionItem>
</Accordion>
```

**Install Required Components:**
```bash
npx shadcn-ui@latest add accordion
npx shadcn-ui@latest add card
```

---

### Phase 6: Table with Drawer (TODO)

**File:** `/frontend/components/review/TableWithDrawerView.tsx`

For moderate complexity schemas (6-10 fields).

**Layout:**
- Main area: Table showing 3-5 key columns
- Row actions: Menu button [⋮] in each row
- Drawer: Slides in from right with full record form

**Example:**
```tsx
<div className="flex flex-col h-full">
  {/* Table */}
  <ScrollArea className="flex-1">
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>
            <Checkbox /> {/* Select all */}
          </TableHead>
          <TableHead>Reference</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Title</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="w-12"></TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {records.map((record, index) => (
          <TableRow key={index}>
            <TableCell>
              <Checkbox />
            </TableCell>
            <TableCell>{record.reference}</TableCell>
            <TableCell>{record.category}</TableCell>
            <TableCell>{record.title}</TableCell>
            <TableCell>
              <StatusBadge status={getStatus(record)} />
            </TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => openDrawer(record)}>
                    Edit Details
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => approveRecord(record)}>
                    Approve
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => rejectRecord(record)}>
                    Reject
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </ScrollArea>

  {/* Drawer */}
  <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
    <SheetContent side="right" className="w-[600px] sm:max-w-[600px]">
      <SheetHeader>
        <SheetTitle>
          {currentRecord?.reference}
        </SheetTitle>
      </SheetHeader>

      <ScrollArea className="h-[calc(100vh-120px)] mt-6">
        <RecordDetailView
          record={currentRecord}
          schema={complexity.fieldMetadata}
          onFieldUpdate={handleFieldUpdate}
        />
      </ScrollArea>

      <SheetFooter className="mt-4">
        <Button variant="outline" onClick={() => setDrawerOpen(false)}>
          Cancel
        </Button>
        <Button onClick={handleSave}>
          Save Changes
        </Button>
      </SheetFooter>
    </SheetContent>
  </Sheet>
</div>
```

**Install Required Components:**
```bash
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add dropdown-menu
```

---

### Phase 7: Refactor DataPanel.tsx (TODO)

**Current:** Single TableView function handles everything

**New:** Router that selects view mode based on complexity

```tsx
// DataPanel.tsx
import { analyzeSchema, isMultiRecordSchema } from '@/lib/schema-analyzer';
import { CompactTableView } from './CompactTableView';
import { TableWithDrawerView } from './TableWithDrawerView';
import { MasterDetailView } from './MasterDetailView';

export function DataPanel({ fileData, schema, onUpdate }: DataPanelProps) {
  const [viewMode, setViewMode] = useState<ViewMode | null>(null);

  // Analyze schema complexity
  const complexity = useMemo(() => {
    return analyzeSchema(fileData, schema);
  }, [fileData, schema]);

  // Auto-select view mode (user can override)
  const effectiveViewMode = viewMode || complexity.recommendedView;

  // Single record view (existing behavior)
  if (!isMultiRecordSchema(fileData)) {
    return (
      <div className="p-6">
        <h3 className="text-lg font-semibold mb-4">Extracted Data</h3>
        <SingleRecordView data={fileData} />
      </div>
    );
  }

  // Multi-record view (adaptive)
  return (
    <div className="flex flex-col h-full">
      {/* Header with view mode selector */}
      <DataPanelHeader
        recordCount={fileData.length}
        complexity={complexity}
        viewMode={effectiveViewMode}
        onViewModeChange={setViewMode}
      />

      {/* Render appropriate view */}
      {effectiveViewMode === 'table' && (
        <CompactTableView
          records={fileData}
          fieldMetadata={complexity.fieldMetadata}
          onRecordUpdate={handleRecordUpdate}
        />
      )}

      {effectiveViewMode === 'table-drawer' && (
        <TableWithDrawerView
          records={fileData}
          fieldMetadata={complexity.fieldMetadata}
          onRecordUpdate={handleRecordUpdate}
        />
      )}

      {effectiveViewMode === 'master-detail' && (
        <MasterDetailView
          records={fileData}
          fieldMetadata={complexity.fieldMetadata}
          onRecordUpdate={handleRecordUpdate}
        />
      )}
    </div>
  );
}
```

---

### Phase 8: Store Updates (TODO)

**File:** `/frontend/lib/store.ts`

Add record-level state management:

```typescript
interface ReviewStore {
  // Existing...
  files: ProcessedFile[];
  currentFileIndex: number;
  pendingEdits: Map<string, any>;
  hasUnsavedChanges: boolean;

  // NEW: Record-level state
  currentRecordId: string | null;
  recordApprovals: Record<string, {
    approved: boolean;
    rejected: boolean;
    rejectedReason?: string;
    approvedAt?: Date;
  }>;
  recordValidationErrors: Record<string, Record<string, string>>;
  viewMode: ViewMode | null;

  // NEW: Actions
  setCurrentRecord: (recordId: string | null) => void;
  approveRecord: (fileId: string, recordId: string) => void;
  rejectRecord: (fileId: string, recordId: string, reason: string) => void;
  approveAllValidRecords: (fileId: string) => void;
  updateRecordField: (fileId: string, recordId: string, fieldPath: string, value: any) => void;
  setRecordValidationError: (recordId: string, field: string, error: string) => void;
  clearRecordValidationError: (recordId: string, field: string) => void;
}

// Implementation
export const useReviewStore = create<ReviewStore>((set, get) => ({
  // ... existing state ...

  currentRecordId: null,
  recordApprovals: {},
  recordValidationErrors: {},
  viewMode: null,

  setCurrentRecord: (recordId) => set({ currentRecordId: recordId }),

  approveRecord: (fileId, recordId) => {
    const { recordApprovals } = get();
    set({
      recordApprovals: {
        ...recordApprovals,
        [recordId]: {
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
        [recordId]: {
          approved: false,
          rejected: true,
          rejectedReason: reason,
        },
      },
    });
  },

  approveAllValidRecords: (fileId) => {
    const { files, recordValidationErrors } = get();
    const file = files.find(f => f.id === fileId);
    if (!file || !file.data?.item) return;

    const newApprovals = { ...get().recordApprovals };

    file.data.item.forEach((_, index) => {
      const recordId = `${fileId}-${index}`;
      const hasErrors = recordValidationErrors[recordId] &&
        Object.keys(recordValidationErrors[recordId]).length > 0;

      if (!hasErrors) {
        newApprovals[recordId] = {
          approved: true,
          rejected: false,
          approvedAt: new Date(),
        };
      }
    });

    set({ recordApprovals: newApprovals });
  },

  updateRecordField: (fileId, recordId, fieldPath, value) => {
    // Update pendingEdits with record-specific path
    const { pendingEdits } = get();
    const editKey = `${fileId}.${recordId}.${fieldPath}`;

    const newEdits = new Map(pendingEdits);
    newEdits.set(editKey, value);

    set({
      pendingEdits: newEdits,
      hasUnsavedChanges: true,
    });
  },

  setRecordValidationError: (recordId, field, error) => {
    const { recordValidationErrors } = get();
    set({
      recordValidationErrors: {
        ...recordValidationErrors,
        [recordId]: {
          ...(recordValidationErrors[recordId] || {}),
          [field]: error,
        },
      },
    });
  },

  clearRecordValidationError: (recordId, field) => {
    const { recordValidationErrors } = get();
    const recordErrors = { ...recordValidationErrors[recordId] };
    delete recordErrors[field];

    set({
      recordValidationErrors: {
        ...recordValidationErrors,
        [recordId]: recordErrors,
      },
    });
  },
}));
```

---

## Approval Workflow Design

### Three Approval Modes

#### Mode 1: Bulk Approval (Simple/Moderate)
```tsx
<Button onClick={() => approveFile(fileId)}>
  Approve All Records ({recordCount})
</Button>
```
- Single click approves entire file
- Used when records are simple or already reviewed
- Fast for high-throughput scenarios

#### Mode 2: Individual Approval (Complex)
```tsx
// In RecordNavigator
<Checkbox
  checked={recordApprovals[recordId]?.approved}
  onChange={() => toggleRecordApproval(recordId)}
/>

// In RecordDetailView footer
<div className="flex gap-2">
  <Button
    variant="destructive"
    onClick={() => rejectRecord(recordId, reason)}
  >
    Reject Record
  </Button>
  <Button
    onClick={() => approveRecord(recordId)}
    disabled={hasValidationErrors}
  >
    Approve Record
  </Button>
</div>
```
- Each record independently approved/rejected
- Required when records have complex validation
- Tracks approval timestamp and user

#### Mode 3: Smart Approval (Hybrid)
```tsx
<Popover>
  <PopoverTrigger asChild>
    <Button>
      Approve Options
      <ChevronDown className="ml-2 h-4 w-4" />
    </Button>
  </PopoverTrigger>

  <PopoverContent align="end" className="w-64">
    <div className="space-y-2">
      <Button
        variant="ghost"
        className="w-full justify-start"
        onClick={() => approveAllValidRecords(fileId)}
      >
        <Check className="mr-2 h-4 w-4" />
        Approve all valid records ({validCount})
      </Button>

      {errorCount > 0 && (
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={() => approveAllIgnoreErrors(fileId)}
        >
          <AlertTriangle className="mr-2 h-4 w-4" />
          Approve all (ignore {errorCount} errors)
        </Button>
      )}

      <Separator />

      <Button
        variant="ghost"
        className="w-full justify-start"
        onClick={() => approveSelected(fileId, selectedRecordIds)}
        disabled={selectedRecordIds.size === 0}
      >
        <CheckSquare className="mr-2 h-4 w-4" />
        Approve selected ({selectedRecordIds.size})
      </Button>
    </div>
  </PopoverContent>
</Popover>
```

---

## Visual Design Specifications

### Color Palette

**Status Colors:**
```css
/* Approved */
.status-approved { background: #f0fdf4; color: #166534; border: #bbf7d0; }

/* Pending */
.status-pending { background: #f9fafb; color: #6b7280; border: #e5e7eb; }

/* Error/Warning */
.status-error { background: #fffbeb; color: #92400e; border: #fde68a; }

/* Rejected */
.status-rejected { background: #fef2f2; color: #991b1b; border: #fecaca; }

/* Unsaved Changes */
.status-edited { background: #fef3c7; color: #92400e; border: #fde68a; }
```

**Interactive States:**
```css
/* Selected record (in navigator) */
.record-selected {
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
}

/* Hover states */
.record-item:hover { background: #f9fafb; }
.record-selected:hover { background: #dbeafe; }

/* Focus states (accessibility) */
.record-item:focus {
  outline: 2px solid #3b82f6;
  outline-offset: -2px;
}
```

### Typography

```css
/* Record identifier (reference/ID) */
.record-identifier {
  font-size: 0.875rem;    /* 14px */
  font-weight: 500;
  line-height: 1.25rem;
}

/* Record title/subtitle */
.record-title {
  font-size: 0.75rem;     /* 12px */
  font-weight: 400;
  line-height: 1rem;
  color: #6b7280;
}

/* Form labels */
.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

/* Field values */
.field-value {
  font-size: 0.875rem;
  line-height: 1.5rem;
}
```

### Spacing

```css
/* Record list items */
.record-item { padding: 0.75rem; gap: 0.75rem; }

/* Form fields */
.form-field { margin-bottom: 1.5rem; }

/* Section spacing */
.form-section { margin-bottom: 2rem; }

/* Nested field padding */
.nested-field { padding-left: 1.5rem; }
```

### Icons

All icons from `lucide-react` at 16px (h-4 w-4):
- Check (approved)
- X (rejected)
- Clock (pending)
- AlertCircle (error)
- Pencil (unsaved changes)
- ChevronDown (expand)
- MoreVertical (actions menu)

---

## Keyboard Shortcuts

| Shortcut | Action | Context |
|----------|--------|---------|
| `↑` / `↓` | Navigate records | Record list focused |
| `Enter` | Select record | Record list |
| `Space` | Toggle checkbox | Record list / form |
| `Ctrl/Cmd + S` | Save changes | Any view |
| `Ctrl/Cmd + A` | Approve record | Detail view |
| `Ctrl/Cmd + R` | Reject record | Detail view |
| `Tab` | Next field | Form |
| `Shift + Tab` | Previous field | Form |
| `Esc` | Close drawer / Clear selection | Any |
| `Ctrl/Cmd + F` | Focus search | Record list |

---

## Accessibility Checklist

### WCAG 2.1 AA Compliance

- [ ] All interactive elements keyboard accessible
- [ ] Visible focus indicators (2px outline)
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] All images have alt text
- [ ] Form inputs have associated labels
- [ ] Error messages linked via aria-describedby
- [ ] Status updates announced to screen readers (aria-live)
- [ ] Semantic HTML (proper heading hierarchy)
- [ ] Skip links for long forms
- [ ] No keyboard traps

### Testing Requirements

1. **Keyboard Navigation Test**
   - Tab through all interactive elements
   - Verify focus order is logical
   - Test all shortcuts

2. **Screen Reader Test**
   - NVDA (Windows) or VoiceOver (macOS)
   - Verify all content is announced
   - Test form validation messages

3. **Color Contrast Test**
   - Use WebAIM Contrast Checker
   - Verify all text meets 4.5:1 ratio

---

## Performance Optimizations

### Virtual Scrolling (50+ Records)

```bash
npm install @tanstack/react-virtual
```

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function RecordNavigator({ records }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: records.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 60,
    overscan: 5,
  });

  return (
    <ScrollArea ref={parentRef} className="h-full">
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <RecordItem
            key={virtualRow.key}
            record={records[virtualRow.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
```

### Memoization Strategy

```tsx
// Memoize expensive computations
const complexity = useMemo(
  () => analyzeSchema(data, schema),
  [data, schema]
);

// Memoize record components
const RecordItem = memo(({ record, onClick }) => {
  return <div onClick={() => onClick(record.id)}>...</div>;
}, (prev, next) => {
  // Custom comparison for better performance
  return prev.record.id === next.record.id &&
         prev.isSelected === next.isSelected &&
         prev.status === next.status;
});

// Memoize callbacks
const handleRecordSelect = useCallback(
  (recordId: string) => {
    setCurrentRecordId(recordId);
  },
  []
);
```

### Debounced Search

```tsx
import { useDebouncedCallback } from 'use-debounce';

const debouncedSearch = useDebouncedCallback(
  (query: string) => {
    // Expensive search operation
    setFilteredRecords(filterRecords(records, query));
  },
  300 // 300ms delay
);
```

---

## Testing Strategy

### Unit Tests

```typescript
// schema-analyzer.test.ts
describe('analyzeSchema', () => {
  it('should detect simple schema', () => {
    const data = { name: 'John', email: 'john@example.com' };
    const result = analyzeSchema(data);
    expect(result.level).toBe('simple');
    expect(result.recommendedView).toBe('table');
  });

  it('should detect complex schema with nested data', () => {
    const data = {
      title: 'Issue',
      description: 'Long description...',
      recommendations: [
        { text: 'Fix this', priority: 'high' }
      ]
    };
    const result = analyzeSchema(data);
    expect(result.level).toBe('complex');
    expect(result.nestedFields).toBe(1);
  });
});
```

### Integration Tests

```typescript
// RecordNavigator.test.tsx
describe('RecordNavigator', () => {
  it('should navigate records with arrow keys', () => {
    render(<RecordNavigator {...props} />);

    const firstRecord = screen.getByText('Record 1');
    firstRecord.focus();

    fireEvent.keyDown(firstRecord, { key: 'ArrowDown' });
    expect(props.onRecordSelect).toHaveBeenCalledWith('record-2');
  });

  it('should filter records by search query', () => {
    render(<RecordNavigator {...props} />);

    const searchInput = screen.getByPlaceholderText('Search records...');
    fireEvent.change(searchInput, { target: { value: 'ISMC-001' } });

    expect(screen.getByText('ISMC-001')).toBeInTheDocument();
    expect(screen.queryByText('ISMC-002')).not.toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)

```typescript
test('approve complex record workflow', async ({ page }) => {
  await page.goto('/review');

  // Select file with complex records
  await page.click('text=IT_Audit.pdf');

  // Wait for master-detail view to load
  await page.waitForSelector('[data-testid="record-navigator"]');

  // Select first record
  await page.click('text=ISMC-2024-001');

  // Edit a field
  await page.fill('[name="root_cause"]', 'Updated root cause');

  // Add recommendation
  await page.click('text=Add Recommendation');
  await page.fill('[name="recommendations.0.description"]', 'Implement MFA');

  // Approve record
  await page.click('text=Approve Record');

  // Verify status updated
  await expect(page.locator('text=ISMC-2024-001')).toContainText('Approved');
});
```

---

## Migration Strategy

### Phase 1: Feature Flag (Week 1)

Add feature flag to enable new UI gradually:

```typescript
// lib/feature-flags.ts
export const useFeatureFlag = (flag: string) => {
  const flags = {
    'new-review-ui': true,  // Enable for testing
  };
  return flags[flag] || false;
};

// DataPanel.tsx
const useNewReviewUI = useFeatureFlag('new-review-ui');

return useNewReviewUI ? (
  <AdaptiveDataPanel />
) : (
  <LegacyTableView />
);
```

### Phase 2: Auto-Detect (Week 2-3)

Automatically use new UI for complex schemas:

```typescript
const shouldUseNewUI = complexity.level !== 'simple';
```

### Phase 3: User Preference (Week 4)

Allow users to manually switch:

```typescript
const [userPreference, setUserPreference] = useLocalStorage('review-ui-mode', 'auto');

const effectiveMode = userPreference === 'auto'
  ? complexity.recommendedView
  : userPreference;
```

### Phase 4: Full Migration (Week 5)

Remove legacy code, make new UI default.

---

## Dependencies to Install

```bash
# shadcn/ui components
npx shadcn-ui@latest add form
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add radio-group
npx shadcn-ui@latest add accordion
npx shadcn-ui@latest add card
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add resizable
npx shadcn-ui@latest add label
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add dropdown-menu

# Additional libraries
npm install @tanstack/react-virtual  # Virtual scrolling
npm install use-debounce              # Debounced inputs
```

---

## Success Metrics

### User Experience
- [ ] Time to review complex record < 30 seconds
- [ ] Approval rate for valid records > 95%
- [ ] User error rate < 2%
- [ ] Keyboard navigation success rate > 90%

### Performance
- [ ] Initial render < 500ms for 50 records
- [ ] Scroll FPS ≥ 60 with virtual scrolling
- [ ] Search/filter response < 100ms
- [ ] Field update latency < 50ms

### Accessibility
- [ ] WCAG 2.1 AA compliance: 100%
- [ ] Keyboard navigation: 100% functional
- [ ] Screen reader compatibility: NVDA + VoiceOver
- [ ] Color contrast: All elements ≥ 4.5:1

---

## Next Steps

### Immediate Tasks (Week 1)
1. ✅ Create schema analyzer utility
2. ✅ Build RecordNavigator component
3. [ ] Install required shadcn/ui components
4. [ ] Create RecordDetailView skeleton
5. [ ] Update Zustand store with record-level state

### Short-term (Week 2-3)
6. [ ] Build MasterDetailView integration
7. [ ] Implement NestedFieldRenderer for arrays
8. [ ] Create TableWithDrawerView for moderate complexity
9. [ ] Add approval controls with validation
10. [ ] Refactor DataPanel.tsx as router

### Medium-term (Week 4-5)
11. [ ] Add keyboard shortcuts
12. [ ] Implement virtual scrolling for large lists
13. [ ] Add accessibility features (ARIA, focus management)
14. [ ] Write unit and integration tests
15. [ ] User testing and feedback iteration

---

## FAQ

**Q: What happens to existing simple schemas?**
A: They continue using the compact table view (no changes). The system automatically detects complexity and only uses new UI for moderate/complex schemas.

**Q: Can users manually switch view modes?**
A: Yes, the header will include a view mode toggle for user preference.

**Q: How are nested arrays handled?**
A: Accordion-based collapsible sections with add/remove buttons. Each item is a Card with full form fields.

**Q: What about very large record counts (500+)?**
A: Virtual scrolling automatically kicks in for lists > 50 records, ensuring smooth performance.

**Q: How does approval work with validation errors?**
A: Records with validation errors are highlighted in red with [!] icon. "Approve All" skips error records by default. Users can approve individually or fix errors first.

**Q: Is this backwards compatible?**
A: Yes, completely. Simple schemas use existing code path. New UI only activates for complex schemas or when explicitly enabled.

---

## Conclusion

This design provides a scalable, adaptive solution for reviewing multi-record documents with complex schemas. The master-detail pattern for complex records, combined with simpler views for basic schemas, ensures optimal UX across all complexity levels.

Key benefits:
- **Automatic Adaptation**: No manual configuration needed
- **Progressive Disclosure**: Complex features only appear when needed
- **Performance Optimized**: Virtual scrolling, memoization, debouncing
- **Accessibility First**: Full WCAG 2.1 AA compliance
- **Backwards Compatible**: Existing workflows unchanged

Implementation can begin immediately with the provided schema analyzer and RecordNavigator components.
