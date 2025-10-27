# Prioritization Frameworks for Product Managers

## Overview

This document provides practical frameworks for prioritizing features, enhancements, and bug fixes. Use these methods to make data-driven decisions about what to build and when.

---

## 1. MoSCoW Method

### What It Is
A simple prioritization technique that categorizes requirements into four buckets.

### When to Use
- Sprint planning
- MVP scoping
- Feature specification
- Stakeholder alignment

### The Four Categories

#### Must Have
**Definition**: Critical for launch; without this, the feature/product fails to function or deliver value.

**Criteria**:
- Legal/regulatory requirement
- Core functionality without which product doesn't work
- Fundamental user need that if unmet, users abandon product

**Examples**:
- User authentication (for an app requiring accounts)
- File upload capability (for a document processing tool)
- Payment processing (for an e-commerce site)

#### Should Have
**Definition**: Important but not vital; can be deferred if necessary, but causes pain or reduced value.

**Criteria**:
- Significantly improves user experience
- Addresses known pain point
- Competitive parity feature

**Examples**:
- Real-time progress updates (users can still use product without it)
- Bulk operations (users can do one-by-one as workaround)
- Export to multiple formats (if one format already exists)

#### Could Have
**Definition**: Nice to have; improves experience but has small impact; can be cut without much consequence.

**Criteria**:
- Small improvement to existing feature
- Aesthetic or convenience enhancement
- Low impact on adoption or retention

**Examples**:
- Dark mode
- Keyboard shortcuts
- Custom themes or branding

#### Won't Have (This Time)
**Definition**: Explicitly out of scope for this release; may reconsider in future.

**Criteria**:
- Not aligned with current goals
- Too much effort for too little benefit
- Dependencies not ready

