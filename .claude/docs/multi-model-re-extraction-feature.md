# Multi-Model Re-Extraction Feature

**Feature Requirement Document**
**Version:** 1.0
**Date:** 2025-10-20
**Project:** InfoTransform
**Status:** Design Phase

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
12. [Open Questions & Future Enhancements](#12-open-questions--future-enhancements)

---

## 1. Executive Summary

### 1.1 Purpose

The Multi-Model Re-Extraction feature enables users to re-run document extraction using different AI models **without re-uploading files**, allowing them to:
- **Compare model outputs** side-by-side to identify the best extraction quality
- **Improve accuracy** by trying alternative models when initial results are unsatisfactory
- **Make informed decisions** about which model works best for their specific document types

### 1.2 Value Proposition

**For End Users:**
- Save time by avoiding re-upload when initial extraction is poor
- Gain confidence through model comparison and validation
- Improve data quality by selecting the best-performing model for their documents

**For AI Factory:**
- Reduce support burden ("extraction didn't work well" → self-service solution)
- Gather valuable data on model performance across document types
- Enable users to optimize extraction quality independently

### 1.3 Key Principles

1. **Efficiency First**: Reuse cached markdown conversions to minimize processing time
2. **Same Schema**: Lock to the original document schema to ensure valid comparisons
3. **Hybrid Approach**: Single model by default, with optional comparison for power users
4. **Clear Guidance**: Help users understand when and why to try different models

---

## 2. Feature Overview

### 2.1 What It Does

After completing an initial extraction, users can:
1. **Try Another Model**: Re-run extraction on the same files using a different AI model
2. **Compare Results**: View original and new extractions side-by-side with difference highlighting
3. **Select Best Result**: Choose which extraction version to keep or export

### 2.2 What It Doesn't Do

- ❌ Change the document schema (schema is locked to original selection)
- ❌ Re-upload files (uses cached files and markdown)
- ❌ Allow unlimited model attempts (recommend limiting to 3-4 versions per file)
- ❌ Automatically select "best" result (user makes the final decision)

### 2.3 When Users Need This

**Scenario 1: Poor Initial Extraction**
> "I ran extraction with GPT-4o-mini but it missed half the fields. Let me try GPT-4o to see if it's more accurate."

**Scenario 2: Model Performance Uncertainty**
> "I'm not sure which model works best for invoices. Let me compare GPT-4o vs GPT-4o-mini side-by-side."

**Scenario 3: Cost vs Quality Trade-offs**
> "The expensive model gave great results, but would the cheaper model work just as well? Let me test it."

---

## 3. User Stories

### 3.1 Core User Stories

#### US-1: Try Alternative Model (Single Re-Extraction)
**As a** data analyst
**I want to** re-run extraction using a different AI model without re-uploading files
**So that** I can improve accuracy when initial results are poor

**Acceptance Criteria:**
- User sees "Try Another Model" button after extraction completes
- User selects a different model from dropdown (excludes already-used models)
- Extraction runs using cached markdown (no file re-upload needed)
- New results appear alongside original results with version labels (V1, V2)
- User can switch between versions or view side-by-side

---

#### US-2: Compare Multiple Models Side-by-Side
**As a** quality assurance specialist
**I want to** compare extraction results from 2-3 different models simultaneously
**So that** I can identify which model performs best for my document type

**Acceptance Criteria:**
- User clicks "Compare with Other Models" button
- User selects 1-2 additional models to run in parallel
- System runs multiple extractions concurrently
- Results display in split-view comparison mode with diff highlighting
- Fields with different values are visually highlighted
- User can select preferred version for each field or entire document

---

#### US-3: Understand Model Selection
**As a** first-time user
**I want to** understand when and why I should try different models
**So that** I can make informed decisions without wasting time or credits

**Acceptance Criteria:**
- Tooltip/help text explains when to consider trying different models
- Model dropdown shows key characteristics (speed, cost, accuracy tier)
- System suggests alternative models based on initial extraction quality
- Clear indicators show which models have already been tried

---

### 3.2 Edge Case Stories

#### US-4: Handle Failed Re-Extraction
**As a** user
**I want to** be notified when a re-extraction fails
**So that** I can retry with another model or troubleshoot the issue

**Acceptance Criteria:**
- Failed extractions show error message with reason
- Original results remain intact
- User can retry with same or different model
- Failed attempts don't count against version limits

---

#### US-5: Preserve Original Results
**As a** user
**I want to** ensure my original extraction results are never lost
**So that** I can always fall back to the first version if needed

**Acceptance Criteria:**
- Original extraction (V1) is marked as "Original" and cannot be deleted
- Re-extractions create new versions (V2, V3, etc.)
- User can revert to any previous version
- Export includes version history metadata

---

## 4. Functional Requirements

### 4.1 Core Functionality

#### FR-1: Model Selection UI
- Display "Try Another Model" button in results panel after extraction completes
- Show model dropdown listing available models not yet used
- Display model characteristics: name, speed tier, cost indicator, accuracy tier
- Gray out or hide already-used models
- Show count of remaining attempts (e.g., "2 more attempts available")

#### FR-2: Re-Extraction Processing
- Use same document schema as original extraction (locked)
- Reuse cached markdown conversions (no re-conversion needed)
- Process files in same order as original extraction
- Support both single-model and multi-model parallel execution
- Stream results using existing SSE architecture
- Track extraction attempt number and model used

#### FR-3: Version Management
- Label extractions as V1 (Original), V2, V3, etc.
- Store version metadata: model name, timestamp, user (if applicable)
- Allow switching between versions via dropdown or tabs
- Maintain version history for each file independently
- Limit to 3-4 versions per file to prevent system overload

#### FR-4: Comparison View
- Side-by-side split view for comparing two versions
- Diff highlighting for fields with different values
- Color-coded indicators: green (same), yellow (different), red (missing)
- Field-level selection: "Use V1" vs "Use V2" toggle for each field
- Bulk selection: "Use all from V2" button
- Quick stats: "15 fields differ between V1 and V2"

#### FR-5: Result Selection & Export
- Allow user to select preferred version for export
- Support creating "hybrid" version by mixing fields from different versions
- Include version metadata in exported files
- Export format shows which model was used for each field (optional)

---

### 4.2 Performance Requirements

#### PFR-1: Speed
- Re-extraction should be 5-10x faster than initial extraction (skip markdown conversion)
- Multi-model parallel execution should complete in ~same time as single model
- Version switching should be instant (<100ms)
- Comparison view rendering should handle 50+ fields without lag

#### PFR-2: Storage
- Cache markdown for 24 hours minimum after initial extraction
- Store up to 4 versions per file
- Auto-cleanup old versions after 7 days or when storage limit reached
- Compressed storage for version history

#### PFR-3: Scalability
- Support re-extraction for 1-100 files in a batch
- Handle concurrent re-extraction requests from multiple users
- Queue management for multi-model requests

---

### 4.3 Usability Requirements

#### UR-1: Discoverability
- "Try Another Model" button prominently placed in results area
- Contextual tooltip: "Not satisfied with the results? Try a different model"
- Help icon with explanation of when to use this feature

#### UR-2: Clarity
- Version labels clearly visible (V1 - Original, V2 - GPT-4o, etc.)
- Active version highlighted in UI
- Comparison mode clearly shows which versions are being compared

#### UR-3: Feedback
- Progress indicators during re-extraction
- Success/failure toast notifications
- Warning when approaching version limit
- Suggested next model based on document type or error patterns

---

## 5. Technical Architecture

### 5.1 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │ ResultsDisplay   │  │ Re-Extraction Panel            │  │
│  │ - Version tabs   │  │ - Model selector               │  │
│  │ - Active version │  │ - "Try Another Model" button   │  │
│  │ - Export button  │  │ - "Compare Models" button      │  │
│  └──────────────────┘  └────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Comparison View                                       │  │
│  │ - Side-by-side split                                  │  │
│  │ - Diff highlighting                                   │  │
│  │ - Field-level selection                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▼
                    API Request (SSE)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │ /api/re-extract (NEW)                                │  │
│  │ - Validate request (session_id, model, files)        │  │
│  │ - Retrieve cached markdown                           │  │
│  │ - Route to AI batch processor with new model         │  │
│  │ - Stream results with version metadata               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Session Manager (NEW)                                │  │
│  │ - Track extraction sessions                          │  │
│  │ - Store version history                              │  │
│  │ - Cache markdown for 24h                             │  │
│  │ - Link files to original extraction                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌───────────────────────────────┐   │
│  │ SQLite DB        │  │ File System Cache              │   │
│  │ - Sessions       │  │ - Markdown files (24h TTL)     │   │
│  │ - Versions       │  │ - Original uploaded files      │   │
│  │ - Metadata       │  │ - Extraction results JSON      │   │
│  └──────────────────┘  └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Data Models

#### Extraction Session
```python
class ExtractionSession:
    session_id: str              # UUID for the session
    created_at: datetime
    schema_name: str             # Locked document schema
    user_id: Optional[str]       # For multi-user scenarios
    status: str                  # 'active', 'completed', 'expired'
    expires_at: datetime         # 24h from creation
    file_count: int
```

#### Extraction Version
```python
class ExtractionVersion:
    version_id: str              # UUID
    session_id: str              # Foreign key to session
    version_number: int          # 1, 2, 3, etc.
    model_name: str              # 'gpt-4o', 'gpt-4o-mini', etc.
    created_at: datetime
    status: str                  # 'processing', 'completed', 'failed'
    file_results: List[FileVersionResult]
```

#### File Version Result
```python
class FileVersionResult:
    file_id: str                 # Links to original uploaded file
    filename: str
    version_id: str              # Foreign key to version
    markdown_cache_path: str     # Path to cached markdown
    extracted_data: Dict[str, Any]
    processing_time: float
    error: Optional[str]
```

---

## 6. Backend Requirements

### 6.1 New API Endpoints

#### 6.1.1 POST /api/re-extract
**Purpose**: Re-run extraction using a different model

**Request:**
```json
{
  "session_id": "uuid-of-original-session",
  "model_name": "gpt-4o",
  "file_ids": ["file1", "file2"],  // Optional: re-extract specific files only
  "compare_mode": false             // If true, run in parallel with current version
}
```

**Response**: SSE stream (same format as /api/transform)
```json
{"event": "file_start", "data": {"filename": "doc.pdf", "version": 2}}
{"event": "file_complete", "data": {"filename": "doc.pdf", "version": 2, "data": {...}}}
{"event": "complete", "data": {"total": 10, "successful": 9, "failed": 1}}
```

---

#### 6.1.2 GET /api/session/{session_id}/versions
**Purpose**: Retrieve all extraction versions for a session

**Response:**
```json
{
  "session_id": "uuid",
  "schema_name": "Invoice",
  "versions": [
    {
      "version_number": 1,
      "model_name": "gpt-4o-mini",
      "created_at": "2025-10-20T10:00:00Z",
      "status": "completed",
      "file_count": 10,
      "success_count": 9,
      "is_original": true
    },
    {
      "version_number": 2,
      "model_name": "gpt-4o",
      "created_at": "2025-10-20T10:05:00Z",
      "status": "completed",
      "file_count": 10,
      "success_count": 10,
      "is_original": false
    }
  ],
  "expires_at": "2025-10-21T10:00:00Z"
}
```

---

#### 6.1.3 GET /api/session/{session_id}/compare
**Purpose**: Get comparison data for two versions

**Query Params:**
- `v1`: version_number (e.g., 1)
- `v2`: version_number (e.g., 2)
- `file_id`: optional, compare specific file only

**Response:**
```json
{
  "version_1": {
    "version_number": 1,
    "model_name": "gpt-4o-mini"
  },
  "version_2": {
    "version_number": 2,
    "model_name": "gpt-4o"
  },
  "files": [
    {
      "filename": "invoice_001.pdf",
      "diff": {
        "invoice_number": {
          "v1": "INV-001",
          "v2": "INV-001",
          "status": "same"
        },
        "total_amount": {
          "v1": "1500",
          "v2": "1500.00",
          "status": "different"
        },
        "line_items": {
          "v1": ["Item 1", "Item 2"],
          "v2": ["Item 1", "Item 2", "Item 3"],
          "status": "different"
        }
      },
      "summary": {
        "same_count": 8,
        "different_count": 5,
        "missing_in_v1": 1,
        "missing_in_v2": 0
      }
    }
  ]
}
```

---

### 6.2 Backend Services

#### 6.2.1 Session Manager
**Location**: `backend/infotransform/services/session_manager.py`

**Responsibilities:**
- Create extraction sessions on initial /api/transform request
- Store session metadata in SQLite
- Track markdown cache paths and file IDs
- Handle session expiration (24h default)
- Cleanup expired sessions and cached files

**Key Methods:**
```python
class SessionManager:
    def create_session(schema_name: str, files: List[UploadFile]) -> str
    def get_session(session_id: str) -> ExtractionSession
    def add_version(session_id: str, model_name: str) -> ExtractionVersion
    def get_versions(session_id: str) -> List[ExtractionVersion]
    def get_cached_markdown(session_id: str, file_id: str) -> str
    def cleanup_expired_sessions() -> None
```

---

#### 6.2.2 Re-Extraction Processor
**Location**: `backend/infotransform/processors/re_extraction_processor.py`

**Responsibilities:**
- Validate re-extraction requests
- Retrieve cached markdown from session
- Route to AI batch processor with new model
- Stream results with version metadata
- Handle errors gracefully

**Key Methods:**
```python
class ReExtractionProcessor:
    async def re_extract(
        session_id: str,
        model_name: str,
        file_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream re-extraction results"""

    async def compare_extract(
        session_id: str,
        model_names: List[str]
    ) -> AsyncGenerator[str, None]:
        """Run multiple models in parallel for comparison"""
```

---

#### 6.2.3 Comparison Service
**Location**: `backend/infotransform/services/comparison_service.py`

**Responsibilities:**
- Compare extraction results between versions
- Generate diff data with field-level granularity
- Calculate similarity metrics
- Suggest which version might be better

**Key Methods:**
```python
class ComparisonService:
    def compare_versions(
        version_1: ExtractionVersion,
        version_2: ExtractionVersion
    ) -> Dict[str, Any]:
        """Generate comparison data"""

    def calculate_diff(
        data_1: Dict[str, Any],
        data_2: Dict[str, Any]
    ) -> Dict[str, DiffResult]:
        """Field-level diff calculation"""

    def suggest_better_version(
        diff: Dict[str, DiffResult],
        field_priorities: Dict[str, int]
    ) -> int:
        """Suggest which version is likely better"""
```

---

### 6.3 Database Schema

#### SQLite Tables

**extraction_sessions**
```sql
CREATE TABLE extraction_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    schema_name TEXT NOT NULL,
    user_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    expires_at TIMESTAMP NOT NULL,
    file_count INTEGER NOT NULL
);
```

**extraction_versions**
```sql
CREATE TABLE extraction_versions (
    version_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    model_name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    FOREIGN KEY (session_id) REFERENCES extraction_sessions(session_id),
    UNIQUE(session_id, version_number)
);
```

**file_version_results**
```sql
CREATE TABLE file_version_results (
    result_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    file_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    markdown_cache_path TEXT NOT NULL,
    extracted_data TEXT NOT NULL,  -- JSON
    processing_time REAL,
    error TEXT,
    FOREIGN KEY (version_id) REFERENCES extraction_versions(version_id)
);
```

---

## 7. Frontend Requirements

### 7.1 New Components

#### 7.1.1 ReExtractionPanel
**Location**: `frontend/components/ReExtractionPanel.tsx`

**Purpose**: UI for selecting model and triggering re-extraction

**Props:**
```typescript
interface ReExtractionPanelProps {
  sessionId: string;
  currentModel: string;
  availableModels: string[];
  usedModels: string[];
  onReExtract: (modelName: string) => void;
  onCompare: (modelNames: string[]) => void;
}
```

**Features:**
- Model dropdown with characteristics
- "Try Another Model" button (single extraction)
- "Compare with Other Models" button (multi-model)
- Version counter and limit indicator
- Help tooltip with guidance

---

#### 7.1.2 VersionTabs
**Location**: `frontend/components/VersionTabs.tsx`

**Purpose**: Switch between extraction versions

**Props:**
```typescript
interface VersionTabsProps {
  versions: ExtractionVersion[];
  activeVersion: number;
  onVersionChange: (version: number) => void;
  onCompareClick: (v1: number, v2: number) => void;
}
```

**Features:**
- Tab for each version (V1, V2, V3)
- Model name and timestamp in tab label
- "Original" badge on V1
- Compare button between versions

---

#### 7.1.3 ComparisonView
**Location**: `frontend/components/ComparisonView.tsx`

**Purpose**: Side-by-side comparison of two extraction versions

**Props:**
```typescript
interface ComparisonViewProps {
  version1: ExtractionVersion;
  version2: ExtractionVersion;
  diffData: ComparisonResult;
  onFieldSelect: (fieldName: string, selectedVersion: number) => void;
  onBulkSelect: (version: number) => void;
}
```

**Features:**
- Split-pane layout (50/50 or adjustable)
- Field-by-field diff highlighting
- Color-coded indicators (same/different/missing)
- Selection checkboxes per field
- Summary stats at top ("15 fields differ")
- "Use all from V2" bulk action button

---

### 7.2 State Management Extensions

#### 7.2.1 Zustand Store Updates
**File**: `frontend/lib/store.ts`

**New State:**
```typescript
interface AppState {
  // ... existing state ...

  // Re-extraction state
  currentSessionId: string | null;
  extractionVersions: ExtractionVersion[];
  activeVersionNumber: number;
  comparisonMode: boolean;
  comparisonVersions: [number, number] | null;

  // Actions
  setSessionId: (id: string) => void;
  addExtractionVersion: (version: ExtractionVersion) => void;
  setActiveVersion: (versionNumber: number) => void;
  enterComparisonMode: (v1: number, v2: number) => void;
  exitComparisonMode: () => void;
}
```

---

### 7.3 API Client Extensions

#### 7.3.1 New API Functions
**File**: `frontend/lib/api.ts`

```typescript
export async function reExtractFiles(
  sessionId: string,
  modelName: string,
  fileIds?: string[]
): Promise<EventSource> {
  // Stream re-extraction results via SSE
}

export async function getSessionVersions(
  sessionId: string
): Promise<ExtractionVersion[]> {
  // Fetch all versions for a session
}

export async function getVersionComparison(
  sessionId: string,
  v1: number,
  v2: number,
  fileId?: string
): Promise<ComparisonResult> {
  // Get diff data for comparison view
}
```

---

## 8. User Interface Specifications

### 8.1 Re-Extraction Panel UI

**Location**: Below "Extracted Data" section in ResultsDisplay

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│                    Extracted Data                        │
│  [Table view showing results...]                         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  🔄 Try a Different Model                                │
│                                                           │
│  Not satisfied with the extraction quality? Try another  │
│  AI model to improve accuracy or compare results.        │
│                                                           │
│  ┌────────────────────────────────────────────┐         │
│  │ Select Model                    ▼          │         │
│  │ • GPT-4o (Recommended)                     │         │
│  │   Fast • Accurate • Best for complex docs  │         │
│  │ • GPT-4o-mini                              │         │
│  │   Very fast • Cost-effective • Good for    │         │
│  │   simple extractions                       │         │
│  └────────────────────────────────────────────┘         │
│                                                           │
│  Currently using: GPT-4o-mini (V1 - Original)           │
│  Used models: GPT-4o-mini                                │
│  Remaining attempts: 2                                   │
│                                                           │
│  [ Try This Model ]  [ Compare Multiple Models ]        │
│                                                           │
│  💡 Tip: Try GPT-4o for better accuracy on complex      │
│         documents or GPT-4o-mini for faster processing  │
└─────────────────────────────────────────────────────────┘
```

**Interactions:**
1. Click "Try This Model" → Single re-extraction with selected model
2. Click "Compare Multiple Models" → Multi-select modal → Run 2-3 models in parallel
3. Model dropdown shows characteristics and grays out used models
4. Progress indicator during re-extraction
5. Success toast: "Re-extraction complete! Switch to V2 to view results."

---

### 8.2 Version Tabs UI

**Location**: Top of Extracted Data section

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│  Extracted Data                                          │
│                                                           │
│  ┌────────┬────────┬────────┐                           │
│  │ V1     │ V2     │ V3     │                           │
│  │ ●      │        │        │                           │
│  │ Original│ GPT-4o│ GPT-4o │                           │
│  │ GPT-4o-│ Oct 20 │ Mini   │                           │
│  │ mini   │ 10:05  │ Oct 20 │                           │
│  │ Oct 20 │        │ 10:10  │                           │
│  │ 10:00  │ Compare│ Compare│                           │
│  └────────┴────────┴────────┘                           │
│                                                           │
│  Currently viewing: V2 (GPT-4o)                          │
│  [ ⚖️ Compare with V1 ]                                  │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Active tab highlighted with colored indicator (●)
- V1 shows "Original" badge
- Each tab shows model name and timestamp
- "Compare" button appears on hover
- Click tab to switch versions instantly
- Click "Compare" to enter side-by-side comparison mode

---

### 8.3 Comparison View UI

**Mode**: Overlay modal or full-screen view

**Layout:**
```
┌───────────────────────────────────────────────────────────────────┐
│  Comparison View                                    [ Close × ]   │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Comparing: V1 (GPT-4o-mini) ⚡ Fast ⇄ V2 (GPT-4o) 🎯 Accurate   │
│                                                                    │
│  📊 Summary: 15 fields differ • 8 identical • 2 missing in V1    │
│                                                                    │
│  [ Use All from V1 ]  [ Use All from V2 ]  [ Export Comparison ] │
│                                                                    │
├───────────────────────────┬───────────────────────────────────────┤
│      V1 (GPT-4o-mini)     │         V2 (GPT-4o)                   │
├───────────────────────────┼───────────────────────────────────────┤
│                           │                                        │
│  Invoice Number           │  Invoice Number                        │
│  INV-001 ✓ Same           │  INV-001 ✓ Same                        │
│  [ Use This ]             │  [ Use This ]                          │
│                           │                                        │
├───────────────────────────┼───────────────────────────────────────┤
│  Total Amount ⚠️          │  Total Amount ⚠️                       │
│  1500                     │  1500.00                               │
│  [ ○ Use This ]           │  [ ● Use This ]                        │
│                           │                                        │
├───────────────────────────┼───────────────────────────────────────┤
│  Line Items ❌            │  Line Items ❌                         │
│  • Item 1                 │  • Item 1                              │
│  • Item 2                 │  • Item 2                              │
│  (Missing: Item 3)        │  • Item 3                              │
│  [ ○ Use This ]           │  [ ● Use This ]                        │
│                           │                                        │
├───────────────────────────┼───────────────────────────────────────┤
│  Vendor Name ✓            │  Vendor Name ✓                         │
│  Acme Corp                │  Acme Corp                             │
│  [ Use This ]             │  [ Use This ]                          │
│                           │                                        │
└───────────────────────────┴───────────────────────────────────────┘
│                                                                    │
│  [ Cancel ]  [ Save Selected Fields ]                             │
└───────────────────────────────────────────────────────────────────┘
```

**Color Coding:**
- ✓ Green = Same value in both versions
- ⚠️ Yellow = Different values (minor difference)
- ❌ Red = Significantly different or missing
- Gray background = Selected field

**Interactions:**
1. Radio button to select which version's value to use
2. "Use All from V1/V2" buttons for bulk selection
3. Scroll both panes in sync
4. Click "Save Selected Fields" to create hybrid version
5. Export comparison report as CSV/Excel

---

### 8.4 Mobile Responsive Design

**Breakpoints:**
- Desktop (>1024px): Full side-by-side comparison
- Tablet (768-1024px): Narrower split panes with horizontal scroll
- Mobile (<768px): Stacked view with toggle button to switch between V1/V2

---

## 9. Data Flow & Integration

### 9.1 Initial Extraction Flow (Modified)

```
User uploads files → /api/transform
                     ↓
              Create session in SQLite
              session_id = uuid()
              schema_name = selected_schema
              expires_at = now() + 24h
                     ↓
              Process files (existing flow)
              Save markdown to cache
              Link files to session
                     ↓
              Return session_id in SSE stream
              event: session_created
              data: {session_id: "uuid"}
                     ↓
              Frontend stores session_id in Zustand
```

---

### 9.2 Re-Extraction Flow

```
User clicks "Try Another Model"
User selects GPT-4o from dropdown
                     ↓
              POST /api/re-extract
              body: {
                session_id: "uuid",
                model_name: "gpt-4o"
              }
                     ↓
              Backend validates session
              Check session not expired
              Check model not already used
              Check version limit not exceeded
                     ↓
              Create new ExtractionVersion (V2)
              version_number = 2
              model_name = "gpt-4o"
                     ↓
              Retrieve cached markdown paths
              FROM file_version_results
              WHERE version_id = V1.version_id
                     ↓
              Route to AI batch processor
              Pass: markdown_paths, schema, new model
              Skip: file upload, markdown conversion
                     ↓
              Stream results via SSE
              event: file_complete
              data: {version: 2, filename: "doc.pdf", data: {...}}
                     ↓
              Save results to file_version_results
              version_id = V2.version_id
                     ↓
              Frontend receives SSE events
              Adds V2 to extractionVersions[]
              Shows success toast
              Automatically switches to V2 tab
```

---

### 9.3 Comparison Flow

```
User clicks "Compare with V1" on V2 tab
                     ↓
              GET /api/session/{session_id}/compare?v1=1&v2=2
                     ↓
              Backend retrieves both versions
              v1_results = SELECT * FROM file_version_results WHERE version_id = V1
              v2_results = SELECT * FROM file_version_results WHERE version_id = V2
                     ↓
              ComparisonService.compare_versions()
              For each file:
                Calculate field-by-field diff
                Categorize: same, different, missing
                Generate summary stats
                     ↓
              Return comparison JSON
                     ↓
              Frontend opens ComparisonView modal
              Renders split-pane UI
              Highlights differences
              Enables field selection
```

---

### 9.4 Session Cleanup Flow

```
Background scheduler (runs every hour)
                     ↓
              SessionManager.cleanup_expired_sessions()
                     ↓
              SELECT * FROM extraction_sessions
              WHERE expires_at < now()
              AND status = 'active'
                     ↓
              For each expired session:
                Delete cached markdown files
                Delete uploaded files
                UPDATE status = 'expired'
                (Keep metadata for analytics)
                     ↓
              Log cleanup stats
              "Cleaned up 15 expired sessions, freed 2.3 GB"
```

---

## 10. Implementation Phases

### Phase 1: MVP - Single Model Re-Extraction (2-3 weeks)

**Goal**: Allow users to try one alternative model

**Backend Tasks:**
1. Create database schema (SQLite tables)
2. Implement SessionManager service
3. Add /api/re-extract endpoint
4. Modify /api/transform to create sessions
5. Implement session cleanup background job

**Frontend Tasks:**
1. Add ReExtractionPanel component
2. Add model selector dropdown
3. Update Zustand store with session state
4. Add version tabs to ResultsDisplay
5. Handle SSE for re-extraction
6. Add success/error notifications

**Success Criteria:**
- ✅ Users can re-run extraction with a different model
- ✅ Re-extraction reuses cached markdown (5-10x faster)
- ✅ Version tabs show V1 and V2
- ✅ User can switch between versions
- ✅ Original results are preserved

---

### Phase 2: Comparison View (2-3 weeks)

**Goal**: Enable side-by-side comparison of two versions

**Backend Tasks:**
1. Implement ComparisonService
2. Add /api/session/{id}/compare endpoint
3. Add diff calculation logic
4. Generate comparison summaries

**Frontend Tasks:**
1. Create ComparisonView component
2. Implement split-pane layout
3. Add diff highlighting (color-coded)
4. Add field selection UI
5. Implement hybrid version creation

**Success Criteria:**
- ✅ Users can compare two versions side-by-side
- ✅ Differences are clearly highlighted
- ✅ Users can select preferred fields
- ✅ Hybrid version can be exported

---

### Phase 3: Multi-Model Parallel Extraction (1-2 weeks)

**Goal**: Run 2-3 models simultaneously for faster comparison

**Backend Tasks:**
1. Add parallel processing support to re-extraction
2. Handle concurrent AI batch requests
3. Optimize database writes for parallel versions

**Frontend Tasks:**
1. Add "Compare Multiple Models" button
2. Create multi-select model modal
3. Show parallel progress indicators
4. Auto-enter comparison mode when complete

**Success Criteria:**
- ✅ Users can select 2-3 models to run in parallel
- ✅ All models complete in ~same time as single model
- ✅ Comparison view loads automatically when complete

---

### Phase 4: Polish & Optimization (1-2 weeks)

**Goal**: Improve UX and performance

**Tasks:**
1. Add model suggestions based on document type
2. Implement smart caching strategies
3. Add analytics tracking for model performance
4. Improve error handling and user guidance
5. Optimize comparison view for large schemas
6. Add mobile-responsive comparison view
7. Implement keyboard shortcuts
8. Add export enhancements (comparison reports)

**Success Criteria:**
- ✅ Smooth, intuitive user experience
- ✅ Fast performance even with large datasets
- ✅ Clear guidance on when/how to use feature
- ✅ Works well on mobile devices

---

## 11. Success Metrics

### 11.1 Adoption Metrics

**Primary KPIs:**
- **Re-extraction Usage Rate**: % of users who use re-extraction feature
  - Target: 30% of users try re-extraction within first month

- **Version Comparison Rate**: % of re-extractions that enter comparison mode
  - Target: 50% of re-extractions use comparison view

- **Hybrid Version Creation**: % of comparisons that result in hybrid versions
  - Target: 25% create custom hybrid versions

### 11.2 Quality Metrics

**Accuracy Improvements:**
- **Data Quality Score**: User satisfaction with final results
  - Baseline: 70% (initial extraction only)
  - Target: 85% (with re-extraction option)

- **Error Reduction**: % reduction in failed extractions
  - Target: 30% fewer completely failed extractions

- **Field Completeness**: % of fields successfully extracted
  - Baseline: 75%
  - Target: 90%

### 11.3 Efficiency Metrics

**Time Savings:**
- **Re-extraction Speed**: Time to re-extract vs. initial extraction
  - Target: 5-10x faster (due to markdown caching)

- **User Time to Resolution**: Time from poor extraction to satisfactory result
  - Baseline: 15 minutes (manual review + re-upload)
  - Target: 3 minutes (re-extract + quick comparison)

**Cost Optimization:**
- **Token Usage**: Reduction in wasted tokens from re-uploads
  - Target: 40% reduction in duplicate markdown conversions

### 11.4 User Experience Metrics

**Satisfaction:**
- **Feature Satisfaction Score**: Rating of re-extraction feature (1-5)
  - Target: 4.2+

- **Support Ticket Reduction**: % reduction in "extraction failed" tickets
  - Target: 50% reduction

- **Net Promoter Score (NPS)**: Overall product NPS
  - Baseline: 35
  - Target: 45 (with re-extraction feature)

---

## 12. Open Questions & Future Enhancements

### 12.1 Open Questions

**Q1: Version Limits**
- How many re-extraction attempts should we allow per session?
- Current thinking: 3-4 versions to prevent abuse
- Alternative: Unlimited versions but charge per re-extraction?

**Q2: Session Expiration**
- What's the right balance between storage costs and user convenience?
- Current thinking: 24 hours
- Alternative: Extend to 7 days for premium users?

**Q3: Model Recommendations**
- Should we automatically suggest the best model based on document type?
- Current thinking: Show suggestions but let user decide
- Alternative: Auto-run best model after initial extraction fails?

**Q4: Pricing Model**
- Should re-extractions be free or charged separately?
- Current thinking: First 2 re-extractions free, then charge
- Alternative: Unlimited for enterprise plans, limited for free tier?

**Q5: Hybrid Version Persistence**
- Should hybrid versions be saved as V4, V5, etc.?
- Current thinking: Yes, treat as new version
- Alternative: Save as "Custom V2" variant?

---

### 12.2 Future Enhancements

#### FE-1: AI-Powered Model Selection
**Description**: Use ML to predict best model for each document type
**Value**: Reduce user decision fatigue, improve first-extraction success rate
**Effort**: Medium (requires training data collection)

#### FE-2: Confidence Scoring
**Description**: Show confidence scores for each extracted field
**Value**: Users can identify low-confidence fields and prioritize re-extraction
**Effort**: Medium (integrate with Pydantic AI agent)

#### FE-3: Selective Field Re-Extraction
**Description**: Re-extract only specific fields instead of entire document
**Value**: Faster, more cost-effective for partial corrections
**Effort**: High (requires granular AI prompting)

#### FE-4: Automatic Quality Detection
**Description**: System automatically suggests re-extraction when quality is low
**Value**: Proactive improvement without user needing to recognize poor quality
**Effort**: Medium (requires quality heuristics)

#### FE-5: Batch Re-Extraction Scheduling
**Description**: Schedule re-extraction for off-peak hours to save costs
**Value**: Lower API costs for large batches
**Effort**: Low (use background job queue)

#### FE-6: Version History Analytics
**Description**: Dashboard showing model performance trends over time
**Value**: Help users and AI Factory optimize model selection
**Effort**: Medium (requires analytics pipeline)

#### FE-7: Collaborative Comparison
**Description**: Multiple users can review and vote on preferred version
**Value**: Team-based quality assurance workflows
**Effort**: High (requires multi-user coordination)

#### FE-8: Export Comparison Reports
**Description**: Generate PDF/Excel reports showing side-by-side comparison
**Value**: Audit trail, stakeholder communication
**Effort**: Low (extend existing export functionality)

#### FE-9: Model Performance Benchmarking
**Description**: Show aggregated stats: "GPT-4o is 15% more accurate for invoices"
**Value**: Data-driven model selection guidance
**Effort**: Medium (requires analytics aggregation)

#### FE-10: Integration with Review Workspace
**Description**: Enable re-extraction from within Review Workspace
**Value**: Seamless workflow for human-in-the-loop review
**Effort**: Medium (integrate with existing review feature)

---

## Appendix A: Technical Considerations

### A.1 Security & Privacy

**Considerations:**
- Cached markdown files must be isolated per session (prevent cross-session access)
- Session IDs should be UUIDs (non-guessable)
- Implement rate limiting on /api/re-extract to prevent abuse
- Add authentication/authorization checks if multi-user support is added
- Encrypt sensitive data in SQLite database
- Audit logging for all re-extraction attempts

**Compliance:**
- GDPR: Right to deletion (user can request session cleanup)
- Data retention: Default 24h, configurable for compliance requirements
- PII handling: Ensure uploaded files don't contain PII or implement PII redaction

---

### A.2 Performance Optimization

**Backend:**
- Use async/await throughout for non-blocking I/O
- Implement connection pooling for SQLite
- Cache model schemas in memory (avoid repeated DB reads)
- Use background tasks for session cleanup (don't block main thread)
- Implement request queuing for high-concurrency scenarios

**Frontend:**
- Lazy load comparison view (only when user clicks "Compare")
- Virtual scrolling for large comparison tables (50+ fields)
- Debounce field selection actions to prevent excessive state updates
- Use React.memo() for expensive components
- Implement incremental SSE rendering (stream results as they arrive)

**Database:**
- Index foreign keys (session_id, version_id)
- Index created_at and expires_at for cleanup queries
- Consider partitioning by date for large-scale deployments
- Implement periodic VACUUM for SQLite maintenance

---

### A.3 Error Handling

**Backend Errors:**
- Session not found → 404 with clear message
- Session expired → 410 Gone with expiration timestamp
- Model already used → 400 with list of available models
- Version limit exceeded → 429 with retry-after header
- AI extraction failure → Log error, continue with other files, mark as failed in version

**Frontend Errors:**
- Network timeout → Retry with exponential backoff
- SSE connection drop → Auto-reconnect, resume from last event
- Invalid session → Redirect to home, show "Session expired" message
- Comparison load failure → Fallback to single version view

---

### A.4 Testing Strategy

**Unit Tests:**
- SessionManager: CRUD operations, expiration logic
- ComparisonService: Diff calculation, edge cases (null values, arrays)
- ReExtractionProcessor: Model routing, caching logic

**Integration Tests:**
- End-to-end re-extraction flow
- SSE streaming with version metadata
- Comparison API with complex schemas
- Session cleanup background job

**E2E Tests:**
- User uploads files → re-extracts → compares → exports
- Mobile responsive comparison view
- Error scenarios (expired session, invalid model)

---

### A.5 Deployment Considerations

**Environment Variables:**
```bash
# Re-extraction feature flags
ENABLE_RE_EXTRACTION=true
MAX_VERSIONS_PER_SESSION=4
SESSION_EXPIRATION_HOURS=24
MARKDOWN_CACHE_DIR=/tmp/infotransform/cache

# Cleanup job
SESSION_CLEANUP_INTERVAL_HOURS=1
```

**Configuration:**
```yaml
# config/config.yaml
re_extraction:
  enabled: true
  max_versions: 4
  session_expiration: 24h
  cleanup_interval: 1h
  markdown_cache_ttl: 24h

  # Model recommendations
  model_suggestions:
    invoice: ["gpt-4o", "gpt-4o-mini"]
    contract: ["gpt-4o"]
    receipt: ["gpt-4o-mini"]
```

---

## Appendix B: API Examples

### B.1 Re-Extraction Request

**Request:**
```bash
curl -X POST http://localhost:8000/api/re-extract \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "model_name": "gpt-4o",
    "file_ids": ["file_001", "file_002"]
  }'
