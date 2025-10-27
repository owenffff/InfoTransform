# Feature Discovery Template

Use this template to gather comprehensive information before designing and building a new feature.

---

## 1. Problem Discovery

### What problem are we solving?

**Problem Statement** (1-2 sentences):
[Clearly articulate the user problem or business opportunity]

**How do we know this is a problem?**
- [ ] User research/interviews (specify number and source)
- [ ] Support tickets (specify number and timeframe)
- [ ] Usage analytics (specify data points)
- [ ] Sales feedback (specify source)
- [ ] Competitive pressure (specify competitors)
- [ ] Other: ___________

**Data Points**:
- [Quantitative data 1: e.g., "78% of users upload more than 10 files per session"]
- [Quantitative data 2]
- [Qualitative insight 1: e.g., "Users describe upload as 'tedious' and 'time-consuming'"]
- [Qualitative insight 2]

### How big is the problem?

**Impact Scale**:
- Number of users affected: ___________
- Frequency of occurrence: [Daily / Weekly / Monthly / Rarely]
- Severity: [Critical / High / Medium / Low]
- Workarounds available?: [Yes / No] - If yes, describe: ___________

**User Quotes** (if available):
> "[Direct quote from user describing the problem]"

> "[Another user quote]"

---

## 2. User Discovery

### Who has this problem?

**Primary User Persona**:
- **Name/Title**: [e.g., "Sarah the Business Analyst"]
- **Industry**: ___________
- **Company Size**: ___________
- **Role Responsibilities**: ___________
- **Goals**: ___________
- **Frustrations**: ___________
- **Tools They Use**: ___________
- **Tech Savviness**: [Low / Medium / High]

**Secondary User Personas** (if applicable):
[Repeat structure for additional personas]

### What are they trying to accomplish?

**User Goals**:
1. [Primary goal]
2. [Secondary goal]
3. [Additional goal]

**Current Workflow**:
[Describe step-by-step how users currently accomplish this goal]

1. Step 1
2. Step 2
3. Step 3...

**Pain Points in Current Workflow**:
- [Pain point 1]
- [Pain point 2]
- [Pain point 3]

