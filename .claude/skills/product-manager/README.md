# Product Manager Skill

## Overview

The **product-manager** skill helps you document features, write specifications, create user stories, and produce product documentation with the rigor and clarity of a professional product manager.

---

## Quick Start

### Using the Skill

Invoke this skill when you need to create product documentation:

```
Use the product-manager skill to document the bulk file upload feature
```

or simply:

```
Document this feature like a PM would
```

### What the Skill Does

When invoked, the skill guides you through:
1. Understanding the feature context (problem, users, goals)
2. Choosing the right documentation type (PRD, user stories, release notes, etc.)
3. Creating comprehensive documentation using professional templates
4. Following product management best practices

---

## Skill Structure

```
product-manager/
├── SKILL.md                          # Main skill definition and instructions
├── README.md                         # This file - usage guide
├── assets/
│   ├── templates/                    # Documentation templates
│   │   ├── feature-spec-template.md
│   │   ├── user-stories-template.md
│   │   ├── release-notes-template.md
│   │   ├── prd-template.md
│   │   ├── roadmap-template.md
│   │   └── acceptance-criteria-template.md
│   └── pm-best-practices/            # PM frameworks and methodologies
│       ├── _README.md                # Guide for adding your own practices
│       ├── discovery-template.md     # Feature discovery framework
│       ├── prioritization-frameworks.md  # RICE, MoSCoW, Value vs Effort, etc.
│       ├── stakeholder-communication.md  # (placeholder for your content)
│       ├── user-research-guide.md        # (placeholder for your content)
│       ├── metrics-and-kpis.md           # (placeholder for your content)
│       └── competitive-analysis.md       # (placeholder for your content)
└── scripts/                          # (reserved for future automation)
```

---

## Documentation Types

### 1. Feature Specification
**When to use**: Detailed technical and functional documentation for a new feature

**Template**: `assets/templates/feature-spec-template.md`

