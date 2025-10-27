# Release Notes Template

## External Release Notes (Customer-Facing)

---

# [Product Name] - Version [X.Y.Z]

**Release Date**: [Month DD, YYYY]

## What's New 🎉

### [Feature Name 1]
Brief description of the new feature and the value it provides to users.

**What you can do now**:
- [Specific capability 1]
- [Specific capability 2]
- [Specific capability 3]

**Why it matters**: [Explain the benefit to users]

![Screenshot or GIF showing the feature]

---

### [Feature Name 2]
Brief description of another new feature.

**What you can do now**:
- [Specific capability 1]
- [Specific capability 2]

**Why it matters**: [Explain the benefit to users]

---

## Improvements ✨

### [Improvement Category 1]
- **[Component/Feature]**: [What improved and how it benefits users]
- **[Component/Feature]**: [What improved and how it benefits users]

### [Improvement Category 2]
- **[Component/Feature]**: [What improved and how it benefits users]

---

## Bug Fixes 🐛

We fixed several issues to improve your experience:

- **[Issue Description]**: Fixed an issue where [problem] when [scenario]. Now [expected behavior].
- **[Issue Description]**: Resolved a problem that caused [symptom]. [Action taken].
- **[Issue Description]**: Corrected [issue] to ensure [expected outcome].

---

## Known Issues ⚠️

We're aware of the following issues and working on fixes:

- **[Issue 1]**: [Description of the issue and any workarounds]
- **[Issue 2]**: [Description of the issue and any workarounds]

---

## Getting Started

**New to [Product Name]?**
- [Link to getting started guide]
- [Link to documentation]
- [Link to video tutorial]

**Need Help?**
- [Link to support]
- [Link to community forum]
- [Contact email]

---

## What's Next

We're working on exciting new features coming soon:
- [Upcoming feature 1]
- [Upcoming feature 2]
- [Upcoming feature 3]

Have feedback? We'd love to hear from you! [Feedback form link]

---

## Example: InfoTransform v1.2.0

**Release Date**: October 21, 2024

## What's New 🎉

### Bulk File Upload
Upload multiple documents at once with our new drag-and-drop bulk upload feature.

**What you can do now**:
- Drag up to 50 files at once into the upload zone
- Upload entire folders with one click
- See all your files with their sizes and types before processing
- Remove individual files from the batch before processing

**Why it matters**: Save time when processing large batches of documents. What used to take 10 minutes of clicking now takes 10 seconds of dragging.

![Animated GIF showing drag-and-drop of multiple files]

---

### Real-Time Processing Progress
Know exactly what's happening while your documents are being processed.

**What you can do now**:
- See live progress for each file (converting, analyzing, complete)
- View overall progress percentage
- Get estimated time remaining
- Identify which files succeeded or failed

**Why it matters**: No more wondering if the system is still working. You get transparency and confidence that your documents are being processed.

---

## Improvements ✨

### Performance
- **Faster processing**: Reduced average processing time by 40% for batches of 10+ files
- **Parallel conversion**: Documents now convert to markdown simultaneously instead of one-by-one

### User Interface
- **Clearer error messages**: More helpful explanations when something goes wrong
- **Better file type icons**: Easier to identify PDFs, images, and audio files at a glance
- **Responsive design**: Improved experience on tablets and smaller screens

### Export
- **Excel formatting**: Results exported to Excel now include proper column widths and header styling
- **CSV encoding**: Fixed character encoding issues when exporting to CSV

---

## Bug Fixes 🐛

- **File upload**: Fixed an issue where uploading files with special characters in filenames would fail. Now all valid filenames are supported.
- **Progress tracking**: Resolved a problem that caused progress updates to freeze at 50% for large PDF files. Progress now updates smoothly.
- **Model selection**: Corrected an issue where the selected model would reset after adding more files. Your selection now persists.
- **Result display**: Fixed formatting issues in the results table when extracting data with long text fields.

---

## Known Issues ⚠️

- **Safari compatibility**: Drag-and-drop may not work consistently in Safari 15 or earlier. Please upgrade to Safari 16+ or use Chrome/Edge.
- **Large ZIP files**: Extracting ZIP archives larger than 200MB may timeout. We recommend keeping archives under 200MB.

---

## Getting Started

