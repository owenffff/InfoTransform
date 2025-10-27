# PM Best Practices Asset Folder

## Purpose

This folder contains product management best practices, frameworks, and templates that you can customize and expand with your own methodologies and learnings.

---

## Current Files

### 1. discovery-template.md
**Purpose**: Comprehensive framework for feature discovery before building

**When to use**: At the start of any new feature or enhancement project

**What it covers**:
- Problem discovery (what problem are we solving?)
- User discovery (who has this problem?)
- Solution discovery (how might we solve it?)
- Market & competitive discovery
- Success metrics definition
- Technical feasibility
- Resource planning
- Risk identification

**How to customize**: Add your own discovery questions based on your organization's needs

---

### 2. prioritization-frameworks.md
**Purpose**: Multiple frameworks for prioritizing features and roadmap items

**When to use**: When deciding what to build next, roadmap planning, sprint planning

**What it covers**:
- MoSCoW Method (Must/Should/Could/Won't Have)
- RICE Scoring (Reach × Impact × Confidence / Effort)
- Value vs Effort Matrix (2x2 grid)
- Kano Model (Basic/Performance/Delight features)
- Eisenhower Matrix (Urgent vs Important)
- Weighted Scoring Model (customizable criteria)

**How to customize**: Adapt the scoring criteria and weights to match your organization's priorities

---

## Placeholder Files (Add Your Content)

The following files are placeholders for you to add your own best practices:

### 3. stakeholder-communication.md
**Suggested content**:
- Communication templates for different audiences (engineering, executives, users)
- How to run effective stakeholder meetings
- Presentation templates for feature proposals
- Email templates for launch announcements
- How to say "no" gracefully to feature requests

---

### 4. user-research-guide.md
**Suggested content**:
- How to conduct user interviews
- Survey design best practices
- Usability testing methods
- Analyzing and synthesizing research findings
- Creating user personas
- Jobs-to-be-done framework

---

### 5. metrics-and-kpis.md
**Suggested content**:
- Product health metrics (DAU/MAU, retention, churn)
- Feature success metrics (adoption, engagement, satisfaction)
- How to define good KPIs (SMART criteria)
- Setting targets and benchmarks
- Creating metrics dashboards
- Leading vs lagging indicators

---

### 6. competitive-analysis.md
**Suggested content**:
- Framework for analyzing competitors
- What to analyze (features, pricing, positioning, UX)
- Creating competitive matrices
- Identifying differentiation opportunities
- Tracking competitive moves over time
- Win/loss analysis

---

## How to Add Your Own Content

### Option 1: Create New Markdown Files

Create a new `.md` file in this folder with your topic:

```bash
touch assets/pm-best-practices/your-topic.md
```

### Option 2: Fill In Placeholder Files

Edit the placeholder files listed above and add your organization's best practices.

### Option 3: Add Examples and Case Studies

Enhance existing files with:
- Real examples from your product
- Case studies of successful (and unsuccessful) features
- Lessons learned from past projects
- Your organization's specific processes and templates

---

## Recommended Structure for New Files

When creating new best practice documents, follow this structure:

```markdown
# [Topic Name]

## Overview
[Brief description of what this document covers]

## When to Use
[Scenarios where this practice applies]

## The Framework/Method
[Step-by-step explanation]

## Examples
[Real-world examples]

## Templates
[Reusable templates]

## Best Practices
[Do's and Don'ts]

## Common Pitfalls
[What to avoid]

## Further Reading
[Additional resources]
```

---

## Tips for Building Your Best Practices Library

1. **Start with what you use most**: Add frameworks you actually use, not just theoretical ones

2. **Include real examples**: Use examples from your own product and industry

3. **Keep it practical**: Focus on actionable advice, not just theory

4. **Update regularly**: Revisit and update as you learn from experience

5. **Make it searchable**: Use clear headings and consistent formatting

6. **Link related docs**: Cross-reference related best practices and templates

7. **Version control**: Track changes to understand how your practices evolve

---

## Integration with Claude Code Skill

This folder is referenced by the **product-manager** skill (`SKILL.md`). When you invoke the skill, Claude will use these best practices to guide product documentation.

To make the most of the skill:
1. **Fill in the placeholders** with your organization's practices
2. **Add real examples** from your product
3. **Customize templates** to match your workflow
4. **Keep it updated** as your practices evolve

---

## Contributing

If you're part of a team, consider:
- Having a "PM Best Practices" review session to align on standards
- Rotating ownership of different documents
- Sharing learnings from recent features/launches
- Creating a changelog for significant updates

---

## Questions?

For questions about using the product-manager skill or these best practices:
- Review the main `SKILL.md` file for skill usage instructions
- Check the `assets/templates/` folder for documentation templates
- Consult the Claude Code documentation

---

**Last Updated**: 2024-10-21
**Maintained By**: Product Team
