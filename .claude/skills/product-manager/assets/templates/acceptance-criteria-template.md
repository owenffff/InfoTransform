# Acceptance Criteria Template

## What Are Acceptance Criteria?

Acceptance criteria define the specific conditions that must be met for a user story or feature to be considered "done." They serve as a contract between the product team, engineering, and QA on what success looks like.

---

## Characteristics of Good Acceptance Criteria

Good acceptance criteria are:

- **Specific**: No ambiguity about what "done" means
- **Testable**: Can be verified through manual or automated testing
- **Achievable**: Within scope and technically feasible
- **Relevant**: Directly related to the user story or feature
- **Clear**: Understandable by all team members (PM, engineering, design, QA)
- **Complete**: Covers happy path, edge cases, and error states

---

## Format 1: Given-When-Then (Recommended)

Based on Behavior-Driven Development (BDD), this format clearly defines context, action, and outcome.

### Template

```
Given [initial context or precondition]
When [action is performed]
Then [expected outcome]
And [additional outcome if needed]
```

### Example 1: File Upload

```
Given I am on the upload page
When I drag 3 PDF files into the upload zone
Then all 3 files should appear in the file list
And each file should display its name, size, and type
And I should see a "Remove" button next to each file
```

### Example 2: Model Selection

```
Given I have uploaded at least one file
When I click on the "Select Model" dropdown
Then I should see a list of all available models
And each model should show its name and description
And the currently selected model should be highlighted

Given no files have been uploaded
When I view the model selection dropdown
Then the dropdown should be disabled
And a tooltip should say "Upload files first"
```

### Example 3: Error Handling

```
Given I am uploading files
When I drag a file larger than 50MB into the upload zone
Then the file should be rejected
And an error message should appear: "File exceeds 50MB limit"
And other valid files should still be accepted
And I should be able to dismiss the error message
```

---

## Format 2: Checklist (Simple Features)

For straightforward features, a checklist can be clear and concise.

### Template

```
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]
- [ ] [Edge case 1]
- [ ] [Edge case 2]
- [ ] [Error state 1]
```

### Example: Bulk File Upload

```
- [ ] User can drag and drop multiple files (2-50) into upload zone
- [ ] User can select multiple files via file browser
- [ ] System validates file types (PDF, JPG, PNG, MP3, WAV)
- [ ] Invalid file types show error message without blocking valid files
- [ ] Each file displays: name, size (KB/MB), file type icon
- [ ] User can remove individual files before processing
- [ ] Total batch size is limited to 100MB
- [ ] Uploading 0 files shows helpful message
- [ ] Uploading 51+ files shows error: "Maximum 50 files allowed"
- [ ] Duplicate files are highlighted with warning
```

---

## Format 3: Scenario-Based (Complex Features)

For features with multiple user paths, organize by scenario.

### Template

```
**Scenario 1: [Title]**
- [Step 1]
- [Step 2]
- [Expected outcome]

**Scenario 2: [Title]**
- [Step 1]
- [Step 2]
- [Expected outcome]
```

### Example: Real-Time Processing Progress

```
**Scenario 1: Successful Batch Processing**
- User uploads 10 files and clicks "Process"
- System displays progress section with "Processing 0 of 10 (0%)"
- As each file processes, counter updates: "Processing 3 of 10 (30%)"
- Each file shows status: "Converting..." → "Analyzing..." → "Complete"
- When all complete, shows "Processing complete: 10 of 10 (100%)"
- Results section appears automatically below progress

**Scenario 2: Partial Failure**
- User uploads 10 files and clicks "Process"
- 7 files process successfully, 3 fail due to invalid format
- Progress shows "Completed 7 of 10 (3 failed)"
- Failed files display error icon and message: "Invalid file format"
- Successfully processed files show in results section
- User can retry failed files individually

**Scenario 3: Complete Failure**
- User uploads 5 files and clicks "Process"
- Backend API is down
- Progress shows "Processing failed - Unable to connect to server"
- Error message provides troubleshooting steps
- User can retry entire batch when connection restored

**Scenario 4: User Cancels Processing**
- User uploads 20 files and starts processing
- After 5 files complete, user clicks "Cancel"
- Processing stops immediately
- Completed files (5) show in results section
- Incomplete files (15) return to "Ready" state
- User can resume processing the remaining files
```

---

## Format 4: Table Format (Comparison/States)

For features with multiple states or variations, a table can be clearer.

### Example: File Upload States

| State | User Action | System Behavior | UI Display |
|-------|-------------|-----------------|------------|
| No files uploaded | User views upload zone | Upload zone is empty | "Drag files here or click to browse" |
| Dragging files over zone | User drags files over | Upload zone highlights | Blue border, "Drop files here" |
| Valid file dropped | User drops PDF file | File is accepted | File appears in list with name, size, type |
| Invalid file dropped | User drops .exe file | File is rejected | Error toast: "Unsupported file type: .exe" |
| 50 files uploaded | User tries to add more | System prevents upload | Error: "Maximum 50 files per batch" |
| File being removed | User clicks "Remove" | File disappears from list | Remaining files stay in list |

