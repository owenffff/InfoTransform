# InfoTransform API Specification & UI Requirements

## Overview

InfoTransform is an AI-powered document processing application that transforms various file types (images, PDFs, documents, audio) into structured data. This document provides comprehensive specifications for building a modern UI that interfaces with the backend API.

## Core Functionality

The application performs the following key operations:
1. **File Upload**: Accepts multiple files including images, PDFs, documents, audio files, and ZIP archives
2. **AI Analysis**: Processes files through customizable AI models to extract structured data
3. **Real-time Progress**: Provides streaming updates during processing
4. **Data Export**: Allows users to download results in Excel or CSV format

## API Endpoints

### 1. GET `/`
- **Purpose**: Serves the main web interface
- **Response**: HTML page
- **Current Implementation**: Jinja2 template

### 2. GET `/api/models`
- **Purpose**: Retrieve available analysis models and AI models
- **Response Format**:
```json
{
  "models": {
    "content_compliance": {
      "name": "Content Compliance",
      "description": "Content compliance analysis for policy violations",
      "fields": {
        "is_violating": {
          "type": "boolean",
          "description": "Whether content violates policies",
          "required": true
        },
        "category": {
          "type": "string",
          "description": "Violation category if applicable",
          "required": false,
          "enum": ["violence", "sexual", "self_harm"]
        },
        "explanation_if_violating": {
          "type": "string",
          "description": "Explanation of violation",
          "required": false
        }
      }
    },
    "document_metadata": {
      "name": "Document Metadata",
      "description": "Document metadata extraction",
      "fields": {
        "title": {"type": "string", "required": true},
        "author": {"type": "string", "required": false},
        "summary": {"type": "string", "required": true},
        "word_count": {"type": "integer", "required": true},
        "key_topics": {"type": "array", "required": true}
      }
    },
    "technical_analysis": {
      "name": "Technical Documentation Analysis",
      "description": "Technical documentation analysis",
      "fields": {
        "programming_languages": {"type": "array", "required": true},
        "code_snippets_count": {"type": "integer", "required": true},
        "has_installation_guide": {"type": "boolean", "required": true},
        "has_api_reference": {"type": "boolean", "required": true},
        "complexity_level": {"type": "string", "required": true},
        "external_links_count": {"type": "integer", "required": true}
      }
    }
  },
  "ai_models": {
    "models": {
      "gpt-4o-mini": {
        "display_name": "GPT-4 Optimized Mini",
        "max_tokens": 16384
      },
      "gpt-4o": {
        "display_name": "GPT-4 Optimized",
        "max_tokens": 128000
      }
    }
  }
}
```

### 3. POST `/api/transform` (Main Processing Endpoint)
- **Purpose**: Process files and extract structured data
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - `files`: Multiple file uploads (required)
  - `model_key`: Selected analysis model key (required)
  - `custom_instructions`: Additional user instructions (optional)
  - `ai_model`: Override default AI model (optional)
- **Response**: Server-Sent Events (SSE) stream
- **Supported File Types**:
  - Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
  - Documents: `.pdf`, `.docx`, `.pptx`, `.xlsx`, `.md`, `.txt`
  - Audio: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.webm`
  - Archives: `.zip`

### 4. POST `/api/download-results`
- **Purpose**: Download processing results as Excel file
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "results": {
    "results": [/* array of processed results */],
    "summary": {/* optional summary data */}
  },
  "format": "excel"
}
```
- **Response**: Binary Excel file stream

### 5. GET `/health`
- **Purpose**: Health check endpoint
- **Response**:
```json
{
  "status": "healthy",
  "processors_initialized": true,
  "server": "FastAPI",
  "version": "2.0.0"
}
```

## Server-Sent Events (SSE) Format

The `/api/transform` endpoint uses SSE for real-time updates. Each event follows this format:
```
data: {JSON_OBJECT}\n\n
```

### Event Types

#### 1. `init` Event
Sent at the start of processing:
```json
{
  "type": "init",
  "total_files": 5,
  "model_key": "document_metadata",
  "model_name": "Document Metadata",
  "model_fields": ["title", "author", "summary", "word_count", "key_topics"],
  "ai_model": "gpt-4o-mini",
  "optimization": {
    "parallel_conversion": true,
    "batch_processing": true,
    "max_workers": 4,
    "batch_size": 5
  }
}
```

#### 2. `phase` Event
Indicates processing phase transitions:
```json
{
  "type": "phase",
  "phase": "markdown_conversion",  // or "summarization", "ai_processing"
  "status": "started",  // or "completed"
  "duration": 2.45,  // seconds (only in completed events)
  "files_per_second": 2.04  // (only in completed events)
}
```

#### 3. `conversion_progress` Event
Real-time progress during file conversion:
```json
{
  "type": "conversion_progress",
  "phase": 1,
  "phase_name": "Converting documents",
  "current": 3,
  "total": 5,
  "filename": "document.pdf",
  "success": true,
  "files_per_second": 1.5
}
```