**New to InfoTransform?**
- [Getting Started Guide](https://docs.example.com/getting-started)
- [Video Tutorial: Your First Document Analysis](https://youtube.com/watch?v=xxx)
- [Sample Documents to Try](https://example.com/samples)

**Need Help?**
- [Documentation](https://docs.example.com)
- [Community Forum](https://community.example.com)
- [Email Support](mailto:support@example.com)

---

## What's Next

We're working on exciting new features coming in Q4 2024:
- Custom document schemas: Create your own extraction models
- API access: Integrate InfoTransform into your workflows
- Scheduled processing: Automatically process documents from cloud storage

Have feedback or feature requests? [Share your ideas](https://feedback.example.com)

---

---

## Internal Release Notes (Engineering/QA)

---

# [Product Name] - Version [X.Y.Z]

**Release Date**: [YYYY-MM-DD]
**Git Tag**: `v[X.Y.Z]`
**Build**: `#[build-number]`

## Summary

[High-level summary of what changed in this release]

---

## New Features

### [Feature Name 1]
**Jira**: [PROJ-###]
**Pull Request**: [#PR-number]

**Changes**:
- [Technical detail 1]
- [Technical detail 2]
- [Technical detail 3]

**API Changes**: [Any new or modified endpoints]

**Database Changes**: [Schema migrations, new tables, etc.]

**Configuration**: [New environment variables or config options]

---

## Improvements

### Backend
- **[Component]**: [Technical description of improvement] ([#PR-number])
- **[Component]**: [Technical description of improvement] ([#PR-number])

### Frontend
- **[Component]**: [Technical description of improvement] ([#PR-number])
- **[Component]**: [Technical description of improvement] ([#PR-number])

---

## Bug Fixes

### Critical
- **[PROJ-###]**: [Technical description of bug and fix] ([#PR-number])

### High Priority
- **[PROJ-###]**: [Technical description of bug and fix] ([#PR-number])
- **[PROJ-###]**: [Technical description of bug and fix] ([#PR-number])

### Medium Priority
- **[PROJ-###]**: [Technical description of bug and fix] ([#PR-number])

---

## API Changes

### Breaking Changes ⚠️
- **[Endpoint]**: [What changed and why] ([#PR-number])
  - **Migration Guide**: [How to update client code]

### New Endpoints
- `POST /api/new-endpoint` - [Description] ([#PR-number])
- `GET /api/another-endpoint` - [Description] ([#PR-number])

### Modified Endpoints
- `POST /api/existing-endpoint` - [What changed] ([#PR-number])
  - **Backward Compatible**: Yes/No
  - **Deprecated Parameters**: [List any deprecated params]

---

## Database Changes

### Migrations
- **Migration File**: `[YYYYMMDD_HHMMSS_migration_name.sql]`
- **Direction**: Forward only / Reversible
- **Duration**: [Estimated time]
- **Impact**: [Downtime required? Data loss risk?]

### Schema Changes
- **New Tables**: [table_name] - [Purpose]
- **Modified Tables**: [table_name] - [What changed]
- **Dropped Tables**: [table_name] - [Why removed]

### Data Changes
- [Description of any data migrations or transformations]

---

## Configuration Changes

### Environment Variables
- **New**: `NEW_VAR_NAME` - [Description, default value]
- **Modified**: `EXISTING_VAR` - [What changed]
- **Deprecated**: `OLD_VAR` - [Use `NEW_VAR` instead]

### Config Files
- [List any changes to config files]

---

## Dependencies

### Updated
- [package-name] `v1.0.0` → `v1.2.0` - [Reason for update]
- [package-name] `v2.5.0` → `v3.0.0` - [Breaking changes? Migration needed?]

### Added
- [new-package] `v1.0.0` - [Why added]

### Removed
- [old-package] - [Why removed, replacement]

---

## Testing

### Test Coverage
- **Unit Tests**: [Coverage %] ([+/- change])
- **Integration Tests**: [Number of tests added/modified]
- **E2E Tests**: [Number of scenarios covered]

### Manual Testing Required
- [ ] [Test scenario 1]
- [ ] [Test scenario 2]
- [ ] [Test scenario 3]

---

## Deployment Notes

### Pre-Deployment Steps
1. [Step 1: e.g., Backup database]
2. [Step 2: e.g., Set maintenance mode]
3. [Step 3: e.g., Run migration script]

### Deployment Steps
1. [Step 1: e.g., Pull latest code]
2. [Step 2: e.g., Install dependencies]
3. [Step 3: e.g., Build frontend]
4. [Step 4: e.g., Restart services]

### Post-Deployment Verification
- [ ] [Check 1: Health endpoint returns 200]
- [ ] [Check 2: Can create new records]
- [ ] [Check 3: Background jobs are running]

### Rollback Plan
1. [Step 1: e.g., Revert to previous git tag]
2. [Step 2: e.g., Restore database from backup]
3. [Step 3: e.g., Clear cache]

**Estimated Rollback Time**: [X minutes]

---

## Known Issues

### Critical
- **[PROJ-###]**: [Description of issue and impact]
  - **Workaround**: [If available]
  - **Fix ETA**: [Expected fix date]

### High Priority
- **[PROJ-###]**: [Description of issue]
  - **Workaround**: [If available]

---

## Performance Impact

### Metrics
- **Page Load Time**: [Before] → [After]
- **API Response Time**: [Before] → [After]
- **Database Query Time**: [Before] → [After]

### Resource Usage
- **Memory**: [Expected change]
- **CPU**: [Expected change]
- **Disk Space**: [Expected change]

---

## Security Notes

- [Any security-related changes or considerations]
- [New permissions or access controls]
- [Security vulnerabilities fixed]

---

## Documentation Updates

- [ ] [API documentation updated]
- [ ] [README updated]
- [ ] [Deployment guide updated]
- [ ] [User guide updated]

---

## Contributors

- [Name] ([GitHub handle]) - [Contribution]
- [Name] ([GitHub handle]) - [Contribution]

---

## Links

- **Release Branch**: [Link to branch]
- **Release Board**: [Link to Jira board]
- **Pull Requests**: [Link to list of PRs in this release]
- **CI/CD Pipeline**: [Link to build]

---
