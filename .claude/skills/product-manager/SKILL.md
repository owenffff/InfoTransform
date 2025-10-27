---
name: product-manager
description: Use this skill when documenting new features like a product manager. This skill should be used when the user requests product documentation, feature specifications, user stories, release notes, product roadmaps, or any PM-style documentation for new features and enhancements.
---

# Product Manager Documentation Skill

## Overview

Document new features, enhancements, and product changes with the rigor and clarity of a professional product manager. This skill guides you through creating comprehensive product documentation including feature specifications, user stories, acceptance criteria, release notes, and product roadmaps.

## When to Use This Skill

Invoke this skill when the user requests:
- "Document this new feature like a PM"
- "Create a product spec for the upload functionality"
- "Write user stories for the new AI analysis feature"
- "Generate release notes for the latest update"
- "Create a product roadmap for the next quarter"
- "Write acceptance criteria for this feature"
- Any request to document features in a product management style

## Core Workflow

Follow these steps when creating product documentation:

### Step 1: Understand the Feature Context

Before writing any documentation, gather essential information:

**Key Questions to Ask:**
1. **What problem does this solve?** - Understand the user pain point or business need
2. **Who is this for?** - Identify the target user personas
3. **What is the scope?** - Clarify what's included and what's not (MVP vs future enhancements)
4. **What are the success metrics?** - How will we measure if this feature succeeds?
5. **Are there dependencies?** - Technical, business, or cross-team dependencies
6. **What's the timeline?** - Release target and any phasing plans

**Reference Material**: See `assets/pm-best-practices/discovery-template.md` for a comprehensive discovery question framework.

### Step 2: Choose the Right Documentation Type

Select the appropriate documentation format based on the request:

| Documentation Type | When to Use | Template Location |
|-------------------|-------------|-------------------|
| **Feature Specification** | Detailed feature documentation for development | `assets/templates/feature-spec-template.md` |
| **User Stories** | Breaking down features into user-centric tasks | `assets/templates/user-stories-template.md` |
| **Release Notes** | Communicating changes to users | `assets/templates/release-notes-template.md` |
| **Product Requirements Document (PRD)** | Comprehensive feature planning document | `assets/templates/prd-template.md` |
| **Roadmap** | Strategic planning and timeline communication | `assets/templates/roadmap-template.md` |
| **Acceptance Criteria** | Defining "done" for a feature | `assets/templates/acceptance-criteria-template.md` |

### Step 3: Write Feature Specifications

When documenting a new feature, follow this structure:

**1. Feature Overview**
- **Feature Name**: Clear, user-facing name
- **Problem Statement**: What user problem does this solve?
- **Proposed Solution**: High-level description of the feature
- **Success Metrics**: How we'll measure success (KPIs, user adoption, etc.)

**2. User Personas & Use Cases**
- **Primary Users**: Who will use this feature most?
- **Secondary Users**: Who else might benefit?
- **Use Cases**: Real-world scenarios where users will use this feature

**3. Functional Requirements**
- **Must Have**: Core functionality required for MVP
- **Should Have**: Important but not critical for initial release
- **Could Have**: Nice-to-have enhancements
- **Won't Have**: Explicitly out of scope

**4. User Flow**
- Step-by-step description of how users will interact with the feature
- Consider edge cases and error states
- Include visual diagrams if helpful (ASCII or Mermaid diagrams)

**5. Technical Considerations**
- API endpoints or backend changes needed
- Frontend components or UI changes
- Performance requirements
- Security and privacy considerations
- Accessibility requirements

**6. Design Requirements**
- UI/UX specifications
- Visual design assets needed
- Responsive design considerations
- Accessibility standards (WCAG compliance)

**7. Testing & Validation**
- Unit test requirements
- Integration test scenarios
- User acceptance testing criteria
- Edge cases to test

**8. Release Plan**
- Phasing strategy (if applicable)
- Feature flags or gradual rollout
- Rollback plan
- Communication plan

**Reference**: See `assets/templates/feature-spec-template.md` for a complete template.

### Step 4: Write User Stories

Break down features into user stories using the standard format:

**Format:**
```
As a [user persona]
I want to [action]
So that [benefit]
```

**Good User Story Example:**
```
As a business analyst
I want to upload multiple invoice PDFs at once
So that I can extract data from a batch of invoices efficiently
```

**For Each User Story, Include:**
- **Story ID**: Unique identifier (e.g., `US-001`)
- **Priority**: Must Have / Should Have / Could Have / Won't Have (MoSCoW)
- **Story Points**: Effort estimate (1, 2, 3, 5, 8, 13, etc.)
- **Acceptance Criteria**: Specific, testable conditions for "done"
- **Dependencies**: Other stories or technical work required first
- **Notes**: Additional context, design links, technical details