#### 4. `conversion_summary` Event
Summary after conversion phase:
```json
{
  "type": "conversion_summary",
  "successful": 4,
  "failed": 1,
  "failed_files": ["protected.pdf"],
  "password_required": ["protected.pdf"]
}
```

#### 5. `partial` Event
Partial results during AI processing (for progressive updates):
```json
{
  "type": "partial",
  "filename": "document.pdf",
  "status": "success",
  "structured_data": {
    "title": "Sample Document",
    "author": null,  // Fields may be null while processing
    // ... other fields
  },
  "model_fields": ["title", "author", "summary"],
  "processing_time": 0.5
}
```

#### 6. `result` Event
Final result for each file:
```json
{
  "type": "result",
  "filename": "document.pdf",
  "status": "success",  // or "error"
  "markdown_content": "# Document content...",
  "structured_data": {
    "title": "Sample Document",
    "author": "John Doe",
    "summary": "This document discusses...",
    "word_count": 1500,
    "key_topics": ["AI", "Machine Learning", "Data Processing"]
  },
  "model_fields": ["title", "author", "summary", "word_count", "key_topics"],
  "processing_time": 2.3,
  "was_summarized": false,
  "summarization_metrics": null,
  "progress": {
    "phase": 2,
    "phase_name": "Analyzing with AI",
    "current": 3,
    "total": 5,
    "successful": 2,
    "failed": 1
  }
}
```

For error results:
```json
{
  "type": "result",
  "filename": "corrupted.pdf",
  "status": "error",
  "error": "Failed to process PDF: File appears to be corrupted",
  "error_type": "password_required",  // Optional, for specific error types
  "progress": {
    "current": 4,
    "total": 5,
    "successful": 3,
    "failed": 1
  }
}
```

#### 7. `complete` Event
Final summary of all processing:
```json
{
  "type": "complete",
  "total_files": 5,
  "successful": 4,
  "failed": 1,
  "model_used": "document_metadata",
  "ai_model_used": "gpt-4o-mini",
  "summarization": {
    "files_summarized": 2,
    "summarization_duration": 1.5,
    "token_threshold": 16000,
    "summary_model": "gpt-4o-mini"
  },
  "performance": {
    "total_duration": 15.6,
    "conversion_duration": 3.2,
    "summarization_duration": 1.5,
    "ai_duration": 10.9,
    "files_per_second": 0.32,
    "conversion_metrics": {
      "total_processed": 5,
      "total_time": 3.2,
      "average_time": 0.64
    },
    "batch_metrics": {
      "total_batches": 1,
      "total_items": 5,
      "average_batch_time": 10.9
    }
  }
}
```

## Required UI Features

### 1. File Upload Interface
- **Drag & Drop Zone**: Large, interactive area for file dropping
- **File Selection**: Traditional file picker as alternative
- **Multi-file Support**: Handle multiple files at once
- **File Preview**: Show selected files before processing
  - File name
  - File size
  - File type icon
  - Remove button for each file
- **Supported Types Indicator**: Clear display of accepted formats
- **File Validation**: Client-side validation before upload

### 2. Configuration Panel
- **Model Selection**:
  - Dropdown/select for analysis models
  - Display model description on selection
  - Show schema preview with field information
- **AI Model Selection**:
  - Dropdown for available AI models
  - Show model capabilities (token limits)
- **Custom Instructions**:
  - Text area for additional user instructions
  - Character/word counter
  - Examples or placeholders

### 3. Schema Preview
- **Field Display**: Visual representation of expected output fields
- **Field Properties**:
  - Field name
  - Data type (string, boolean, array, etc.)
  - Required/optional indicator
  - Description tooltip
- **Interactive Elements**: Hover for more details

### 4. Processing Status
- **Multi-phase Progress**:
  - Phase 1: Document Conversion (blue progress bar)
  - Phase 2: AI Analysis (green progress bar)
  - Optional: Summarization phase indicator
- **Real-time Updates**:
  - Current file being processed
  - Files completed vs total
  - Processing speed (files/second)
  - Time elapsed
- **Phase Badges**: Visual indicators for current phase
- **Loading States**: Skeleton screens or spinners

### 5. Results Display

#### Table View
- **Features**:
  - Sortable columns
  - Searchable content
  - Inline editing capabilities
  - Row selection
  - Pagination for large datasets
- **Cell Types**:
  - Text cells
  - Boolean cells (Yes/No with visual indicators)
  - Array cells (tags or chips)
  - Long text with expand/collapse
- **Edit Tracking**:
  - Visual indication of edited cells
  - Undo/redo functionality
  - Clear all edits button

#### Card View
- **Features**:
  - One card per processed file
  - Expandable sections for long content
  - Field-value pairs
  - Status indicators (success/error)
- **Error Cards**:
  - Clear error message
  - Error type icon
  - Retry option (if applicable)

### 6. Export Controls
- **Format Selection**:
  - Excel (.xlsx) - server-side generation
  - CSV (.csv) - client-side generation