---

## Including Edge Cases

Always consider and document edge cases:

### Categories of Edge Cases

1. **Boundary Conditions**
   - Minimum/maximum values (file size, file count, character limits)
   - Empty states (no files, no models, no results)
   - Single item vs. multiple items

2. **Invalid Input**
   - Wrong file types
   - Corrupted files
   - Missing required fields
   - Special characters in filenames

3. **System States**
   - Slow network connection
   - API timeout or failure
   - Out of memory
   - Concurrent operations

4. **User Behavior**
   - Rapid clicking (double-submit)
   - Browser back button
   - Page refresh during processing
   - Multiple browser tabs

### Example: Edge Cases for File Upload

```
**Boundary Conditions:**
- [ ] User uploads exactly 1 file (minimum)
- [ ] User uploads exactly 50 files (maximum)
- [ ] User uploads file exactly 50MB (size limit)
- [ ] User uploads 0 files and clicks "Process" → Error message

**Invalid Input:**
- [ ] User uploads file with no extension → Error message
- [ ] User uploads corrupted PDF → Error during processing with helpful message
- [ ] User uploads file with special chars (#, %, &) → Filename is sanitized
- [ ] User uploads file with 500-character name → Truncated with ellipsis

**System States:**
- [ ] User uploads on slow connection → Shows "Uploading..." with progress bar
- [ ] Backend API is down → Error message with retry button
- [ ] User has 500ms latency → UI remains responsive, queue uploads
- [ ] Two uploads happen simultaneously → Both succeed without conflict

**User Behavior:**
- [ ] User clicks "Upload" twice rapidly → Second click is ignored
- [ ] User refreshes page during upload → Confirmation dialog appears
- [ ] User opens two tabs and uploads in both → Separate upload sessions
- [ ] User hits browser back button → Confirmation dialog if unsaved work
```

---

## Error States Template

Always define how errors are handled:

### Template

```
**Error: [Error Name]**
- **Trigger**: [What causes this error]
- **User Sees**: [Error message displayed]
- **User Can Do**: [Available actions to resolve]
- **System Does**: [Backend behavior]
```

### Example: Error States for Document Processing

```
**Error: File Too Large**
- **Trigger**: User uploads file over 50MB
- **User Sees**: Toast error "File exceeds 50MB limit. Please reduce file size or split into multiple files."
- **User Can Do**: Remove file, upload smaller file
- **System Does**: Rejects file, doesn't add to list, other files unaffected

**Error: Unsupported File Type**
- **Trigger**: User uploads .exe, .dmg, or other unsupported file
- **User Sees**: Toast error "Unsupported file type: .exe. Supported types: PDF, JPG, PNG, MP3, WAV"
- **User Can Do**: Remove file, upload supported file type
- **System Does**: Rejects file, shows list of supported types

**Error: Processing Failed**
- **Trigger**: Backend API returns 500 error during processing
- **User Sees**: Error in progress section "Processing failed for document.pdf: Server error. Please try again."
- **User Can Do**: Click "Retry" button for failed file, continue viewing successful results
- **System Does**: Logs error details, preserves successfully processed files, allows retry

**Error: Network Timeout**
- **Trigger**: API call takes longer than 30 seconds
- **User Sees**: "Processing timed out. Your files may still be processing. Please refresh to check status."
- **User Can Do**: Click "Refresh" button, wait and retry
- **System Does**: Continues processing in background, allows status check via refresh
```

---

## Accessibility Acceptance Criteria

Don't forget accessibility requirements:

### Template

```
**Keyboard Navigation:**
- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical (left-to-right, top-to-bottom)
- [ ] Focus indicators are visible on all focusable elements
- [ ] User can operate all features using only keyboard

**Screen Reader:**
- [ ] All images have alt text
- [ ] Form inputs have associated labels
- [ ] Dynamic content changes are announced
- [ ] Error messages are announced when they appear

**Visual:**
- [ ] Color contrast meets WCAG AA standards (4.5:1 for text)
- [ ] Information is not conveyed by color alone
- [ ] Text is resizable up to 200% without breaking layout
- [ ] Focus indicators have 3:1 contrast ratio

**Other:**
- [ ] Motion/animations can be disabled (prefers-reduced-motion)
- [ ] Time limits can be extended or disabled
- [ ] Page is usable at 200% zoom
```

---

## Performance Acceptance Criteria

Define performance expectations:

### Template

```
- [ ] Page loads in under [X seconds] on [network condition]
- [ ] API responds in under [X seconds] for [scenario]
- [ ] UI remains responsive during [operation]
- [ ] Can handle [X] concurrent users/operations
```

### Example: Performance Criteria for Bulk Upload

```
- [ ] Upload zone responds to drag events within 100ms
- [ ] File list updates within 200ms after files dropped
- [ ] Can handle uploading 50 files simultaneously without UI freeze
- [ ] Progress updates stream in real-time (< 1 second latency)
- [ ] Page remains interactive during file processing
- [ ] Can process 10 documents in under 30 seconds (on average)
```

