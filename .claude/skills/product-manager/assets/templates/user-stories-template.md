# User Stories Template

## User Story Format

```
As a [user persona]
I want to [action]
So that [benefit]
```

---

## User Story Template

**Story ID**: US-[###]
**Title**: [Brief, descriptive title]
**Priority**: [Must Have | Should Have | Could Have | Won't Have]
**Story Points**: [1, 2, 3, 5, 8, 13, 21]
**Status**: [Backlog | In Progress | In Review | Done]

### User Story

As a [user persona]
I want to [action]
So that [benefit]

### Acceptance Criteria

**Given** [initial context/precondition]
**When** [action is performed]
**Then** [expected outcome]

**And** [additional outcome or condition if needed]

### Additional Details

**Notes**: [Any additional context, design links, technical details]

**Dependencies**: [Other stories or work that must be completed first]

**Related Stories**: [Links to related user stories]

---

## Example User Stories

### Example 1: File Upload Feature

**Story ID**: US-001
**Title**: Upload Multiple Files via Drag-and-Drop
**Priority**: Must Have
**Story Points**: 5
**Status**: In Progress

#### User Story

As a business analyst
I want to drag and drop multiple files into the upload zone
So that I can quickly upload batches of documents without selecting files one by one

#### Acceptance Criteria

**Given** I am on the file upload page
**When** I drag 10 PDF files from my desktop into the upload zone
**Then** all 10 files should appear in the file list with their names, sizes, and file types displayed

**And** the system should validate that all files are supported types (PDF, images, audio)
**And** the system should show an error message for any unsupported file types
**And** I should be able to remove individual files from the list before processing

#### Additional Details

**Notes**:
- Maximum of 50 files per upload session
- Maximum single file size: 50MB
- Maximum total upload size: 100MB
- Design mockups: [link to Figma]

**Dependencies**:
- Backend API must support multipart file upload (US-000)
- Frontend drag-and-drop component must be added to design system

**Related Stories**:
- US-002: Upload files via file browser
- US-003: Display upload progress for each file

---

### Example 2: Model Selection

**Story ID**: US-004
**Title**: Select Analysis Model from Dropdown
**Priority**: Must Have
**Story Points**: 3
**Status**: Backlog

#### User Story

As a business analyst
I want to select which analysis model to use from a dropdown menu
So that I can extract the right type of structured data from my documents

#### Acceptance Criteria

**Given** I have uploaded at least one file
**When** I click on the "Analysis Model" dropdown
**Then** I should see a list of all available models with descriptions

**And** each model should display:
- Model name (e.g., "Invoice Schema", "Report Summary")
- Short description of what it extracts
- Recommended document types

**When** I select a model from the dropdown
**Then** the selected model should be highlighted
**And** the model name should appear in the dropdown button

**Given** no files are uploaded
**When** I view the model dropdown
**Then** the dropdown should be disabled with a tooltip saying "Upload files first"

#### Additional Details

**Notes**:
- Models are fetched from `/api/models` endpoint
- Model descriptions come from backend `AVAILABLE_MODELS` dictionary
- Default model should be "General Analysis" if available

**Dependencies**:
- Backend `/api/models` endpoint must return model metadata (US-003)

**Related Stories**:
- US-005: Display model examples
- US-006: Allow custom model creation

---

### Example 3: Real-Time Processing Status

**Story ID**: US-007
**Title**: Display Real-Time Processing Progress
**Priority**: Should Have
**Story Points**: 8
**Status**: Backlog

#### User Story

As a business analyst
I want to see real-time progress updates while my files are being processed
So that I know the system is working and how long I need to wait

#### Acceptance Criteria

**Given** I have started processing files
**When** the system begins processing
**Then** I should see a progress section appear below the upload area

**And** the progress section should display:
- Overall progress percentage (e.g., "Processing 3 of 10 files - 30%")
- Status for each file (e.g., "Converting to markdown", "Analyzing with AI", "Complete")
- Estimated time remaining
- Any errors or warnings

**When** the processing completes successfully
**Then** the progress section should show "Complete - 10 of 10 files processed"
**And** the results section should automatically appear below

**When** processing fails for some files
**Then** the progress section should show which files failed
**And** display error messages for each failed file
**And** still allow me to view results for successfully processed files

#### Additional Details

**Notes**:
- Uses Server-Sent Events (SSE) for real-time updates
- Backend streams progress events via `/api/transform` endpoint
- Frontend uses EventSource API to receive updates
- Progress bar component: [link to design]

**Dependencies**:
- Backend streaming infrastructure must be implemented (US-006)
- Frontend SSE handler must be created

**Related Stories**:
- US-008: Add ability to cancel processing
- US-009: Add ability to retry failed files

---

## User Story Sizing Guide

### Story Points Reference

| Points | Complexity | Time Estimate | Example |
|--------|-----------|---------------|---------|
| 1 | Trivial | < 1 hour | Fix typo, update text |
| 2 | Simple | 2-4 hours | Add button with basic logic |
| 3 | Moderate | 1 day | Simple form with validation |
| 5 | Medium | 2-3 days | Feature with frontend + backend |
| 8 | Complex | 1 week | Feature with multiple components |
| 13 | Very Complex | 2 weeks | Large feature with integrations |
| 21 | Epic | 1 month+ | Should be broken down into smaller stories |

---

## MoSCoW Prioritization

### Must Have
Critical features without which the product cannot launch or function properly.

**Example**: User authentication, core file upload, basic processing

### Should Have
Important features that significantly improve the product but aren't critical for initial launch.

**Example**: Real-time progress updates, bulk file operations, advanced filters

### Could Have
Nice-to-have features that would improve user experience but can be deferred.

**Example**: Dark mode, keyboard shortcuts, custom themes

### Won't Have
Features explicitly excluded from current scope, but may be considered in the future.

**Example**: Mobile app, offline mode, AI model training

---

## Tips for Writing Good User Stories

1. **Keep it user-centric**: Always write from the user's perspective, not the system's
2. **Focus on the why**: The "so that" clause explains the value/benefit
3. **Make it testable**: Acceptance criteria should be specific and verifiable
4. **Keep it small**: Stories should be completable within a sprint
5. **Avoid technical jargon**: Use language users would understand
6. **Include edge cases**: Think about error states and unusual scenarios
7. **Link to designs**: Reference mockups, wireframes, or prototypes
8. **Collaborate**: Involve engineers, designers, and stakeholders in refining stories

---

## Anti-Patterns to Avoid

**Too Technical**:
❌ "As a system, I want to implement a RESTful API endpoint..."
✅ "As a developer, I want to call an API to fetch user data so that I can display it in the UI"

**Too Vague**:
❌ "As a user, I want the app to be faster"
✅ "As a user, I want the page to load in under 2 seconds so that I don't get frustrated waiting"

**Too Large**:
❌ "As a user, I want a complete dashboard with charts, filters, and export functionality"
✅ Break into multiple stories:
- "As a user, I want to see a chart of my usage trends"
- "As a user, I want to filter data by date range"
- "As a user, I want to export my data as CSV"

**Missing Acceptance Criteria**:
❌ Story without clear definition of "done"
✅ Include Given-When-Then scenarios that can be tested

---

## Template for Epic (Large Feature)

**Epic ID**: EP-[###]
**Title**: [High-level feature name]
**Goal**: [What we want to achieve]
**Target Release**: [Quarter/Date]

### Description
[Detailed description of the epic and why it matters]

### Success Metrics
- [Metric 1]: [Target]
- [Metric 2]: [Target]

### User Stories (Child Stories)
- [ ] US-### - [Story title]
- [ ] US-### - [Story title]
- [ ] US-### - [Story title]

### Dependencies
- [External dependency 1]
- [External dependency 2]

### Status
[Not Started | In Progress | Completed]

**Example**:

**Epic ID**: EP-001
**Title**: Bulk Document Processing
**Goal**: Enable users to process large batches of documents efficiently
**Target Release**: Q1 2024

**Description**:
Users need to process 50-100 documents at a time for monthly reporting. Current single-file upload is too slow and manual. This epic adds bulk upload, batch processing, and progress tracking.

**Success Metrics**:
- 70% of users adopt bulk upload within 2 months
- Average processing time per document reduced by 60%
- User satisfaction score increases from 7.2 to 8.5

**User Stories**:
- [ ] US-001 - Upload multiple files via drag-and-drop
- [ ] US-002 - Upload files via file browser
- [ ] US-003 - Display real-time processing progress
- [ ] US-004 - Export batch results to Excel
- [ ] US-005 - Retry failed files individually