**Desired Workflow**:
[Describe ideal workflow from user's perspective]

1. Step 1
2. Step 2
3. Step 3...

---

## 3. Solution Discovery

### What are potential solutions?

**Solution Option 1**: [Name/Description]
- **Pros**:
  - [Pro 1]
  - [Pro 2]
- **Cons**:
  - [Con 1]
  - [Con 2]
- **Estimated Effort**: [S / M / L / XL]
- **User Impact**: [Low / Medium / High]

**Solution Option 2**: [Name/Description]
- **Pros**:
- **Cons**:
- **Estimated Effort**:
- **User Impact**:

**Solution Option 3**: [Name/Description]
[Repeat structure]

**Recommended Solution**: [Which option and why?]

[Justification for recommendation]

### What's the MVP (Minimum Viable Product)?

**Must Have** (Cannot launch without):
- [ ] [Requirement 1]
- [ ] [Requirement 2]
- [ ] [Requirement 3]

**Should Have** (Important but can defer):
- [ ] [Requirement 1]
- [ ] [Requirement 2]

**Could Have** (Nice to have):
- [ ] [Requirement 1]
- [ ] [Requirement 2]

**Won't Have** (Explicitly out of scope):
- [ ] [Requirement 1]
- [ ] [Requirement 2]

---

## 4. Market & Competitive Discovery

### How do competitors solve this?

**Competitor 1**: [Name]
- **Their Solution**: [Brief description]
- **Strengths**: [What they do well]
- **Weaknesses**: [What they don't do well]
- **Differentiation Opportunity**: [How we can do better]

**Competitor 2**: [Name]
[Repeat structure]

**Market Standards**:
- What do users expect based on other tools?
- Are there industry best practices we should follow?

---

## 5. Success Discovery

### How will we know if this succeeds?

**Success Metrics** (Quantitative):

| Metric | Baseline | Target | Timeline | Measurement Method |
|--------|----------|--------|----------|-------------------|
| [Metric 1] | [Current] | [Goal] | [When] | [How measured] |
| [Metric 2] | [Current] | [Goal] | [When] | [How measured] |
| [Metric 3] | [Current] | [Goal] | [When] | [How measured] |

**Success Indicators** (Qualitative):
- [ ] [Indicator 1: e.g., "Users describe upload as 'fast' and 'easy'"]
- [ ] [Indicator 2: e.g., "Support tickets about upload decrease"]
- [ ] [Indicator 3]

**Leading Indicators** (Early signs of success):
- [What we can measure in first week]
- [What we can measure in first month]

**Lagging Indicators** (Long-term success):
- [What we measure after 3 months]
- [What we measure after 6 months]

### What would failure look like?

**Failure Signals**:
- [ ] [Signal 1: e.g., "Less than 30% adoption after 2 months"]
- [ ] [Signal 2: e.g., "User satisfaction doesn't improve"]
- [ ] [Signal 3: e.g., "Increase in support tickets about new feature"]

**Contingency Plan**:
[What we'll do if the feature doesn't succeed]

---

## 6. Technical Discovery

### What are the technical considerations?

**Technical Feasibility**:
- [ ] Is this technically possible with our current stack? [Yes / No / Unknown]
- [ ] Are there third-party dependencies? [List if yes]
- [ ] Are there performance concerns? [Describe if yes]
- [ ] Are there security/privacy concerns? [Describe if yes]

**Architecture Questions**:
- [ ] Frontend changes required: [High-level description]
- [ ] Backend changes required: [High-level description]
- [ ] Database changes required: [Yes / No - describe if yes]
- [ ] Infrastructure changes required: [Yes / No - describe if yes]

**Technical Risks**:
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| [Risk 1] | High/Med/Low | High/Med/Low | [How to address] |
| [Risk 2] | High/Med/Low | High/Med/Low | [How to address] |

**Technical Unknowns**:
- [ ] [Unknown 1: e.g., "Can backend handle 50 parallel uploads?"]
- [ ] [Unknown 2: e.g., "What's the storage cost for 100GB of files?"]
- [ ] [Unknown 3]

**Spike/POC Needed?**:
- [ ] Yes - [What needs to be prototyped/tested]
- [ ] No - We have sufficient information

---

## 7. Resource Discovery

### What resources do we need?

**Team Requirements**:
- **Product Manager**: [Time allocation: e.g., "50% for 6 weeks"]
- **Engineering**:
  - Frontend: [Number of engineers × time]
  - Backend: [Number of engineers × time]
- **Design**: [Time allocation]
- **QA**: [Time allocation]
- **Other**: [DevOps, Data, etc.]

**Estimated Effort**:
- **Discovery**: [Time: e.g., "2 weeks"]
- **Design**: [Time]
- **Development**: [Time]
- **Testing**: [Time]
- **Total**: [Time]

**Budget Requirements**:
- **Engineering Cost**: [Estimate]
- **Third-party Services**: [If applicable]
- **Infrastructure**: [Additional costs]
- **Total**: [Estimate]

---

## 8. Dependencies Discovery

### What needs to happen first?

**Internal Dependencies**:
- [ ] [Dependency 1: e.g., "Backend API must support multipart upload"]
  - **Owner**: [Team/Person]
  - **Status**: [Not Started / In Progress / Complete]
  - **Due Date**: [Date]
  - **Blocker?**: [Yes / No]

- [ ] [Dependency 2]
  [Repeat structure]

**External Dependencies**:
- [ ] [Dependency 1: e.g., "Third-party API approval"]
  - **Vendor**: [Name]
  - **Status**: [Status]
  - **Expected Resolution**: [Date]

---

## 9. Risk Discovery

### What could go wrong?

**Product Risks**:
| Risk | Impact | Likelihood | Mitigation | Owner |
|------|--------|------------|------------|-------|
| [Risk 1: e.g., "Users don't adopt the feature"] | High/Med/Low | High/Med/Low | [User testing, phased rollout] | [Name] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Mitigation plan] | [Name] |

**Technical Risks**:
| Risk | Impact | Likelihood | Mitigation | Owner |
|------|--------|------------|------------|-------|
| [Risk 1: e.g., "Performance degrades with 50 files"] | High | Med | [Load testing before launch] | [Name] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Mitigation plan] | [Name] |

**Business Risks**:
| Risk | Impact | Likelihood | Mitigation | Owner |
|------|--------|------------|------------|-------|
| [Risk 1: e.g., "Competitor launches similar feature first"] | Med | Low | [Accelerate timeline] | [Name] |
| [Risk 2] | High/Med/Low | High/Med/Low | [Mitigation plan] | [Name] |

---

## 10. Timeline Discovery

### When can/should this ship?

**Key Milestones**:
| Milestone | Target Date | Status |
|-----------|-------------|--------|
| Discovery Complete | [Date] | [Not Started / In Progress / Done] |
| Design Complete | [Date] | [Status] |
| Dev Complete | [Date] | [Status] |
| Testing Complete | [Date] | [Status] |
| Beta Launch | [Date] | [Status] |
| GA Launch | [Date] | [Status] |

**Timeline Constraints**:
- [ ] Hard deadline: [Date and reason, if applicable]
- [ ] Soft deadline: [Date and reason]
- [ ] No specific deadline