**Examples**:
- Mobile app (if desktop is the priority)
- AI features (if infrastructure isn't ready)
- Advanced admin features (if targeting end users first)

### How to Use MoSCoW

1. **List all potential requirements** for the feature/project
2. **For each requirement, ask**:
   - Can we launch without this? (If no → Must Have)
   - Would users be significantly worse off without this? (If yes → Should Have)
   - Would users notice if it's missing? (If no → Could Have)
   - Is this aligned with current goals? (If no → Won't Have)
3. **Validate with stakeholders**: Engineering (feasibility), Design (user impact), Business (value)
4. **Iterate**: Move items between categories as you learn more

### Example: Bulk File Upload Feature

**Must Have**:
- Drag-and-drop multiple files
- File validation (type, size limits)
- Display uploaded files in list
- Process all files with one action

**Should Have**:
- Real-time progress for each file
- Retry failed files individually
- Remove files before processing

**Could Have**:
- Folder upload support
- Save file sets for reuse
- Keyboard shortcuts for file operations

**Won't Have**:
- Cloud storage integration (Google Drive, Dropbox)
- Scheduled/automated processing
- Mobile app support

---

## 2. RICE Scoring

### What It Is
A quantitative framework that scores features based on Reach, Impact, Confidence, and Effort.

### When to Use
- Roadmap planning
- Comparing multiple feature candidates
- Justifying prioritization decisions
- Resource allocation

### The Formula

**RICE Score = (Reach × Impact × Confidence) / Effort**

Higher score = higher priority

### The Four Factors

#### Reach
**Definition**: How many users will this affect in a given time period?

**How to measure**:
- Number of users per month/quarter
- Percentage of user base
- Number of transactions/sessions

**Examples**:
- Feature affects all users → Reach = 10,000 (total users)
- Feature affects 30% of users → Reach = 3,000
- Feature used 5 times per user per month → Reach = 50,000 (events)

#### Impact
**Definition**: How much will this affect each user?

**Scale**:
- **3 = Massive Impact** (transforms how they use product)
- **2 = High Impact** (significantly improves experience)
- **1 = Medium Impact** (noticeable improvement)
- **0.5 = Low Impact** (small improvement)
- **0.25 = Minimal Impact** (barely noticeable)

**Examples**:
- 3: Bulk upload for users who process 50 files daily
- 2: Real-time progress so users know what's happening
- 1: Export to additional file format
- 0.5: Dark mode for occasional users
- 0.25: New icon set

#### Confidence
**Definition**: How confident are you in your Reach and Impact estimates?

**Scale**:
- **100% = High Confidence** (strong data, validated with users)
- **80% = Medium Confidence** (some data, reasonable assumptions)
- **50% = Low Confidence** (gut feel, minimal data)

**Examples**:
- 100%: Analytics show 78% of users upload 10+ files (strong data)
- 80%: User interviews suggest they'd use this feature (qualitative validation)
- 50%: We think users might want this (hypothesis, not validated)

#### Effort
**Definition**: How much time will this take to build? (person-months)

**Estimation**:
- Include: PM time, engineering time, design time, QA time
- Express in person-months (e.g., 2 engineers × 3 weeks = 1.5 person-months)

**Examples**:
- 0.5 = 2 weeks for one engineer
- 1 = 1 month for one engineer
- 4 = 2 engineers for 2 months
- 12 = 3 engineers for 4 months

### How to Use RICE

1. **List all feature candidates**
2. **For each feature, estimate**:
   - Reach: [Number of users/events per time period]
   - Impact: [3, 2, 1, 0.5, or 0.25]
   - Confidence: [100%, 80%, or 50%]
   - Effort: [Person-months]
3. **Calculate RICE score** for each feature
4. **Sort by score** (highest = highest priority)
5. **Validate and adjust**: Does this feel right? What did we miss?

### Example Comparison

| Feature | Reach | Impact | Confidence | Effort | RICE Score |
|---------|-------|--------|------------|--------|------------|
| Bulk Upload | 1,000 users | 3 | 80% | 1 month | 2,400 |
| API Access | 200 users | 2 | 60% | 2 months | 120 |
| Dark Mode | 800 users | 0.5 | 80% | 0.5 months | 640 |
| Mobile App | 500 users | 2 | 50% | 6 months | 83 |

**Priority Order**: Bulk Upload (2,400) → Dark Mode (640) → API Access (120) → Mobile App (83)

---

## 3. Value vs. Effort Matrix (2x2)

### What It Is
A visual framework that plots features on a grid based on user value and implementation effort.

### When to Use
- Quick prioritization with stakeholders
- Workshop or brainstorming sessions
- Communicating priorities visually
- Identifying quick wins

### The Four Quadrants

```
                High Value
                    |
    Major Projects  |  Quick Wins
    (Do Strategically) | (Do First)
         High       |      Low
         Effort     |     Effort
  ─────────────────────────────────
         High       |      Low
         Effort     |     Effort
    Time Sinks      |  Fill-Ins
    (Avoid/Defer)   | (Do When Available)
                    |
                Low Value
```

#### Quick Wins (High Value, Low Effort)
**Priority**: Do first
**Examples**: Bug fixes, small UX improvements, simple feature additions

#### Major Projects (High Value, High Effort)
**Priority**: Strategic bets
**Examples**: New product lines, major features, platform migrations

#### Fill-Ins (Low Value, Low Effort)
**Priority**: Do when available
**Examples**: Polish, minor improvements, nice-to-haves

#### Time Sinks (Low Value, High Effort)
**Priority**: Avoid or defer
**Examples**: Over-engineered solutions, niche requests, nice-to-haves with big scope

### How to Use the Matrix

1. **Draw the 2x2 grid** on a whiteboard or digital canvas
2. **Write each feature on a sticky note**
3. **For each feature, ask**:
   - Value: How much do users want/need this? (High or Low)
   - Effort: How long will it take? (High or Low)
4. **Place sticky notes** in the appropriate quadrant
5. **Discuss and adjust**: Do we agree on placement?
6. **Prioritize**:
   - Start with Quick Wins
   - Plan for Major Projects
   - Fit in Fill-Ins when capacity allows
   - Deprioritize or eliminate Time Sinks

### Example

**Quick Wins**:
- Fix: File upload fails for files with special characters (2 days)
- Add: "Select All" button for file list (1 day)
- Improve: Error messages to be more helpful (3 days)

**Major Projects**:
- Build: Bulk file upload with parallel processing (4 weeks)
- Build: Custom schema editor (6 weeks)
- Build: API for programmatic access (4 weeks)

**Fill-Ins**:
- Add: Dark mode (3 days)
- Add: More file type icons (1 day)
- Polish: Animations for state transitions (2 days)

**Time Sinks**:
- Build: Mobile app (12 weeks, unclear demand)
- Build: Blockchain integration (8 weeks, no user request)
- Build: Advanced admin dashboard (10 weeks, only 2 admins)

---

## 4. Kano Model

### What It Is
A framework that categorizes features based on how they affect user satisfaction.

### When to Use
- Understanding feature types
- Balancing roadmap (don't only build delighters, ensure basics are solid)
- User research prioritization

### The Three Feature Types

#### 1. Basic Expectations (Must-Haves)
**Definition**: Features users expect; their absence causes dissatisfaction, but their presence doesn't increase satisfaction much.

**Examples**:
- Website loads in under 3 seconds
- File upload works reliably
- Data is saved correctly
- App doesn't crash

**Impact on Satisfaction**:
- Absent → Very dissatisfied
- Present → Neutral (it's expected)

**Prioritization**: Must have; these are table stakes

#### 2. Performance Features (More is Better)
**Definition**: Features where more/better increases satisfaction linearly.

**Examples**:
- Faster processing speed
- More file types supported
- More accurate data extraction
- Lower cost

**Impact on Satisfaction**:
- Less/Worse → Dissatisfied
- More/Better → More satisfied

**Prioritization**: Invest in these to stay competitive

#### 3. Delight Features (Wow Factors)
**Definition**: Unexpected features that delight users when present, but don't cause dissatisfaction when absent (users don't know to expect them).

**Examples**:
- AI suggests corrections to extracted data
- One-click report generation
- Personalized dashboard
- Delightful animations

**Impact on Satisfaction**:
- Absent → Neutral (they didn't expect it)
- Present → Very satisfied (pleasant surprise)

**Prioritization**: Invest in these to differentiate, but only after basics are solid

### How to Use Kano

1. **List all features** on your roadmap
2. **Categorize each** as Basic, Performance, or Delight
3. **Ensure you have**:
   - All Basic features (or users will be dissatisfied)
   - Competitive Performance features (or users will choose competitors)
   - Some Delight features (to stand out and create loyalty)
4. **Validate with users**: Ask "How would you feel if we had this feature?" and "How would you feel if we didn't have this feature?"

### Example: Document Processing Tool

**Basic Expectations**:
- File upload works for PDF, images
- Data extraction is accurate (90%+)
- Results are exportable
- App is secure and private

**Performance Features**:
- Processing speed (faster is better)
- Number of file types supported (more is better)
- Batch size limits (more is better)
- Export format options (more is better)

**Delight Features**:
- AI auto-corrects common data entry errors
- Drag-and-drop folder upload (if unexpected)
- Real-time collaboration on results
- Smart suggestions: "Users like you also extract X field"

---

## 5. Eisenhower Matrix (Urgent vs Important)

### What It Is
A time-management framework adapted for product prioritization.

### When to Use
- Balancing strategic work vs firefighting
- Sprint planning
- Quarterly roadmap reviews

### The Four Quadrants

```
            Urgent          Not Urgent
           ─────────────────────────────
Important  | Do First   | Schedule    |
           | (Q1)       | (Q2)        |
           ─────────────────────────────
Not        | Delegate   | Eliminate   |
Important  | (Q3)       | (Q4)        |
           ─────────────────────────────
```

#### Q1: Urgent & Important (Do First)
**Examples**:
- Critical bugs affecting users
- Security vulnerabilities
- Launch blocker issues
- Deadline-driven features

**Action**: Do immediately

#### Q2: Important but Not Urgent (Schedule)
**Examples**:
- Strategic features for next quarter
- Technical debt reduction
- Process improvements
- Research and discovery

**Action**: Schedule time to work on these proactively

#### Q3: Urgent but Not Important (Delegate)
**Examples**:
- Non-critical support escalations
- Stakeholder requests that can be handled by others
- Routine operational tasks

**Action**: Delegate to appropriate team member

#### Q4: Not Urgent & Not Important (Eliminate)
**Examples**:
- Nice-to-have features no one requested
- Low-impact polish work
- Speculative projects

**Action**: Deprioritize or eliminate

### How to Use

1. **List all work** (features, bugs, requests, projects)
2. **For each item, ask**:
   - Urgent: Does this have a deadline? Is there immediate user pain?
   - Important: Does this align with strategic goals? Does it have significant user/business impact?
3. **Place in appropriate quadrant**
4. **Take action**:
   - Q1: Do now
   - Q2: Schedule into roadmap
   - Q3: Delegate or defer
   - Q4: Say no politely

---

## 6. Weighted Scoring Model

### What It Is
A customizable scoring system where you define criteria and weights based on your specific context.

### When to Use
- Organization-specific prioritization
- Complex decisions with multiple factors
- Transparent, objective decision-making

### How to Build Your Model

1. **Define criteria** (3-7 criteria)
2. **Assign weights** (total = 100%)
3. **Score each feature** (1-5 scale)
4. **Calculate weighted score**

### Example Criteria & Weights

| Criterion | Weight | Description |
|-----------|--------|-------------|
| User Value | 30% | How much users want/need this |
| Business Impact | 25% | Revenue, retention, acquisition potential |
| Strategic Fit | 20% | Alignment with company vision |
| Effort | 15% | Implementation complexity (lower effort = higher score) |
| Risk | 10% | Technical/market risk (lower risk = higher score) |

### Example Scoring

**Feature: Bulk File Upload**

| Criterion | Weight | Score (1-5) | Weighted Score |
|-----------|--------|-------------|----------------|
| User Value | 30% | 5 | 1.5 |
| Business Impact | 25% | 4 | 1.0 |
| Strategic Fit | 20% | 5 | 1.0 |
| Effort (inverted) | 15% | 3 | 0.45 |
| Risk (inverted) | 10% | 4 | 0.4 |
| **Total** | **100%** | | **4.35** |

**Feature: Mobile App**

| Criterion | Weight | Score (1-5) | Weighted Score |
|-----------|--------|-------------|----------------|
| User Value | 30% | 3 | 0.9 |
| Business Impact | 25% | 3 | 0.75 |
| Strategic Fit | 20% | 4 | 0.8 |
| Effort (inverted) | 15% | 1 | 0.15 |
| Risk (inverted) | 10% | 2 | 0.2 |
| **Total** | **100%** | | **2.8** |

**Result**: Bulk Upload (4.35) prioritized over Mobile App (2.8)

---

## Combining Frameworks

No single framework is perfect. Combine them for better decisions:

1. **MoSCoW** to scope MVP
2. **RICE** to prioritize roadmap candidates
3. **Value vs Effort** to communicate visually with stakeholders
4. **Kano** to ensure balanced feature portfolio
5. **Weighted Scoring** for complex decisions with specific organizational criteria

---

## Best Practices

### Do's
- Use data to inform, not dictate (frameworks are tools, not rules)
- Involve stakeholders (engineering, design, business) in prioritization
- Revisit priorities regularly (quarterly at minimum)
- Document why decisions were made (for future reference)
- Be transparent about trade-offs

### Don'ts
- Don't prioritize based solely on who shouts loudest
- Don't ignore effort/feasibility
- Don't commit to everything (saying no is part of the job)
- Don't forget to validate assumptions with users
- Don't optimize only for short-term wins (balance with strategic bets)

---

## Template: Prioritization Document

```markdown
# Prioritization: [Quarter/Year]

## Context
[What are we trying to achieve this period?]

## Framework Used
[MoSCoW / RICE / Value vs Effort / Custom Weighted Scoring]

## Criteria
[If using weighted scoring, list criteria and weights]

## Feature Candidates

### 1. [Feature Name]
- **Description**: [Brief description]
- **User Value**: [Score/rating]
- **Business Impact**: [Score/rating]
- **Effort**: [Estimate]
- **Score**: [Final score]
- **Decision**: [Do now / Schedule / Defer]

[Repeat for each feature]

## Final Priority Order
1. [Feature A] - [Reason]
2. [Feature B] - [Reason]
3. [Feature C] - [Reason]

## Deferred/Declined
- [Feature X] - [Reason for deferral]
- [Feature Y] - [Reason for declining]

## Review Date
[When we'll revisit these priorities]
```

---

## Further Reading

- "Inspired" by Marty Cagan (product discovery and prioritization)
- "The Lean Startup" by Eric Ries (MVP and validation)
- "Competing Against Luck" by Clayton Christensen (jobs-to-be-done framework)