**Acceptance Criteria Format (Given-When-Then):**
```
Given [initial context]
When [action is performed]
Then [expected outcome]
```

**Example:**
```
Given I am on the upload page
When I drag and drop 5 PDF files into the upload zone
Then all 5 files should appear in the file list with correct names and sizes
```

**Reference**: See `assets/templates/user-stories-template.md` for comprehensive examples.

### Step 5: Write Release Notes

When documenting a release, structure it for your audience:

**For External Users (Customer-Facing):**
- **What's New**: Highlight new features and improvements
- **Improvements**: Enhancements to existing features
- **Bug Fixes**: Issues resolved (user-facing language)
- **Known Issues**: Current limitations or known bugs

**For Internal Teams (Engineering/QA):**
- **New Features**: Detailed technical changes
- **API Changes**: Breaking or non-breaking API updates
- **Database Changes**: Schema migrations or data updates
- **Configuration Changes**: Environment variable or config updates
- **Deployment Notes**: Special deployment instructions
- **Rollback Procedures**: How to revert if needed

**Best Practices:**
- Use clear, user-friendly language (avoid jargon)
- Include screenshots or GIFs for visual features
- Link to relevant documentation
- Categorize changes by impact (major, minor, patch)
- Include dates and version numbers
- Thank contributors (if applicable)

**Reference**: See `assets/templates/release-notes-template.md` for examples.

### Step 6: Create Product Roadmaps

When planning future work, create a roadmap that communicates:

**Roadmap Structure:**

1. **Now (Current Quarter)**
   - Features currently in development
   - Expected release dates
   - Current status

2. **Next (Next Quarter)**
   - Planned features
   - Dependencies and prerequisites
   - Research or discovery work needed

3. **Later (Future)**
   - Ideas under consideration
   - Long-term strategic initiatives
   - Features pending customer validation

**For Each Roadmap Item, Include:**
- **Feature Name**: Clear, descriptive title
- **Problem/Opportunity**: Why we're building this
- **Target Users**: Who benefits
- **Success Metrics**: How we'll measure success
- **Estimated Effort**: T-shirt sizing (S, M, L, XL)
- **Dependencies**: Blockers or prerequisites
- **Status**: Discovery, In Development, Testing, Released

**Roadmap Communication Tips:**
- Be transparent about uncertainty (use "might", "considering")
- Avoid committing to specific dates too far in advance
- Explain prioritization criteria
- Update regularly and communicate changes

**Reference**: See `assets/templates/roadmap-template.md` for a complete template.

### Step 7: Define Acceptance Criteria

For any feature or user story, write clear acceptance criteria:

**Characteristics of Good Acceptance Criteria:**
- **Specific**: No ambiguity in what "done" means
- **Testable**: Can be verified through testing
- **Achievable**: Within scope and technically feasible
- **Relevant**: Directly related to the user story
- **Clear**: Understandable by all team members

**Format Options:**

**1. Given-When-Then (Behavior-Driven Development)**
```
Given [context/precondition]
When [action]
Then [expected result]
```

**2. Checklist Format**
```
- [ ] User can upload files via drag-and-drop
- [ ] User can upload files via file browser
- [ ] System validates file types (PDF, images, audio)
- [ ] System shows error for unsupported file types
- [ ] User sees file size for each uploaded file
```

**3. Scenario Format**
```
Scenario: User uploads a valid PDF file
- User drags a PDF file into the upload zone
- System validates the file type
- System displays the file in the upload list
- System shows file name, size, and type
- User can remove the file from the list
```

**Include Edge Cases:**
- What happens with invalid input?
- What are the system limits? (file size, count, etc.)
- What happens with slow connections or timeouts?
- How are errors communicated to users?

**Reference**: See `assets/templates/acceptance-criteria-template.md` for comprehensive examples.

## Common Documentation Patterns

### Feature Launch Documentation
1. Feature Specification (detailed technical and functional requirements)
2. User Stories (broken down into implementable units)
3. Acceptance Criteria (clear definition of done)
4. Release Notes (user-facing communication)

### Product Planning Documentation
1. Product Requirements Document (comprehensive feature planning)
2. User Stories (prioritized backlog)
3. Roadmap (strategic timeline)
4. Success Metrics (measurement plan)