- **Download Button**: Prominent call-to-action
- **Include Edits**: Edited values included in export

### 7. Error Handling
- **Error Types**:
  - Password-protected files
  - Unsupported formats
  - Corrupted files
  - Network errors
  - Processing timeouts
- **User Feedback**:
  - Toast notifications for quick messages
  - Error alerts for critical issues
  - Inline error messages
- **Recovery Options**:
  - Retry failed files
  - Skip and continue
  - Download partial results

### 8. Summary Statistics
Display for multi-file processing:
- Total files processed
- Success count
- Failure count
- Processing duration
- Average time per file

## User Interaction Flows

### Primary Flow
1. User uploads files (drag & drop or browse)
2. System shows file preview
3. User selects analysis model
4. User optionally adds custom instructions
5. User clicks "Transform" button
6. System shows real-time progress
7. Results appear progressively as files complete
8. User can edit results inline
9. User downloads final results

### Error Recovery Flow
1. System encounters error during processing
2. Error notification appears
3. Failed files are marked clearly
4. User can:
   - Retry failed files only
   - Continue with successful files
   - Adjust settings and retry all

## Performance Considerations

### Optimizations Implemented
- **Parallel Processing**: Multiple files converted simultaneously
- **Batch AI Processing**: Groups files for efficient API calls
- **Streaming Results**: Progressive display as files complete
- **Automatic Summarization**: Long documents summarized before analysis

### UI Performance Requirements
- **Responsive Updates**: No UI freezing during processing
- **Progressive Rendering**: Show results as they arrive
- **Efficient Re-renders**: Only update changed elements
- **Virtual Scrolling**: For large result sets
- **Debounced Search**: Prevent excessive filtering operations

## Brand Guidelines

### Color Palette (Per color_guideline.md)
```css
/* Core Brand Colors */
--brand-orange: #FD5108;      /* Primary - use sparingly for CTAs and progress */
--white: #FFFFFF;              /* Primary background */
--black: #000000;              /* Text only */

/* Orange Tints (limited use) */
--orange-400: #FE7C39;         /* Data viz only */
--orange-300: #FFAA72;         /* Data viz only */
--orange-200: #FFCDA8;         /* Backgrounds & data viz */
--orange-100: #FFE8D4;         /* Backgrounds & data viz */

/* Grey Tints */
--grey-500: #A1A8B3;           /* Data viz only */
--grey-400: #B5BCC4;           /* Data viz only */
--grey-300: #CBD1D6;           /* Data viz only */
--grey-200: #DFE3E6;           /* Backgrounds & borders */
--grey-100: #EEEFF1;           /* Backgrounds */
```

### Design Principles
1. **Lead with Orange**: Use orange purposefully as accent, never as full backgrounds
2. **White Space**: Generous use of white for clean, professional look
3. **Minimal Colors**: Avoid using multiple colors together
4. **Black Text**: All text should be black on white backgrounds
5. **No Custom Gradients**: Only use approved gradients if needed

## Technical Requirements

### Browser Support
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

### Responsive Design
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- Proper ARIA labels
- Focus indicators

### Framework Recommendations
- **Modern Options**:
  - Next.js with TypeScript
  - React with Vite
  - Vue 3
- **UI Libraries**:
  - shadcn/ui (recommended)
  - Tailwind CSS
  - Radix UI primitives
- **State Management**:
  - Zustand or Redux Toolkit
  - TanStack Query for API calls
- **Real-time Updates**:
  - Native EventSource API for SSE
  - React/Vue hooks for SSE handling

## Security Considerations

1. **File Validation**: Client-side file type and size validation
2. **CORS**: Properly configured for production domains
3. **Error Messages**: Don't expose sensitive server information
4. **Rate Limiting**: Implement client-side throttling for API calls
5. **Secure File Handling**: Don't expose file paths in UI

## Example API Integration

### Fetching Models
```javascript
const response = await fetch('/api/models');
const { models, ai_models } = await response.json();
```

### Processing Files with SSE
```javascript
const formData = new FormData();
files.forEach(file => formData.append('files', file));
formData.append('model_key', 'document_metadata');
formData.append('custom_instructions', 'Focus on technical details');

const response = await fetch('/api/transform', {
  method: 'POST',
  body: formData
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      handleEvent(event);
    }
  }
}
```

## Next Steps for UI Development

1. **Setup**: Initialize project with chosen framework
2. **Components**: Build reusable component library
3. **API Client**: Create service layer for API communication
4. **SSE Handler**: Implement robust SSE event handling
5. **State Management**: Setup global state for app data
6. **Styling**: Implement design system following brand guidelines
7. **Testing**: Unit and integration tests for critical paths
8. **Optimization**: Performance profiling and optimization
9. **Deployment**: Production build configuration

---

This specification provides all necessary information to build a modern, production-ready UI for the InfoTransform API. The UI should prioritize user experience, real-time feedback, and strict adherence to brand guidelines while leveraging the full capabilities of the streaming API.