---

## Security Acceptance Criteria

For features with security implications:

### Template

```
**Authentication:**
- [ ] Feature requires authenticated user
- [ ] Session timeout is enforced
- [ ] Unauthorized access returns 401/403

**Authorization:**
- [ ] User can only access their own data
- [ ] Admin-only features require admin role
- [ ] Permissions are checked on both client and server

**Data Protection:**
- [ ] Sensitive data is encrypted in transit (HTTPS)
- [ ] Sensitive data is encrypted at rest
- [ ] PII is masked in logs and error messages
- [ ] Files are deleted after processing (or retention period)

**Input Validation:**
- [ ] All user input is validated and sanitized
- [ ] File uploads are scanned for malware
- [ ] SQL injection is prevented (parameterized queries)
- [ ] XSS attacks are prevented (escaped output)
```

---

## Review Checklist for Acceptance Criteria

Before finalizing, verify your acceptance criteria:

- [ ] **Covers happy path**: Standard successful use case is defined
- [ ] **Covers edge cases**: Boundary conditions and unusual inputs
- [ ] **Covers error states**: What happens when things go wrong
- [ ] **Testable**: QA can write test cases from these criteria
- [ ] **Clear**: No ambiguous terms like "fast", "easy", "good"
- [ ] **Complete**: Engineering knows exactly what to build
- [ ] **Accessible**: Includes accessibility requirements
- [ ] **Performant**: Defines performance expectations
- [ ] **Secure**: Addresses security concerns if applicable

---

## Anti-Patterns to Avoid

**Too Vague:**
❌ "The upload feature should be user-friendly"
✅ "User can drag and drop up to 50 files, each file displays name and size, invalid files show clear error messages"

**Too Technical:**
❌ "API should return 200 status code with JSON payload containing array of file objects"
✅ "When upload succeeds, user sees list of uploaded files with names and sizes"

**Missing Edge Cases:**
❌ "User can upload files"
✅ "User can upload files AND system handles: max file size exceeded, unsupported file types, network errors, duplicate files"

**Not Testable:**
❌ "Upload should be fast"
✅ "Upload UI responds within 200ms, files appear in list within 500ms"

**Missing Error States:**
❌ "User can process documents"
✅ "User can process documents AND if processing fails, error message explains why and offers retry option"

---

## Complete Example: Bulk File Upload Feature

### User Story

As a business analyst
I want to upload multiple documents at once
So that I can process batches of files efficiently

### Acceptance Criteria

**Happy Path (Given-When-Then):**

```
Given I am on the upload page
When I drag 10 PDF files into the upload zone
Then all 10 files appear in the file list
And each file displays: name, size, file type icon, and "Remove" button
And the total batch size is shown at the bottom
And the "Process" button becomes enabled
```

**File Browser Upload:**

```
Given I am on the upload page
When I click "Browse" and select 5 files from my computer
Then those 5 files are added to the file list
And they display the same information as drag-and-drop uploads
```

**Removing Files:**

```
Given I have uploaded 10 files
When I click the "Remove" button next to one file
Then that file is removed from the list
And the remaining 9 files stay in the list
And the total batch size updates
```

**Edge Cases:**

- [ ] User uploads exactly 1 file → Success
- [ ] User uploads exactly 50 files (max) → Success
- [ ] User tries to upload 51 files → Error: "Maximum 50 files per batch"
- [ ] User uploads 0 files and clicks "Process" → Error: "Please upload at least one file"
- [ ] User uploads file with 200-character filename → Filename truncated with ellipsis in UI, full name in tooltip
- [ ] User uploads duplicate files → Warning icon appears, tooltip says "Duplicate file"

**Error States:**

```
Given I am uploading files
When I drag a .exe file into the upload zone
Then the file is rejected
And an error toast appears: "Unsupported file type: .exe. Supported: PDF, JPG, PNG, MP3, WAV"
And other valid files are unaffected

Given I am uploading files
When I drag a 60MB file (over 50MB limit)
Then the file is rejected
And an error toast appears: "File exceeds 50MB limit"
And a tooltip suggests: "Compress the file or split into multiple files"
```

**Performance:**

- [ ] Upload zone highlights within 100ms when files are dragged over
- [ ] Files appear in list within 500ms of being dropped
- [ ] UI remains responsive while uploading 50 files
- [ ] Can handle 100MB total upload size without timeout

**Accessibility:**

- [ ] User can tab to upload zone and press Enter/Space to open file browser
- [ ] Screen reader announces "Upload zone, drag files here or press Enter to browse"
- [ ] When files are added, screen reader announces "10 files uploaded"
- [ ] Remove buttons are keyboard accessible with focus indicators
- [ ] Upload zone has visible focus indicator when tabbed to

**Visual/Responsive:**

- [ ] Upload zone works on desktop, tablet (768px+), and mobile (375px+)
- [ ] File list is scrollable if more than 10 files
- [ ] Touch gestures work on mobile/tablet devices
- [ ] Dark mode is supported (if app has dark mode)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-10-21 | Product Team | Initial template |
