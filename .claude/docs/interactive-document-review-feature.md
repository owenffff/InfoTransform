# Human-in-the-Loop Review Workspace

**Feature Requirement Document**  
**Version:** 2.0  
**Date:** 2025-10-07  
**Project:** InfoTransform  
**Status:** Planning Phase - Revised

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Feature Overview](#2-feature-overview)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Technical Architecture](#5-technical-architecture)
6. [Backend Requirements](#6-backend-requirements)
7. [Frontend Requirements](#7-frontend-requirements)
8. [User Interface Specifications](#8-user-interface-specifications)
9. [Data Flow & Integration](#9-data-flow--integration)
10. [Implementation Phases](#10-implementation-phases)
11. [Success Metrics](#11-success-metrics)
12. [Appendix](#12-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

This feature introduces a **Human-in-the-Loop Review Workspace** that allows users to review, validate, and edit AI-extracted data alongside the original source documents and their markdown transformations. This workspace enables human oversight and correction of automated extractions, ensuring data quality before final export.

### 1.2 Goals

- **Enhance Data Accuracy**: Enable users to verify and correct AI-extracted data by cross-referencing with source documents
- **Unified Review Interface**: Provide single workspace showing source file, markdown transformation, and extracted data
- **Efficient Batch Review**: Navigate through multiple files (including ZIP contents) with persistent file list
- **Human-in-the-Loop Workflow**: Enable manual validation and editing before data export
- **Transparent Transformation**: Show users how non-text files (images, audio) were converted to markdown before extraction

### 1.3 Key Benefits

- **Side-by-Side Comparison**: View original source and extracted data simultaneously
- **Markdown Visibility**: See intermediate markdown transformation for images/audio/Office files
- **Batch Management**: File list sidebar shows all files including ZIP contents with status indicators
- **Quick Corrections**: Edit data directly while viewing the source context
- **Audit Trail**: Track which fields have been reviewed and approved
- **Browser-Adaptive**: Resizable panels adapt to browser window size

---

## 2. Feature Overview

### 2.1 Core Capabilities

The Human-in-the-Loop Review Workspace introduces a dedicated review interface accessed after the initial document processing phase. Users can:

1. **Browse all files** in a persistent sidebar list (including individual files from ZIP archives)
2. **Select any file** to view its source content, markdown transformation, and extracted data
3. **View multi-format sources** (PDF, image, Office, audio) with their markdown conversions
4. **Review extracted data** in multiple view modes (Form, Table, JSON)
5. **Edit** extracted fields directly with real-time validation
6. **Approve/Reject** individual documents after verification
7. **Export** validated data with approval metadata

### 2.2 User Workflow

```
[Upload & Process] → [Results Table] → Click "Review Workspace" Button
                                                ↓
                                    [Review Workspace Loads]
                                                ↓
                        [File List Sidebar] | [Source + Data Viewer]
                                ↓                       ↓
                        Click File Name          View & Edit Data
                                ↓                       ↓
                        Shows That File          Save → Approve
                                                        ↓
                                            Repeat or Export All
```

### 2.3 Interface Layout

**Three-Panel Layout** (browser-adaptive):
- **Left Sidebar**: File list with status indicators (20% width, collapsible)
- **Center Panel**: Source document OR markdown viewer (40% width, resizable)
- **Right Panel**: Extracted data editor (40% width, resizable)

**Responsive Behavior**:
- Panels resize smoothly as browser window changes
- Draggable dividers between panels
- Minimum panel widths prevent unusable narrow views
- Sidebar auto-collapses on narrow screens (<900px)

---

## 3. User Stories

### 3.1 Primary User Stories

**US-01: Review Invoice Extraction**
> As a finance team member, I want to review extracted invoice data alongside the original invoice PDF so that I can verify the accuracy of line items, totals, and vendor information before importing into our accounting system.

**US-02: Correct OCR Errors**
> As a data entry specialist, I want to see which part of the scanned document each extracted field came from so that I can quickly identify and correct OCR errors caused by poor image quality.

**US-03: Validate Multi-Page Documents**
> As an auditor, I want to navigate through multi-page documents while keeping the extracted data visible so that I can verify information spread across multiple pages efficiently.

**US-04: Mobile Review Workflow**
> As a field agent, I want to review and approve extracted data on my tablet while on-site so that I can validate information immediately after document capture.

**US-05: Batch Approval Process**
> As a supervisor, I want to quickly navigate between multiple processed documents and approve them in sequence so that I can efficiently validate a batch of submissions.

### 3.2 Secondary User Stories

**US-06: Audio Transcript Review**
> As a transcription reviewer, I want to see the transcript alongside the audio player with timestamps so that I can verify and correct transcription errors by listening to specific sections.

**US-07: Data Export with Metadata**
> As a system administrator, I want to export validated data with approval timestamps and editor information so that I can maintain an audit trail of data processing.

**US-08: View Processing History**
> As a quality assurance analyst, I want to see which fields have been edited and when so that I can track data quality improvements over time.

---

## 4. Functional Requirements

### 4.1 File List Sidebar (Left Panel)

#### 4.1.1 File List Display

**REQ-FL-01**: Display all processed files
- Show all uploaded files in chronological order
- For ZIP archives: Expand to show all contained files with indentation/tree structure
- Display filename (or relative path for ZIP contents)
- Show file type icon (PDF, image, audio, Office)
- Visual status indicator for each file (not reviewed, in review, approved, has errors)

**REQ-FL-02**: ZIP archive handling
- ZIP files appear as expandable/collapsible groups
- Show "📦 archive.zip (5 files)" with expand arrow
- Clicking ZIP name expands to show contained files indented
- Each contained file is individually selectable and reviewable
- ZIP archive itself is not directly reviewable (only its contents)

**REQ-FL-03**: File selection
- Click file to load its content and data in main panels
- Selected file highlighted with background color
- Keyboard navigation: Up/Down arrows to navigate list
- Search/filter box at top of sidebar to find files by name

**REQ-FL-04**: Status indicators
- 🔵 Not Reviewed (default, gray)
- 🟡 In Review (currently viewing, yellow)
- ✅ Approved (green checkmark)
- ❌ Has Errors (red X)
- Each file shows edit count badge if data has been modified

**REQ-FL-05**: Sidebar controls
- Collapse/expand button to hide sidebar (gain more space)
- "Approve All" button at bottom (batch operation)
- Progress counter: "3 of 12 approved"
- Filter dropdown: Show All / Approved Only / Needs Review / Has Errors

### 4.2 Source Content Viewer (Center Panel)

#### 4.2.1 Document Rendering

**REQ-SC-01**: Support multiple document formats
- PDF: Render using PDF.js
- Images: Display JPG, PNG, GIF 
- Office Documents: Convert to PDF on backend, display as PDF
- Audio Files: Show HTML5 audio player

**REQ-SC-02**: Multi-page navigation (for PDFs)
- Page indicator (e.g., "Page 2 of 15")
- Previous/Next page buttons
- Jump-to-page input field

**REQ-SC-03**: Panel mode toggle
- "Source" tab: Shows original file (PDF viewer, image, audio player)
- "Markdown" tab: Shows markdown transformation used for extraction
- Tab switching preserved per file type (e.g., always show Markdown first for images)

**REQ-SC-04**: Markdown display
- Syntax-highlighted markdown viewer
- Read-only display (no editing)
- Copy-to-clipboard button
- Shows transformation method used (e.g., "Converted via markitdown")

#### 4.2.2 Audio Player Integration

**REQ-SC-05**: Audio playback controls
- Play/Pause button
- Progress bar with seek capability
- Volume control
- Playback speed adjustment (0.5x, 1x, 1.5x, 2x)

**REQ-SC-06**: Transcript display (in Markdown tab)
- Full transcript shown in Markdown tab
- Timestamps for each segment
- Auto-scroll transcript during playback
- Click timestamp to jump to that audio position

### 4.3 Extracted Data Panel (Right Panel)

#### 4.3.1 View Modes

**REQ-ED-01**: Three switchable view modes
- **Form View** (default): Vertical list of labeled input fields
- **Table View**: Tabular display for list-based data (e.g., line items)
- **JSON View**: Raw JSON for debugging and technical users

**REQ-ED-02**: View mode persistence
- Remember user's preferred view mode per session
- Local storage for cross-session persistence
- Per-document-type view mode preferences

#### 4.2.2 Form View

**REQ-ED-03**: Field rendering
- Label: Field name from schema (human-readable)
- Input: Editable text field, textarea, or select dropdown
- Value: Current extracted value
- Edit indicator: Visual marker when field has been edited

**REQ-ED-04**: Field types
- Text fields for strings
- Number inputs for numeric values
- Date pickers for date fields
- Dropdown selects for enumerated values
- Textarea for long text fields

**REQ-ED-05**: Field validation
- Real-time validation based on schema constraints
- Error messages for invalid inputs
- Warning indicators for suspicious values
- Required field indicators

**REQ-ED-06**: Field metadata
- Confidence score (if available from AI)
- Last edited by/timestamp
- Original vs. edited value comparison
- Field description tooltip

#### 4.2.3 Table View

**REQ-ED-07**: List data rendering
- Display items in rows (e.g., invoice line items)
- Columns: Fields from each item
- Sortable columns
- Inline editing for each cell

**REQ-ED-08**: Table operations
- Add new row
- Delete row
- Reorder rows (drag-and-drop)
- Bulk edit selected rows
- Export table to CSV

**REQ-ED-09**: Table highlighting
- Hover row to highlight all related fields in document
- Click row to lock highlight
- Visual indicator for currently selected row

#### 4.2.4 JSON View

**REQ-ED-10**: JSON display
- Syntax-highlighted JSON
- Collapsible/expandable nodes
- Copy-to-clipboard button
- Search within JSON
- Diff view (original vs. edited)

#### 4.2.5 Editing Capabilities

**REQ-ED-11**: Edit tracking
- Track all field modifications
- Show edited fields with visual indicator (e.g., yellow background)
- Undo/Redo functionality
- Comparison view (original vs. edited)

**REQ-ED-12**: Save and discard controls
- "Save Changes" button (bottom of panel)
- "Discard Changes" button (revert to original)
- Auto-save drafts to local storage
- Unsaved changes warning on navigation

**REQ-ED-13**: Validation feedback
- Real-time validation as user types
- Error summary at top of panel
- Field-level error messages
- Block approval if validation errors exist

### 4.4 Navigation & Workflow

#### 4.4.1 File Navigation

**REQ-NAV-01**: Primary navigation via sidebar
- Click any file in left sidebar to load it
- No "Previous/Next" buttons needed (file list serves this purpose)
- Keyboard shortcuts: Up/Down arrows navigate file list, Enter selects
- Current file highlighted in sidebar

**REQ-NAV-02**: Batch workspace entry
- Add "Open Review Workspace" button in Results Display component
- Button appears in header of results table (after "Download" button)
- Icon: UserCheck or ClipboardCheck to indicate human review
- Clicking creates review session and navigates to /review-workspace/[sessionId]

**REQ-NAV-03**: Navigation warnings
- Warn if unsaved changes exist before selecting different file
- Modal dialog: "Save changes?" with [Save] [Discard] [Cancel] buttons
- Option to auto-save before navigation (user preference)

#### 4.4.2 Approval Workflow

**REQ-WF-01**: Approve button
- Location: Header, right side
- Enabled only when: No validation errors, required fields completed
- Action: Mark document as approved, add approval metadata
- Visual feedback: Green checkmark, success animation

**REQ-WF-02**: Approval metadata
- Timestamp of approval
- Approver user ID/name
- Any comments or notes
- Approval status in file list

**REQ-WF-03**: Approval states
- Not Reviewed (default)
- In Review (opened in review interface)
- Approved (validation complete)
- Rejected (optional: flag for re-processing)
- Has Errors (validation failed)

**REQ-WF-04**: Batch operations
- "Approve All" for batch approval (with confirmation)
- Export only approved files
- Re-process rejected files
- Email summary of approved/rejected files

### 4.5 Browser-Adaptive Layout

**Primary Use Case**: Desktop/laptop browser interface (optimized for screens ≥900px width)

#### 4.5.1 Three-Panel Layout

**REQ-RD-01**: Panel structure
- Left Sidebar: File list (20% width, min 250px, max 400px)
- Center Panel: Source/Markdown viewer (40% width, min 300px)
- Right Panel: Data editor (40% width, min 350px)
- Draggable dividers between center and right panels

**REQ-RD-02**: Panel behaviors
- Independent scroll for each panel
- Panels resize as browser window resizes
- Minimum widths prevent unusable narrow panels
- Full-height panels (100vh minus header/footer)

#### 4.5.2 Narrow Screen Handling (<900px)

**REQ-RD-03**: Sidebar auto-collapse
- Left sidebar automatically collapses to icon-only mode
- Click hamburger icon to temporarily expand as overlay
- File list appears as slide-out panel over content

**REQ-RD-04**: Two-panel mode
- When sidebar collapsed, show center and right panels only
- Center panel: 45% width
- Right panel: 55% width
- Maintain resizable divider

---

## 5. Technical Architecture

### 5.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
├─────────────────────────────────────────────────────────────┤
│  Review Interface Container                                  │
│  ├── Document Viewer Component                               │
│  │   ├── PDF Renderer (PDF.js)                              │
│  │   ├── Image Viewer                                        │
│  │   ├── Audio Player                                        │
│  │   └── Highlight Overlay Manager                          │
│  ├── Data Panel Component                                    │
│  │   ├── Form View                                          │
│  │   ├── Table View                                         │
│  │   └── JSON View                                          │
│  ├── Navigation Component                                    │
│  └── Approval Component                                      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  Review API Endpoints                                        │
│  ├── GET /api/review/{file_id}                              │
│  ├── POST /api/review/{file_id}/update                      │
│  ├── POST /api/review/{file_id}/approve                     │
│  ├── GET /api/review/{file_id}/document                     │
│  └── POST /api/convert-to-pdf                               │
│  Coordinate Extraction Service                              │
│  ├── Vision AI for bounding box detection                   │
│  ├── PDF text position extraction                           │
│  └── Coordinate mapping service                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Data Models

#### 5.2.1 Review Session

```typescript
interface ReviewSession {
  session_id: string;
  files: FileReviewStatus[];
  created_at: string;
  updated_at: string;
  user_id?: string;
  batch_metadata?: {
    total_files: number;
    approved_count: number;
    rejected_count: number;
  };
}
```

#### 5.2.2 File Review Status

```typescript
interface FileReviewStatus {
  file_id: string;
  filename: string;
  display_name: string;
  status: 'not_reviewed' | 'in_review' | 'approved' | 'rejected' | 'has_errors';
  document_type: 'pdf' | 'image' | 'office' | 'audio';
  document_url: string;
  extracted_data: Record<string, any>;
  field_coordinates?: FieldCoordinate[];
  edits?: FieldEdit[];
  approval_metadata?: ApprovalMetadata;
  processing_metadata: {
    model_used: string;
    processing_time: number;
    confidence_scores?: Record<string, number>;
  };
}
```

#### 5.2.3 Field Coordinate

```typescript
interface FieldCoordinate {
  field_name: string;
  page: number;
  coordinates: {
    x: number;      // Left position (pixels or percentage)
    y: number;      // Top position
    width: number;  // Bounding box width
    height: number; // Bounding box height
  };
  confidence?: number;
  text_content?: string; // Original text extracted
}
```

#### 5.2.4 Field Edit

```typescript
interface FieldEdit {
  field_name: string;
  original_value: any;
  edited_value: any;
  edited_at: string;
  edited_by?: string;
  validation_status: 'valid' | 'invalid' | 'warning';
  validation_message?: string;
}
```

#### 5.2.5 Approval Metadata

```typescript
interface ApprovalMetadata {
  approved_at: string;
  approved_by: string;
  comments?: string;
  approval_status: 'approved' | 'rejected';
  rejection_reason?: string;
}
```

### 5.3 State Management

#### 5.3.1 Zustand Store Extensions

```typescript
interface ReviewStore {
  // Current review session
  currentSession: ReviewSession | null;
  currentFileIndex: number;
  
  // UI state
  activeViewMode: 'form' | 'table' | 'json';
  highlightedFields: string[];
  lockedHighlights: string[];
  panelSizes: { document: number; data: number };
  
  // Edit state
  pendingEdits: Record<string, FieldEdit>;
  hasUnsavedChanges: boolean;
  
  // Actions
  setCurrentFile: (index: number) => void;
  updateField: (fieldName: string, value: any) => void;
  saveChanges: () => Promise<void>;
  discardChanges: () => void;
  approveFile: (comments?: string) => Promise<void>;
  rejectFile: (reason: string) => Promise<void>;
  addHighlight: (fieldName: string) => void;
  removeHighlight: (fieldName: string) => void;
  lockHighlight: (fieldName: string) => void;
}
```

---

## 6. Backend Requirements

### 6.1 API Endpoints

#### 6.1.1 Get Review Data

```python
@router.get("/api/review/{session_id}")
async def get_review_session(session_id: str) -> ReviewSession:
    """
    Retrieve a review session with all files and their data.
    
    Returns:
        - session metadata
        - list of files with status
        - document URLs
        - extracted data
        - field coordinates (if available)
    """
```

#### 6.1.2 Get Single File Review

```python
@router.get("/api/review/{session_id}/files/{file_id}")
async def get_file_review(session_id: str, file_id: str) -> FileReviewStatus:
    """
    Get detailed review data for a single file.
    
    Includes:
        - Original document (as URL or base64)
        - Extracted structured data
        - Field coordinates for highlighting
        - Edit history
        - Approval status
    """
```

#### 6.1.3 Update Field Data

```python
@router.post("/api/review/{session_id}/files/{file_id}/update")
async def update_field_data(
    session_id: str, 
    file_id: str, 
    updates: List[FieldEdit]
) -> FileReviewStatus:
    """
    Update one or more fields in the extracted data.
    
    Args:
        updates: List of field edits with original/new values
    
    Returns:
        Updated file review status with validation results
    """
```

#### 6.1.4 Approve/Reject File

```python
@router.post("/api/review/{session_id}/files/{file_id}/approve")
async def approve_file(
    session_id: str,
    file_id: str,
    approval: ApprovalMetadata
) -> FileReviewStatus:
    """
    Approve or reject a file after review.
    
    Validates:
        - All required fields are filled
        - No validation errors exist
        - Edits are saved
    
    Returns:
        Updated file status with approval metadata
    """
```

#### 6.1.5 Convert Office Documents to PDF

```python
@router.post("/api/convert-to-pdf")
async def convert_office_to_pdf(file: UploadFile) -> FileResponse:
    """
    Convert DOCX, PPTX, XLSX to PDF for consistent rendering.
    
    Uses:
        - LibreOffice (headless) for conversion
        - Alternative: Microsoft Graph API
        - Fallback: Return original file with warning
    
    Returns:
        PDF file or error message
    """
```

#### 6.1.6 Get Markdown Content

```python
@router.get("/api/review/{session_id}/files/{file_id}/markdown")
async def get_markdown_content(
    session_id: str,
    file_id: str
) -> dict:
    """
    Retrieve the markdown transformation of a source file.
    
    Returns:
        - markdown_content: The converted markdown text
        - conversion_method: How it was converted (markitdown, vision, audio transcription)
        - original_length: Character count of markdown
        - was_summarized: Boolean if summarization was applied
    """
```

### 6.2 Document Serving

#### 6.2.1 Static File Serving

```python
@router.get("/api/documents/{file_id}")
async def serve_document(file_id: str) -> FileResponse:
    """
    Serve original or converted document for viewer.
    
    Returns:
        - PDF files: Direct file response
        - Images: Direct file response
        - Office: Converted PDF
        - Audio: Direct file response with MIME type
    """
```

#### 6.2.2 Thumbnail Generation

```python
@router.get("/api/documents/{file_id}/thumbnail")
async def get_document_thumbnail(
    file_id: str, 
    page: int = 1, 
    size: int = 200
) -> FileResponse:
    """
    Generate thumbnail for document page.
    
    Used for:
        - File list preview
        - Page navigation thumbnails
        - Quick preview on hover
    """
```

---

## 7. Frontend Requirements

### 7.1 Component Structure

```
/frontend/components/review/
├── ReviewInterface.tsx          # Main container
├── DocumentViewer/
│   ├── DocumentViewer.tsx      # Main viewer component
│   ├── PDFViewer.tsx           # PDF.js wrapper
│   ├── ImageViewer.tsx         # Image display with zoom
│   ├── AudioPlayer.tsx         # Audio player with transcript
│   ├── HighlightOverlay.tsx    # Highlight box renderer
│   └── ViewerControls.tsx      # Zoom, pan, page nav
├── DataPanel/
│   ├── DataPanel.tsx           # Main data panel
│   ├── FormView.tsx            # Form layout
│   ├── TableView.tsx           # Table layout
│   ├── JSONView.tsx            # JSON display
│   ├── FieldInput.tsx          # Reusable field component
│   └── EditControls.tsx        # Save/discard buttons
├── Navigation/
│   ├── FileNavigation.tsx      # Prev/next controls
│   ├── FileList.tsx            # Sidebar file list
│   └── ApprovalButton.tsx      # Approve/reject
└── shared/
    ├── ResizablePanel.tsx      # Draggable divider
    ├── FieldHighlighter.tsx    # Hover effect handler
    └── ValidationMessage.tsx   # Error/warning display
```

### 7.2 Key Components

#### 7.2.1 ReviewInterface.tsx

```typescript
export function ReviewInterface() {
  const { currentSession, currentFileIndex } = useReviewStore();
  const [panelSizes, setPanelSizes] = useState({ left: 50, right: 50 });
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  const currentFile = currentSession?.files[currentFileIndex];

  return (
    <div className="review-interface h-screen flex flex-col">
      <ReviewHeader file={currentFile} />
      
      {isDesktop ? (
        <ResizablePanels orientation="horizontal">
          <Panel defaultSize={50}>
            <DocumentViewer file={currentFile} />
          </Panel>
          <Panel defaultSize={50}>
            <DataPanel file={currentFile} />
          </Panel>
        </ResizablePanels>
      ) : (
        <ResizablePanels orientation="vertical">
          <Panel defaultSize={60}>
            <DocumentViewer file={currentFile} />
          </Panel>
          <Panel defaultSize={40}>
            <DataPanel file={currentFile} />
          </Panel>
        </ResizablePanels>
      )}
    </div>
  );
}
```

#### 7.2.2 DocumentViewer.tsx

```typescript
export function DocumentViewer({ file }: { file: FileReviewStatus }) {
  const [zoom, setZoom] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const { highlightedFields, lockedHighlights } = useReviewStore();

  const renderDocument = () => {
    switch (file.document_type) {
      case 'pdf':
        return <PDFViewer url={file.document_url} page={currentPage} zoom={zoom} />;
      case 'image':
        return <ImageViewer url={file.document_url} zoom={zoom} />;
      case 'audio':
        return <AudioPlayer url={file.document_url} transcript={file.transcript} />;
      default:
        return <div>Unsupported format</div>;
    }
  };

  return (
    <div className="document-viewer relative">
      <ViewerControls
        zoom={zoom}
        onZoomChange={setZoom}
        currentPage={currentPage}
        totalPages={file.page_count}
        onPageChange={setCurrentPage}
      />
      
      <div className="document-container relative">
        {renderDocument()}
        
        <HighlightOverlay
          coordinates={file.field_coordinates}
          highlightedFields={highlightedFields}
          lockedHighlights={lockedHighlights}
          page={currentPage}
        />
      </div>
    </div>
  );
}
```

#### 7.2.3 HighlightOverlay.tsx

```typescript
export function HighlightOverlay({
  coordinates,
  highlightedFields,
  lockedHighlights,
  page
}: HighlightOverlayProps) {
  const { addHighlight, removeHighlight } = useReviewStore();

  const activeCoordinates = coordinates?.filter(
    coord => coord.page === page && 
             (highlightedFields.includes(coord.field_name) || 
              lockedHighlights.includes(coord.field_name))
  );

  return (
    <div className="highlight-overlay absolute inset-0 pointer-events-none">
      {activeCoordinates?.map(coord => (
        <div
          key={coord.field_name}
          className={cn(
            "absolute border-3 rounded transition-all duration-150",
            "bg-yellow-200 bg-opacity-20 pointer-events-auto cursor-pointer",
            lockedHighlights.includes(coord.field_name) 
              ? "border-yellow-500 opacity-100" 
              : "border-yellow-400 opacity-70"
          )}
          style={{
            left: `${coord.coordinates.x}px`,
            top: `${coord.coordinates.y}px`,
            width: `${coord.coordinates.width}px`,
            height: `${coord.coordinates.height}px`,
          }}
          onClick={() => addHighlight(coord.field_name)}
          onMouseEnter={() => addHighlight(coord.field_name)}
          onMouseLeave={() => {
            if (!lockedHighlights.includes(coord.field_name)) {
              removeHighlight(coord.field_name);
            }
          }}
        />
      ))}
    </div>
  );
}
```

#### 7.2.4 FormView.tsx

```typescript
export function FormView({ file }: { file: FileReviewStatus }) {
  const { pendingEdits, updateField, addHighlight, removeHighlight } = useReviewStore();

  const fields = Object.entries(file.extracted_data);

  return (
    <div className="form-view p-6 space-y-4">
      {fields.map(([fieldName, value]) => {
        const edit = pendingEdits[fieldName];
        const displayValue = edit?.edited_value ?? value;

        return (
          <div
            key={fieldName}
            className={cn(
              "field-group p-3 rounded-lg transition-colors",
              edit && "bg-yellow-50 border border-yellow-200"
            )}
            onMouseEnter={() => addHighlight(fieldName)}
            onMouseLeave={() => removeHighlight(fieldName)}
          >
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {formatFieldName(fieldName)}
            </label>
            
            <FieldInput
              fieldName={fieldName}
              value={displayValue}
              onChange={(newValue) => updateField(fieldName, newValue)}
              fieldType={inferFieldType(value)}
            />
            
            {edit && (
              <div className="text-xs text-gray-500 mt-1">
                Original: {edit.original_value}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

### 7.3 Routing Integration

#### 7.3.1 New Route

```typescript
// frontend/app/review/[sessionId]/page.tsx
export default function ReviewPage({ params }: { params: { sessionId: string } }) {
  const { data: session, isLoading } = useReviewSession(params.sessionId);

  if (isLoading) return <LoadingSpinner />;
  if (!session) return <ErrorMessage />;

  return <ReviewInterface />;
}
```

#### 7.3.2 Entry Point from Results Display

```typescript
// frontend/components/ResultsDisplay.tsx
// Add "Open Review Workspace" button in header (next to Download button)

const handleOpenReviewWorkspace = async () => {
  // Create review session from current results
  const sessionId = await createReviewSession(streamingResults);
  
  // Navigate to review workspace
  router.push(`/review-workspace/${sessionId}`);
};

// In the header section, after Download button:
<button
  onClick={handleOpenReviewWorkspace}
  disabled={successfulResults.length === 0}
  className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-brand-orange-600 border border-transparent rounded-md shadow-sm hover:bg-brand-orange-700"
>
  <UserCheck className="w-4 h-4 mr-2" />
  Open Review Workspace
</button>
```

#### 7.3.3 New Route

```typescript
// frontend/app/review-workspace/[sessionId]/page.tsx
export default function ReviewWorkspacePage({ 
  params 
}: { 
  params: { sessionId: string } 
}) {
  const { data: session, isLoading } = useReviewSession(params.sessionId);

  if (isLoading) return <LoadingSpinner />;
  if (!session) return <ErrorMessage message="Review session not found" />;

  return <ReviewWorkspaceInterface session={session} />;
}
```

---

## 8. User Interface Specifications

### 8.1 Layout Specifications

#### 8.1.1 Three-Panel Desktop Layout (≥900px)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Header: InfoTransform Review Workspace | 3 of 12 approved | [Export All]  │
├──────────────┬──────────────────────────┬───────────────────────────────────┤
│ File List    │  Source/Markdown Viewer  │   Extracted Data Editor           │
│              │                          │                                   │
│ 📦 batch.zip │  [Source][Markdown]      │   [Form][Table][JSON]             │
│ ▾ (3 files)  │  ┌────────────────────┐  │   ┌─────────────────────────┐     │
│  ✅ doc1.pdf │  │                    │  │   │ invoice_id: [INV-001]   │     │
│  🟡 doc2.jpg │  │   PDF Viewer or    │  │   │ amount: [1234.56]       │     │
│  🔵 doc3.doc │  │   Markdown Display │  │   │ date: [2025-01-15]      │     │
│              │  │                    │  │   │ ...                     │     │
│ 🔵 audio.mp3 │  │   [Page 1 of 3]    │  │   │                         │     │
│              │  │                    │  │   │                         │     │
│ [≡ Collapse] │  └────────────────────┘  │   ├─────────────────────────┤     │
│              │                          │   │ [Save] [Discard]        │     │
│ [🔍 Search]  │                          │   │ [✓ Approve File]        │     │
│              │                          │   └─────────────────────────┘     │
│ 3 of 12 ✓    │                          │                                   │
└──────────────┴──────────────────────────┴───────────────────────────────────┘
   20% width        40% width                      40% width
 (collapsible)    (resizable)                   (resizable)
```

#### 8.1.2 Narrow Screen Layout (<900px)

```
┌───────────────────────────────────────────────────────────┐
│ [≡] Review Workspace | invoice.pdf | [Approve]            │
├────────────────────────────┬──────────────────────────────┤
│  Source/Markdown Viewer    │   Extracted Data Editor      │
│                            │                              │
│  [Source][Markdown]        │   [Form][Table][JSON]        │
│  ┌──────────────────────┐  │   ┌───────────────────────┐  │
│  │                      │  │   │ invoice_id: [...    ] │  │
│  │   Document Display   │  │   │ amount: [...]         │  │
│  │                      │  │   │ date: [...]           │  │
│  │                      │  │   │                       │  │
│  └──────────────────────┘  │   └───────────────────────┘  │
│                            │   [Save] [Approve]           │
└────────────────────────────┴──────────────────────────────┘
      45% width                      55% width

Note: [≡] button opens file list as slide-out overlay
```

### 8.2 Color Scheme & Visual Design

#### 8.2.1 File List Status Colors

```css
/* File status indicators */
.file-not-reviewed {
  color: #9ca3af; /* gray-400 */
  border-left: 3px solid #e5e7eb; /* gray-200 */
}

.file-in-review {
  color: #f59e0b; /* amber-500 */
  background: #fffbeb; /* amber-50 */
  border-left: 3px solid #f59e0b;
}

.file-approved {
  color: #10b981; /* green-500 */
  border-left: 3px solid #10b981;
}

.file-has-errors {
  color: #ef4444; /* red-500 */
  background: #fef2f2; /* red-50 */
  border-left: 3px solid #ef4444;
}
```

#### 8.2.2 Field States

```css
/* Edited field */
.field-edited {
  background: #fef3c7; /* yellow-100 */
  border-left: 4px solid #f59e0b; /* amber-500 */
}

/* Validation error */
.field-error {
  background: #fee2e2; /* red-100 */
  border-left: 4px solid #ef4444; /* red-500 */
}

/* Validation warning */
.field-warning {
  background: #fef3c7; /* yellow-100 */
  border-left: 4px solid #f59e0b; /* amber-500 */
}

/* Field in focus/highlighted from document */
.field-highlighted {
  background: #dbeafe; /* blue-100 */
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}
```

### 8.3 Interaction Patterns

#### 8.3.1 File Selection

**Click File in List**
- Action: Load file's source and data into center/right panels
- Unsaved changes warning if navigating away from edited file
- Visual: Highlight selected file in list with background color

**ZIP Archive Expansion**
- Click ZIP name or arrow icon to expand/collapse
- Contained files shown indented beneath ZIP
- Each file individually clickable

#### 8.3.2 View Mode Switching

**Source ↔ Markdown Toggle**
- Click tab headers to switch between Source and Markdown views
- For text-based files (PDF, Office): Both tabs available
- For images: Markdown tab shows OCR/vision extraction result
- For audio: Markdown tab shows transcript

**Data View Modes**
- Click Form/Table/JSON tabs to switch data presentation
- Preference saved per session
- Form view: Best for single-record schemas
- Table view: Best for list-based schemas (e.g., line items)
- JSON view: Raw data for debugging

#### 8.3.3 Keyboard Shortcuts

```
File Navigation:
  - Arrow Up/Down:     Navigate file list
  - Enter:             Select highlighted file
  - Ctrl+F / Cmd+F:    Focus search box in file list

Field Navigation:
  - Tab/Shift+Tab:     Navigate between fields in form
  - Arrow Up/Down:     Navigate fields (Form view)

Actions:
  - Ctrl+S / Cmd+S:    Save changes
  - Ctrl+Z / Cmd+Z:    Undo last edit
  - Ctrl+Enter:        Approve current file
  - ESC:               Cancel/close dialogs

View:
  - 1: Form view
  - 2: Table view
  - 3: JSON view
  - Ctrl+B / Cmd+B:    Toggle sidebar collapse
```

### 8.4 Accessibility

#### 8.4.1 ARIA Labels

```html
<!-- Document viewer -->
<div role="img" aria-label="Document preview">
  <div role="button" aria-label="Highlight for Invoice Number field">
  </div>
</div>

<!-- Data fields -->
<label for="invoice-number">Invoice Number</label>
<input
  id="invoice-number"
  aria-describedby="invoice-number-help"
  aria-invalid={hasError}
/>
<div id="invoice-number-help" role="alert">
  {validationMessage}
</div>
```

#### 8.4.2 Keyboard Navigation

- All interactive elements must be keyboard accessible
- Focus indicators must be visible (2px outline)
- Skip links for quick navigation
- Screen reader announcements for state changes

#### 8.4.3 Color Contrast

- All text must meet WCAG AA standards (4.5:1 ratio)
- Highlights must have sufficient contrast against backgrounds
- Error/warning colors must be distinguishable by non-color cues (icons)

---

## 9. Data Flow & Integration

### 9.1 Integration with Current Processing

#### 9.1.1 Entry Point from Results Display

**User Flow:**
1. User completes batch processing (current flow)
2. Results displayed in `ResultsDisplay.tsx`
3. New "Review" button appears next to each successful result
4. Clicking "Review" creates a review session and navigates to review interface

**Implementation:**

```typescript
// ResultsDisplay.tsx - Add review button

const handleReviewClick = async (result: FileResult) => {
  // Create review session
  const sessionId = await createReviewSession([result]);
  
  // Navigate to review interface
  router.push(`/review/${sessionId}`);
};

// Add button to each result row
<button onClick={() => handleReviewClick(result)}>
  <Eye className="w-4 h-4" />
  Review & Validate
</button>
```

#### 9.1.2 Session Creation

```typescript
// lib/api.ts

export async function createReviewSession(results: FileResult[]): Promise<string> {
  const response = await fetch('/api/review/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      files: results.map(r => ({
        filename: r.filename,
        extracted_data: r.structured_data,
        document_url: `/api/documents/${r.file_id}`,
        processing_metadata: {
          model_used: r.model_name,
          processing_time: r.processing_time
        }
      }))
    })
  });
  
  const session = await response.json();
  return session.session_id;
}
```

### 9.2 Coordinate Extraction Pipeline

#### 9.2.1 Trigger Coordinate Extraction

**Option 1: During initial processing** (adds latency)
```python
# In structured_analyzer_agent.py, after successful extraction
async def analyze_content_stream(...):
    # ... existing code ...
    
    if result['success']:
        # Extract coordinates in background
        asyncio.create_task(
            extract_coordinates_async(file_path, result['structured_data'])
        )
```

**Option 2: On-demand during review** (preferred)
```python
# When review interface loads, request coordinates
@router.get("/api/review/{session_id}/files/{file_id}")
async def get_file_review(...):
    # ... get file data ...
    
    # Check if coordinates already extracted
    if not file.field_coordinates:
        # Extract coordinates asynchronously
        coordinates = await extract_field_coordinates(
            file.document_path,
            file.extracted_data
        )
        # Cache for future requests
        file.field_coordinates = coordinates
        await save_file_review(file)
    
    return file
```

#### 9.2.2 Coordinate Caching

```python
# Store coordinates in database or file system
class FileReview(BaseModel):
    file_id: str
    extracted_data: Dict
    field_coordinates: Optional[List[FieldCoordinate]] = None
    coordinates_extracted_at: Optional[datetime] = None

# Cache strategy
async def get_or_extract_coordinates(
    file_path: str,
    extracted_data: Dict,
    file_id: str
) -> List[FieldCoordinate]:
    # Check cache
    cached = await cache.get(f"coordinates:{file_id}")
    if cached:
        return cached
    
    # Extract coordinates
    coordinates = await extract_field_coordinates(file_path, extracted_data)
    
    # Cache for 24 hours
    await cache.set(f"coordinates:{file_id}", coordinates, ttl=86400)
    
    return coordinates
```

### 9.3 Real-time Updates

#### 9.3.1 Edit Persistence

**Local State (Immediate):**
- Edits stored in Zustand store immediately
- Auto-save to localStorage every 30 seconds
- Survives browser refresh

**Server Sync (On Save):**
- Batch edits sent to server when user clicks "Save"
- Server validates and persists edits
- Returns updated validation status

```typescript
// Auto-save to localStorage
useEffect(() => {
  const interval = setInterval(() => {
    if (hasUnsavedChanges) {
      localStorage.setItem(
        `review-drafts-${sessionId}-${fileId}`,
        JSON.stringify(pendingEdits)
      );
    }
  }, 30000); // Every 30 seconds

  return () => clearInterval(interval);
}, [hasUnsavedChanges, pendingEdits, sessionId, fileId]);

// Save to server
const saveChanges = async () => {
  const response = await fetch(
    `/api/review/${sessionId}/files/${fileId}/update`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        edits: Object.values(pendingEdits)
      })
    }
  );
  
  if (response.ok) {
    setHasUnsavedChanges(false);
    localStorage.removeItem(`review-drafts-${sessionId}-${fileId}`);
  }
};
```

### 9.4 Export Integration

#### 9.4.1 Enhanced Export with Approval Data

```typescript
// Extend existing downloadResults function
export async function downloadResultsWithApprovals(
  sessionId: string,
  format: 'excel' | 'csv'
): Promise<void> {
  const response = await fetch(
    `/api/review/${sessionId}/export?format=${format}`,
    { method: 'POST' }
  );
  
  // ... download file ...
}
```

**Backend Export Endpoint:**
```python
@router.post("/api/review/{session_id}/export")
async def export_review_session(
    session_id: str,
    format: str = 'excel',
    include_only_approved: bool = True
) -> FileResponse:
    """
    Export review session data with approval metadata.
    
    Includes:
        - Original extracted data
        - Edited values
        - Approval status and timestamps
        - Editor information
        - Validation status
    """
    session = await get_review_session(session_id)
    
    # Filter files
    files_to_export = [
        f for f in session.files
        if not include_only_approved or f.status == 'approved'
    ]
    
    # Build export data
    export_data = []
    for file in files_to_export:
        row = {
            'filename': file.filename,
            **file.extracted_data,  # Original/edited data
            '_approval_status': file.approval_metadata.approval_status,
            '_approved_by': file.approval_metadata.approved_by,
            '_approved_at': file.approval_metadata.approved_at,
            '_has_edits': len(file.edits or []) > 0,
            '_edit_count': len(file.edits or [])
        }
        export_data.append(row)
    
    # Generate Excel/CSV
    if format == 'excel':
        return generate_excel(export_data)
    else:
        return generate_csv(export_data)
```

---

## 10. Implementation Phases

### 10.1 Phase 1: Foundation (Weeks 1-2)

**Goal:** Basic review interface with document viewing and data display

**Tasks:**
1. Create review route and page structure
2. Implement DocumentViewer component (PDF and image support)
3. Implement DataPanel with Form View
4. Add basic file navigation (previous/next)
5. Integrate with existing results flow (create review session)
6. Basic styling and responsive layout

**Deliverables:**
- Users can view documents and extracted data side-by-side
- Navigate between files
- Responsive layout works on desktop and mobile

**Testing:**
- Test with PDFs and images
- Verify responsive behavior
- Navigation between files

### 10.2 Phase 2: Editing & Validation (Weeks 3-4)

**Goal:** Enable data editing and validation

**Tasks:**
1. Implement field editing in Form View
2. Add validation logic (field types, constraints)
3. Implement save/discard functionality
4. Add edit tracking and visual indicators
5. Create Table View for list-based data
6. Implement JSON View
7. Add unsaved changes warnings

**Deliverables:**
- Users can edit extracted data
- Real-time validation and error messages
- Edits are tracked and can be saved or discarded
- Multiple view modes available

**Testing:**
- Test editing various field types
- Validation with invalid inputs
- Save/discard behavior
- View mode switching

### 10.3 Phase 3: File List & ZIP Handling (Weeks 5-6)

**Goal:** Implement file list sidebar with ZIP expansion

**Tasks:**
1. Create file list sidebar component
2. Implement ZIP archive detection and expansion UI
3. Add file status indicators (not reviewed, approved, errors)
4. Implement file selection and navigation
5. Add search/filter functionality
6. Implement sidebar collapse/expand
7. Add keyboard navigation for file list

**Deliverables:**
- Functional file list sidebar showing all files
- ZIP archives expand to show contained files
- Click file to load its content and data
- Status indicators update based on review state
- Keyboard shortcuts work for file navigation

**Testing:**
- Test with single files and ZIP archives
- Multiple levels of ZIP nesting
- File filtering and search
- Keyboard navigation
- Status indicator updates

### 10.4 Phase 4: Approval & Export (Weeks 7-8)

**Goal:** Add approval workflow and batch operations

**Tasks:**
1. Implement approval workflow and API
2. Add approval button per file and "Approve All" batch operation
3. Implement approval metadata tracking
4. Add export with approval data
5. Implement markdown content retrieval API
6. Add Source/Markdown tab switching
7. Performance optimizations for large batches
8. Add keyboard shortcuts

**Deliverables:**
- Full approval workflow with metadata
- Batch operations (approve all, export approved only)
- Markdown content display for all file types
- Export includes approval status
- Keyboard shortcuts functional

**Testing:**
- End-to-end approval workflow
- Batch approval operations
- Markdown display for different file types
- Export with approval metadata
- Performance with 100+ files

### 10.5 Phase 5: Polish & Production (Weeks 9-10)

**Goal:** Production readiness and optimization

**Tasks:**
1. Accessibility audit and improvements
2. Performance optimization (lazy loading, caching)
3. Error handling and edge cases
4. Documentation (user guide, API docs)
5. Analytics and usage tracking
6. User testing and feedback
7. Bug fixes and refinements
8. Deployment and rollout

**Deliverables:**
- Fully accessible interface
- Optimized performance
- Comprehensive error handling
- Complete documentation
- Production deployment

**Testing:**
- Accessibility testing (screen readers, keyboard)
- Load testing with large documents
- Edge case testing
- User acceptance testing

---

## 11. Success Metrics

### 11.1 Performance Metrics

**Speed:**
- Review interface loads within 2 seconds
- Document rendering completes within 3 seconds
- Highlight appears within 200ms of hover
- Field updates reflect within 100ms

**Efficiency:**
- 50% reduction in time to review and validate extracted data
- 75% reduction in context switching (document ↔ data)
- Support for batches of 100+ files without performance degradation

### 11.2 User Satisfaction Metrics

**Usability:**
- 90% of users can complete a review task without training
- Average task completion time < 2 minutes per document
- < 5% error rate in data validation
- 80% user satisfaction score (post-feature survey)

**Adoption:**
- 70% of processed batches use review feature within first month
- 50% of users enable review for all processing jobs
- 90% approval rate after review (high confidence in validation)

### 11.3 Quality Metrics

**Data Accuracy:**
- 95% reduction in data entry errors after review
- 85% of AI-extracted data approved without edits
- < 10% field edit rate per document

**System Reliability:**
- 99.5% uptime for review interface
- < 1% error rate in coordinate extraction
- < 0.1% data loss rate (auto-save effectiveness)

---

## 12. Appendix

### 12.1 Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript 5
- React 18
- Tailwind CSS
- Zustand (state management)
- PDF.js (PDF rendering)
- Radix UI (accessible components)

**Backend:**
- FastAPI (Python)
- Pydantic (data validation)
- OpenAI API (vision for coordinate extraction)
- PyPDF2/pdfplumber (PDF text extraction)
- LibreOffice (headless for Office conversion)

**Infrastructure:**
- File storage: Local filesystem or S3
- Caching: Redis (optional)
- Database: PostgreSQL (for approval metadata)

### 12.2 Alternative Approaches Considered

#### 12.2.1 Coordinate Extraction

**Option A: Vision AI (Selected)**
- Pros: Works with all document types, high accuracy
- Cons: API costs, slower processing
- Decision: Best user experience, worth the cost

**Option B: Text-based search only**
- Pros: Fast, no API costs
- Cons: Doesn't work with images or scanned docs
- Decision: Rejected, too limited

**Option C: Manual annotation**
- Pros: User has full control
- Cons: Tedious, defeats purpose of automation
- Decision: Rejected, poor UX

#### 12.2.2 UI Layout

**Option A: Side-by-side (Selected)**
- Pros: Best for comparison workflows, standard pattern
- Cons: Requires wide screens
- Decision: Primary layout with mobile fallback

**Option B: Overlay/modal**
- Pros: Maximizes document viewing area
- Cons: Hides data, requires toggling
- Decision: Rejected, too much context switching

**Option C: Tabbed interface**
- Pros: Simple implementation
- Cons: Can't see both document and data simultaneously
- Decision: Rejected, loses core benefit

### 12.3 Known Limitations & Future Enhancements

**Current Limitations:**
- Coordinate extraction may be inaccurate for complex layouts
- Office document conversion requires LibreOffice installation
- Audio transcript highlighting requires word-level timestamps
- Limited to single-user editing (no collaboration)

**Future Enhancements (Post-MVP):**
- **Bi-directional highlighting** (Phase 2+): For PDF documents with searchable text, implement field-to-document highlighting by searching extracted values in PDF and displaying bounding boxes
- Real-time collaboration (multiple users reviewing same document)
- Version history and rollback
- Custom field types and validation rules
- Integration with external systems (CRM, ERP)
- Offline mode with sync
- Advanced search across all files in workspace

### 12.4 References

**Design Inspiration:**
- DocuSign review interface
- Adobe Acrobat document review
- Prodigy annotation tool
- Google Docs suggestion mode

**Technical Resources:**
- [PDF.js Documentation](https://mozilla.github.io/pdf.js/)
- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [LibreOffice Headless](https://wiki.documentfoundation.org/Faq/General/135)

### 12.5 Glossary

**Bi-directional Highlighting:** Interactive feature where hovering over data highlights the source in the document, and vice versa

**Bounding Box:** Rectangular coordinates defining the position of text or elements in a document

**Field Coordinate:** Data structure containing the position and dimensions of an extracted field within a document

**Review Session:** A collection of processed files grouped together for validation and approval

**Approval Metadata:** Information about who approved a document, when, and any associated comments

**Edit Tracking:** System for recording changes made to extracted data, including original and new values

**Nested Schema:** Pydantic model that extracts multiple instances of structured data from a single document

**Flat Schema:** Pydantic model that extracts a single set of fields from a document

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-07 | Claude Code | Initial document creation |
| 2.0 | 2025-10-07 | Claude Code | Major revision based on user feedback:<br>- Renamed to "Human-in-the-Loop Review Workspace"<br>- Changed to 3-panel layout with file list sidebar<br>- Removed bi-directional highlighting from MVP (moved to Phase 2+)<br>- Added ZIP archive file list expansion<br>- Emphasized markdown transformation visibility<br>- Simplified to browser-adaptive layout (removed mobile/zoom)<br>- Added clear entry point from Results Display |

**Approval:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Product Owner | [TBD] | [TBD] | [TBD] |
| Technical Lead | [TBD] | [TBD] | [TBD] |
| UX Designer | [TBD] | [TBD] | [TBD] |

**Document Location:**
`.claude/docs/interactive-document-review-feature.md`

---

*End of Document*