```

**Response (SSE Stream):**
```
event: session_validated
data: {"session_id": "a1b2c3d4...", "version_number": 2}

event: file_start
data: {"filename": "invoice_001.pdf", "version": 2}

event: file_progress
data: {"filename": "invoice_001.pdf", "progress": 50}

event: file_complete
data: {
  "filename": "invoice_001.pdf",
  "version": 2,
  "model": "gpt-4o",
  "data": {
    "invoice_number": "INV-001",
    "total_amount": 1500.00,
    ...
  }
}

event: complete
data: {
  "version": 2,
  "total": 2,
  "successful": 2,
  "failed": 0,
  "processing_time": 12.5
}
```

---

### B.2 Comparison Request

**Request:**
```bash
curl -X GET "http://localhost:8000/api/session/a1b2c3d4.../compare?v1=1&v2=2&file_id=file_001"
```

**Response:**
```json
{
  "session_id": "a1b2c3d4...",
  "version_1": {
    "version_number": 1,
    "model_name": "gpt-4o-mini",
    "created_at": "2025-10-20T10:00:00Z"
  },
  "version_2": {
    "version_number": 2,
    "model_name": "gpt-4o",
    "created_at": "2025-10-20T10:05:00Z"
  },
  "files": [
    {
      "file_id": "file_001",
      "filename": "invoice_001.pdf",
      "diff": {
        "invoice_number": {
          "v1": "INV-001",
          "v2": "INV-001",
          "status": "same",
          "confidence": 1.0
        },
        "total_amount": {
          "v1": "1500",
          "v2": "1500.00",
          "status": "different",
          "difference_type": "format",
          "confidence": 0.95
        },
        "line_items": {
          "v1": ["Item 1", "Item 2"],
          "v2": ["Item 1", "Item 2", "Item 3"],
          "status": "different",
          "difference_type": "content",
          "missing_in_v1": ["Item 3"],
          "confidence": 0.8
        }
      },
      "summary": {
        "total_fields": 15,
        "same_count": 8,
        "different_count": 5,
        "missing_in_v1": 2,
        "missing_in_v2": 0,
        "confidence_avg": 0.87
      }
    }
  ]
}
```

---

## Document Change Log

| Version | Date       | Author      | Changes                                |
|---------|------------|-------------|----------------------------------------|
| 1.0     | 2025-10-20 | AI Factory  | Initial feature specification created  |

---

**End of Document**