### Bug Fix Documentation
1. Issue Description (what's broken)
2. Root Cause Analysis (why it's broken)
3. Solution Approach (how we'll fix it)
4. Testing Plan (validation strategy)
5. Release Notes (user communication)

### Enhancement Documentation
1. Current State (how it works now)
2. Desired State (how it should work)
3. User Impact (who benefits and how)
4. Implementation Plan (technical approach)
5. Success Metrics (measurement criteria)

## Product Management Best Practices

### Writing Principles
1. **User-Centric**: Always frame features from the user's perspective
2. **Clear and Concise**: Avoid jargon; use simple, direct language
3. **Data-Driven**: Include metrics, research, and evidence
4. **Actionable**: Make it clear what needs to be done
5. **Complete**: Anticipate questions and provide thorough answers

### Prioritization Frameworks

**MoSCoW Method**:
- **Must Have**: Critical for launch; without this, the feature fails
- **Should Have**: Important but not vital; can be deferred if needed
- **Could Have**: Nice to have; will improve UX but not essential
- **Won't Have**: Out of scope for this release; explicitly excluded

**RICE Scoring** (for roadmap prioritization):
- **Reach**: How many users will this impact?
- **Impact**: How much will it impact each user? (Massive=3, High=2, Medium=1, Low=0.5)
- **Confidence**: How confident are we in our estimates? (100%, 80%, 50%)
- **Effort**: How much work is required? (person-months)
- **Score**: (Reach × Impact × Confidence) / Effort

**Value vs Effort Matrix**:
- High Value, Low Effort: Quick wins (do first)
- High Value, High Effort: Major projects (strategic bets)
- Low Value, Low Effort: Fill-ins (do when available)
- Low Value, High Effort: Time sinks (avoid or defer)

**Reference**: See `assets/pm-best-practices/prioritization-frameworks.md` for detailed explanations and examples.

### Stakeholder Communication

**For Engineering Teams**:
- Provide clear technical requirements
- Include API specs, data models, edge cases
- Link to design mockups and user flows
- Be available for questions and clarifications

**For Design Teams**:
- Share user research and personas
- Provide context on user problems
- Define success metrics for design
- Collaborate on user flows and information architecture

**For Executive/Business Stakeholders**:
- Focus on business impact and ROI
- Highlight user value and market opportunity
- Include competitive analysis if relevant
- Provide clear timelines and resource requirements

**For End Users**:
- Use plain language (no technical jargon)
- Focus on benefits, not features
- Include visual examples (screenshots, videos)
- Provide clear instructions and support resources

**Reference**: See `assets/pm-best-practices/stakeholder-communication.md` for communication templates.

## Troubleshooting Common Issues

**Documentation feels too long or complex:**
- Break into smaller sections
- Use bullet points and tables for scanability
- Add a TL;DR summary at the top
- Create an appendix for detailed technical content

**Acceptance criteria are ambiguous:**
- Use Given-When-Then format for clarity
- Include specific examples
- Define edge cases explicitly
- Have engineers review and ask questions

**Stakeholders don't read the documentation:**
- Create an executive summary (1 page max)
- Use visuals (diagrams, mockups, flowcharts)
- Present the content in meetings, don't just share it
- Tailor the format to your audience

**Requirements keep changing:**
- Document assumptions and constraints upfront
- Use version control for documentation
- Track changes with a changelog
- Set clear "freeze" dates for scope

**Missing technical details:**
- Collaborate with engineering early
- Include technical review as part of the process
- Ask engineers to contribute sections
- Use technical templates as scaffolding

## Resources

### assets/templates/
- `feature-spec-template.md` - Complete feature specification template
- `user-stories-template.md` - User story writing guide with examples
- `release-notes-template.md` - Release notes templates for different audiences
- `prd-template.md` - Product Requirements Document template
- `roadmap-template.md` - Product roadmap template
- `acceptance-criteria-template.md` - Acceptance criteria writing guide

### assets/pm-best-practices/
- `discovery-template.md` - Feature discovery question framework
- `prioritization-frameworks.md` - Detailed prioritization methodologies
- `stakeholder-communication.md` - Communication templates for different audiences
- `user-research-guide.md` - User research and validation techniques
- `metrics-and-kpis.md` - Defining and tracking success metrics
- `competitive-analysis.md` - Framework for competitive research

### scripts/
- (Placeholder for future automation scripts, e.g., changelog generators, roadmap exporters)

## Additional Notes

- Always start with the "why" before diving into the "what" and "how"
- Validate assumptions with data, user research, or stakeholder input
- Keep documentation living and up-to-date; review and revise regularly
- Use consistent terminology across all documentation
- Link related documents together (roadmap → PRD → user stories → acceptance criteria)
- Consider your audience and adjust the level of detail accordingly
- Include dates and version numbers on all documents
- Make documentation searchable and accessible to all relevant team members

## Document Versioning

For all product documentation, include a version history table:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-10-21 | Your Name | Initial version |
| 1.1 | 2024-10-25 | Your Name | Added acceptance criteria section |

This helps track changes and understand the evolution of requirements over time.