**Phasing Strategy**:
- **Phase 1** ([Date]): [What's included]
- **Phase 2** ([Date]): [What's included]
- **Phase 3** ([Date]): [What's included]

---

## 11. Open Questions

### What do we still need to figure out?

**Product Questions**:
- [ ] [Question 1: e.g., "Should we support folder upload or just files?"]
  - **Need answer by**: [Date]
  - **How to resolve**: [User research, stakeholder decision, etc.]

- [ ] [Question 2]
  [Repeat structure]

**Design Questions**:
- [ ] [Question 1: e.g., "Where should progress bar appear?"]
  - **Need answer by**: [Date]
  - **How to resolve**: [User testing, A/B test, etc.]

**Technical Questions**:
- [ ] [Question 1: e.g., "What's the optimal batch size for API calls?"]
  - **Need answer by**: [Date]
  - **How to resolve**: [Performance testing, spike]

**Business Questions**:
- [ ] [Question 1: e.g., "Is this a free or paid feature?"]
  - **Need answer by**: [Date]
  - **How to resolve**: [Leadership decision]

---

## 12. Decision Log

### What decisions have we made?

| Decision | Made By | Date | Rationale |
|----------|---------|------|-----------|
| [Decision 1] | [Name/Role] | [Date] | [Why this decision] |
| [Decision 2] | [Name/Role] | [Date] | [Why this decision] |

---

## 13. Next Steps

### What happens now?

**Immediate Next Steps**:
1. [ ] [Action 1: e.g., "Schedule user interviews with 5 power users"]
   - **Owner**: [Name]
   - **Due Date**: [Date]

2. [ ] [Action 2: e.g., "Create wireframes for 3 solution options"]
   - **Owner**: [Name]
   - **Due Date**: [Date]

3. [ ] [Action 3]
   [Repeat structure]

**Go/No-Go Decision**:
- **Decision Date**: [When we decide whether to proceed]
- **Decision Makers**: [Who makes the decision]
- **Criteria for "Go"**: [What needs to be true to proceed]

---

## Completed Example: Bulk File Upload Discovery

### 1. Problem Discovery

**Problem Statement**:
Users can only upload one file at a time, which is inefficient for business analysts who need to process 20-50 documents daily.

**How do we know this is a problem?**
- ✅ User research: 15 user interviews
- ✅ Support tickets: 45 tickets in Q3 requesting bulk upload
- ✅ Usage analytics: 78% of sessions involve 10+ file uploads
- ✅ Sales feedback: Lost 2 deals to competitors with bulk upload

**Data Points**:
- 78% of users upload 10+ files per session (analytics, last 90 days)
- Average session time: 12 minutes (8 minutes of which is just uploading)
- User satisfaction with upload: 6.5/10 (user survey, n=120)
- 3 of top 5 competitors have bulk upload functionality

### 2. User Discovery

**Primary User Persona: Sarah the Business Analyst**
- **Industry**: Accounting/Finance
- **Company Size**: 50-500 employees
- **Role**: Processes vendor invoices, creates monthly reports
- **Goals**: Extract invoice data accurately and quickly for reporting
- **Frustrations**: Repetitive file uploading, context switching between email/filesystem
- **Tools**: Excel, email, accounting software
- **Tech Savviness**: Medium

**Current Workflow**:
1. Receives 40 vendor invoices via email at month-end
2. Downloads each PDF from email to Downloads folder
3. Opens InfoTransform
4. For each of 40 files:
   - Clicks "Upload"
   - Navigates to Downloads folder
   - Selects one file
   - Waits for upload
   - Waits for processing
   - Copies result to Excel
5. Takes 90 minutes total

**Pain Points**:
- Clicking "Upload" 40 times is tedious
- Losing track of which files are processed
- Context switching between folders and browser
- Can't do other work while waiting for sequential uploads

**Desired Workflow**:
1. Downloads all 40 PDFs to a folder
2. Opens InfoTransform
3. Drags entire folder into upload zone
4. Selects model once
5. Clicks "Process All"
6. Reviews progress in real-time
7. Exports all results to Excel at once
8. Takes 20 minutes total

### 3. Solution Discovery

**Recommended Solution**: Drag-and-drop bulk upload with parallel processing

**MVP Must Have**:
- [ ] Drag-and-drop 2-50 files at once
- [ ] File validation (type, size)
- [ ] File list showing name, size, type
- [ ] Remove individual files before processing
- [ ] Process all files with one click

**Should Have** (defer if needed):
- [ ] Folder upload (extract and add all files)
- [ ] Retry failed files individually
- [ ] Save/load file sets for recurring workflows

**Won't Have** (explicitly out of scope):
- Cloud storage integration (Google Drive, Dropbox)
- Scheduled/automated processing

### Success Metrics

| Metric | Baseline | Target | Timeline | Measurement |
|--------|----------|--------|----------|-------------|
| Bulk upload adoption | 0% | 70% | 2 months | % of users who upload 2+ files |
| Avg session time | 12 min | 5 min | 2 months | Analytics: time from upload to export |
| User satisfaction | 6.5/10 | 8.5/10 | 1 month post-launch | Post-feature survey |
| Support tickets | 15/month | 3/month | 3 months | Ticket volume about uploads |

**Failure Signals**:
- Less than 30% adoption after 2 months
- User satisfaction doesn't improve to 7.5+
- Increase in support tickets or bug reports

---

## Document Info

**Last Updated**: [Date]
**Owner**: [Product Manager Name]
**Status**: [In Progress / Complete / Archived]
**Related Documents**:
- [Link to PRD]
- [Link to user research findings]
- [Link to technical spike]