**Includes**:
- Feature overview (problem statement, solution, success metrics)
- User personas and use cases
- Functional requirements (must/should/could/won't have)
- User flows (happy path, alternatives, error states)
- Technical considerations
- Design requirements
- Testing & validation
- Release plan

**Example use case**: "Create a feature spec for the new bulk upload functionality"

---

### 2. User Stories
**When to use**: Breaking down features into user-centric, implementable tasks

**Template**: `assets/templates/user-stories-template.md`

**Includes**:
- User story format (As a...I want to...So that...)
- Acceptance criteria (Given-When-Then)
- Story sizing and prioritization (MoSCoW, story points)
- Dependencies and related stories
- Examples of good and bad user stories

**Example use case**: "Write user stories for the authentication feature"

---

### 3. Release Notes
**When to use**: Communicating changes to users and internal teams

**Template**: `assets/templates/release-notes-template.md`

**Includes**:
- **External** (customer-facing): What's new, improvements, bug fixes
- **Internal** (engineering/QA): Technical details, API changes, deployment notes
- Version history and contributors

**Example use case**: "Generate release notes for v1.2.0"

---

### 4. Product Requirements Document (PRD)
**When to use**: Comprehensive feature planning document before development

**Template**: `assets/templates/prd-template.md`

**Includes**:
- Executive summary
- Problem and user discovery
- Goals and success metrics
- Functional and technical requirements
- User experience and design
- Testing and quality assurance
- Launch plan and timeline
- Appendices (research, competitive analysis, etc.)

**Example use case**: "Create a PRD for the new analytics dashboard"

---

### 5. Product Roadmap
**When to use**: Strategic planning and communicating future work

**Template**: `assets/templates/roadmap-template.md`

**Includes**:
- Now (current quarter features)
- Next (next quarter planned features)
- Later (future ideas under consideration)
- Completed (recent releases)
- Not doing (explicitly out of scope)
- Prioritization framework
- Risks and dependencies

**Example use case**: "Create a Q4 2024 product roadmap"

---

### 6. Acceptance Criteria
**When to use**: Defining clear "done" conditions for features and user stories

**Template**: `assets/templates/acceptance-criteria-template.md`

**Includes**:
- Given-When-Then format (BDD style)
- Checklist format (simple features)
- Scenario-based format (complex features)
- Edge cases and error states
- Accessibility criteria
- Performance criteria

**Example use case**: "Write acceptance criteria for the file upload user story"

---

## PM Best Practices

The `assets/pm-best-practices/` folder contains frameworks and methodologies to support your product work:

### ✅ Completed Best Practices

#### 1. Feature Discovery Template
**File**: `discovery-template.md`

**Use for**: Gathering information before designing/building a feature

**Covers**:
- Problem, user, and solution discovery
- Market and competitive research
- Success metrics and goals
- Technical feasibility
- Resource planning and dependencies
- Risk identification

---

#### 2. Prioritization Frameworks
**File**: `prioritization-frameworks.md`

**Use for**: Deciding what to build next

**Includes**:
- **MoSCoW**: Must/Should/Could/Won't Have categorization
- **RICE Scoring**: Reach × Impact × Confidence / Effort
- **Value vs Effort Matrix**: 2x2 grid for quick wins
- **Kano Model**: Basic/Performance/Delight features
- **Eisenhower Matrix**: Urgent vs Important
- **Weighted Scoring**: Customizable criteria and weights

---

### 📝 Placeholder Best Practices (Add Your Content!)

The following files are placeholders for you to add your organization's best practices:

#### 3. Stakeholder Communication
**File**: `stakeholder-communication.md`

**Suggested content**: Communication templates for different audiences, how to say "no" gracefully, presentation templates

---

#### 4. User Research Guide
**File**: `user-research-guide.md`

**Suggested content**: Interview techniques, survey design, usability testing, creating personas, jobs-to-be-done framework

---

#### 5. Metrics and KPIs
**File**: `metrics-and-kpis.md`

**Suggested content**: Product health metrics, feature success metrics, setting targets, creating dashboards, leading vs lagging indicators

---

#### 6. Competitive Analysis
**File**: `competitive-analysis.md`

**Suggested content**: Framework for analyzing competitors, creating competitive matrices, win/loss analysis, monitoring competitive moves

---

## Customizing the Skill

### Adding Your Own Best Practices

1. **Navigate to the PM best practices folder**:
   ```
   .claude/skills/product-manager/assets/pm-best-practices/
   ```

2. **Fill in placeholder files** with your organization's processes and examples

3. **Or create new files** for additional topics:
   ```bash
   # Example: Add a file about product strategy
   touch assets/pm-best-practices/product-strategy.md
   ```

4. **Use the _README.md** in that folder for guidance on structure and content

---

### Adding Examples from Your Product

Enhance templates and best practices with real examples from your product:

- **In feature specs**: Reference actual features you've built
- **In user stories**: Use real user personas from your product
- **In release notes**: Include actual release notes you've published
- **In roadmaps**: Show real roadmap examples (anonymized if needed)

This makes the skill more practical and tailored to your context.

---

## Tips for Effective Use

### 1. Start with Discovery
Before writing specs, use the discovery template to gather information:
- What problem are we solving?
- Who has this problem?
- How will we measure success?

### 2. Choose the Right Format
Match the documentation type to your audience and stage:
- **Early exploration** → Discovery template
- **Pre-development planning** → PRD or Feature Spec
- **Development phase** → User Stories with Acceptance Criteria
- **Launch communication** → Release Notes
- **Strategic planning** → Roadmap

### 3. Iterate and Collaborate
Product docs are living documents:
- Share drafts early with engineering, design, and stakeholders
- Incorporate feedback
- Keep docs updated as requirements evolve
- Use version history tables to track changes

### 4. Be User-Centric
Always frame features from the user's perspective:
- Start with the problem, not the solution
- Use user stories: "As a [user], I want to [action] so that [benefit]"
- Include real user quotes and research data
- Define success from the user's point of view

### 5. Use Data
Support decisions with evidence:
- User research findings
- Analytics and usage data
- Support ticket trends
- Competitive analysis
- Success metrics and KPIs

---

## Common Use Cases

### Use Case 1: New Feature Development
1. Run discovery (use discovery template)
2. Write PRD with full context
3. Break down into user stories
4. Define acceptance criteria for each story
5. Create release notes when launching

---

### Use Case 2: Quarterly Planning
1. Review past quarter (what shipped, what didn't, why)
2. Prioritize candidates (use prioritization frameworks)
3. Create roadmap for next quarter
4. Write PRDs for top priorities
5. Communicate roadmap to stakeholders

---

### Use Case 3: Feature Launch
1. Finalize feature specs and acceptance criteria
2. Conduct user testing and validation
3. Write internal release notes (technical details)
4. Write external release notes (user-facing)
5. Plan communication strategy

---

## Integration with Development Workflow

### With Agile/Scrum
- **Product Backlog**: User stories from templates
- **Sprint Planning**: Acceptance criteria guide estimates
- **Sprint Review**: Demo against acceptance criteria
- **Retrospectives**: Update best practices based on learnings

### With Design Process
- **Discovery**: Inform design requirements
- **Design Reviews**: Feature specs provide context
- **Handoff**: Acceptance criteria define expected behavior

### With QA/Testing
- **Test Planning**: Acceptance criteria become test cases
- **Bug Reporting**: Reference specs for expected behavior
- **UAT**: Release notes guide user testing

---

## Skill Invocation Examples

### General Documentation
```
Use the product-manager skill to document the new export feature
```

### Specific Document Type
```
Create a PRD for the custom schema editor using the product-manager skill
```

### User Stories
```
Write user stories with acceptance criteria for the API access feature
```

### Release Notes
```
Generate release notes for version 2.0 using the product-manager skill
```

### Roadmap
```
Create a Q1 2025 roadmap using the product-manager skill
```

---

## Best Practices for Documentation

### Writing Principles
1. **Clear and Concise**: Use simple, direct language
2. **User-Centric**: Frame from user perspective
3. **Data-Driven**: Include evidence and metrics
4. **Actionable**: Make it clear what needs to be done
5. **Complete**: Anticipate questions

### Formatting Tips
- Use headings and bullet points for scannability
- Include tables for comparisons and structured data
- Add examples to illustrate concepts
- Use version history to track changes
- Link to related documents

### Collaboration
- Share early and often
- Invite feedback from all stakeholders
- Document decisions and rationale
- Keep docs accessible to all teams

---

## Maintenance

### Keeping the Skill Up-to-Date

1. **Review quarterly**: Are templates still relevant?
2. **Add learnings**: Incorporate insights from recent projects
3. **Update examples**: Replace outdated examples with current ones
4. **Fill placeholders**: Add your organization's best practices over time
5. **Version templates**: Track changes to understand evolution

### Contributing to the Skill

If working with a team:
- Rotate ownership of different best practices
- Hold PM best practices review sessions
- Share learnings from recent launches
- Create a changelog for significant updates

---

## Troubleshooting

### "I don't know where to start"
→ Start with the discovery template to gather information, then choose the appropriate documentation type

### "The templates are too detailed"
→ Use them as a guide, not a checklist. Adapt sections based on feature complexity

### "I need a format not covered here"
→ Create your own template in the assets folder following the existing structure

### "The skill isn't using my custom best practices"
→ Ensure your files are in the correct folder and follow markdown formatting

---

## Resources

### Within This Skill
- **Main skill file**: `SKILL.md` - Full instructions for using the skill
- **Templates folder**: `assets/templates/` - All documentation templates
- **Best practices folder**: `assets/pm-best-practices/` - PM frameworks and methodologies

### External Resources
- "Inspired" by Marty Cagan - Product discovery and management
- "The Lean Startup" by Eric Ries - MVP and validation
- "User Story Mapping" by Jeff Patton - Agile product planning
- "Escaping the Build Trap" by Melissa Perri - Outcome-driven product management

---

## Feedback and Improvements

This skill is designed to evolve with your needs:
- Customize templates for your organization
- Add your own best practices and frameworks
- Incorporate learnings from your product work
- Share improvements with your team

---

## Quick Reference

| Need to... | Use this template | Found at |
|------------|-------------------|----------|
| Document a new feature | Feature Spec | `assets/templates/feature-spec-template.md` |
| Break down into tasks | User Stories | `assets/templates/user-stories-template.md` |
| Communicate a release | Release Notes | `assets/templates/release-notes-template.md` |
| Plan comprehensively | PRD | `assets/templates/prd-template.md` |
| Show future plans | Roadmap | `assets/templates/roadmap-template.md` |
| Define "done" | Acceptance Criteria | `assets/templates/acceptance-criteria-template.md` |
| Gather info first | Discovery | `assets/pm-best-practices/discovery-template.md` |
| Prioritize features | Frameworks | `assets/pm-best-practices/prioritization-frameworks.md` |

---

**Created**: 2024-10-21
**Version**: 1.0
**Maintained By**: Product Team

For questions or suggestions about this skill, consult the main `SKILL.md` file or reach out to the product team.
