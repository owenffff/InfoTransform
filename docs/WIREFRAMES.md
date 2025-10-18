# Multi-Record Review UI Wireframes

Visual layouts for the three view modes in the adaptive review workspace.

---

## Layout Overview

All three views share the same outer shell:

```
┌────────────────────────────────────────────────────────────────────┐
│ Top Bar (unchanged)                                                │
│ [InfoTransform Logo]  Session: IT_Audit_2024     [Export] [Close] │
└────────────────────────────────────────────────────────────────────┘
┌────────────────┬───────────────────────────────────────────────────┐
│                │                                                    │
│  File List     │         Document Viewer (60%)                     │
│  Sidebar       │         [PDF or Image Preview]                    │
│  (20%)         │                                                    │
│                │                                                    │
│                ├───────────────────────────────────────────────────┤
│                │                                                    │
│                │         Data Panel (40%) ← THIS CHANGES           │
│                │         [View Mode Specific Layout]               │
│                │                                                    │
└────────────────┴───────────────────────────────────────────────────┘
```

The **Data Panel** (bottom right) adapts based on schema complexity.

---

## View Mode 1: Compact Table (Simple Schemas)

**When:** 1-5 fields, no nesting, < 20 records

**Example:** Document metadata extraction
```
Schema: { title: str, author: str, date: str, page_count: int }
```

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│ Extracted Data                                         [Approve] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  5 records extracted                                                │
│                                                                     │
│  ┌───┬─────────────────┬─────────────────┬─────────────┬────────┐ │
│  │ # │ Title           │ Author          │ Date        │ Pages  │ │
│  ├───┼─────────────────┼─────────────────┼─────────────┼────────┤ │
│  │ 1 │ Annual Report   │ John Smith      │ 2024-01-15  │ 124    │ │
│  │ 2 │ Q4 Summary      │ Jane Doe        │ 2024-02-01  │ 45     │ │
│  │ 3 │ Audit Findings  │ Bob Johnson     │ 2024-03-10  │ 89     │ │
│  │ 4 │ Compliance Rev  │ Alice Chen      │ 2024-03-15  │ 67     │ │
│  │ 5 │ Risk Assessment │ Mike Williams   │ 2024-04-01  │ 103    │ │
│  └───┴─────────────────┴─────────────────┴─────────────┴────────┘ │
│                                                                     │
│  💡 Click any cell to edit, double-click for expanded editor       │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Progress: 12 of 50 approved                                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- All data visible at once
- Inline editing (click to edit)
- Horizontal scroll if many columns
- Sticky row number column

---

## View Mode 2: Table + Drawer (Moderate Schemas)

**When:** 6-10 fields, 1-2 long text fields, no deep nesting

**Example:** Report summaries
```
Schema: {
  report_id: str,
  title: str,
  category: str,
  summary: str (long),
  author: str,
  date: date,
  status: enum,
  priority: enum
}
```

### Wireframe

**Main View (Table):**
```
┌─────────────────────────────────────────────────────────────────────┐
│ Extracted Data │ [Table ⊞] [Filter ▼]              [Approve All] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  8 records extracted                                                │
│                                                                     │
│  ┌───┬──────────┬─────────────────┬─────────────┬──────────┬─────┐ │
│  │ ☑ │ ID       │ Title           │ Category    │ Status   │ ⋮  │ │
│  ├───┼──────────┼─────────────────┼─────────────┼──────────┼─────┤ │
│  │ ☑ │ RPT-001  │ Infrastructure  │ Security    │ ✓ App    │ ⋮  │ │
│  │ ☐ │ RPT-002  │ Access Control  │ Compliance  │ Pending  │ ⋮  │ ← Click [⋮]
│  │ ☑ │ RPT-003  │ Data Protection │ Privacy     │ ✓ App    │ ⋮  │ │
│  │ ☐ │ RPT-004  │ Network Scan    │ Security    │ Pending  │ ⋮  │ │
│  │ ☐ │ RPT-005  │ User Training   │ HR          │ ⚠ Error  │ ⋮  │ │
│  └───┴──────────┴─────────────────┴─────────────┴──────────┴─────┘ │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ Progress: 12 of 50 approved                                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Drawer (Slides in from right):**
```
                                    ┌───────────────────────────────┐
                                    │ × RPT-002                     │
                                    ├───────────────────────────────┤
                                    │                               │
                                    │  Report ID                    │
                                    │  [RPT-002________________]    │
                                    │                               │
                                    │  Title                        │
                                    │  [Access Control Review___]   │
                                    │                               │
                                    │  Category                     │
                                    │  [Compliance ▼]               │
                                    │                               │
                                    │  Summary (158 chars)          │
                                    │  ┌─────────────────────────┐  │
                                    │  │This report examines...│  │
                                    │  │current access control │  │
                                    │  │policies and identifies│  │
                                    │  │gaps in enforcement... │  │
                                    │  └─────────────────────────┘  │
                                    │                               │
                                    │  Author                       │
                                    │  [Sarah Johnson__________]    │
                                    │                               │
                                    │  Date                         │
                                    │  [2024-03-15 📅]              │
                                    │                               │
                                    │  Status                       │
                                    │  ◉ Pending                    │
                                    │  ○ Approved                   │
                                    │  ○ Rejected                   │
                                    │                               │
                                    │  Priority                     │
                                    │  [High ▼]                     │
                                    │                               │
                                    ├───────────────────────────────┤
                                    │ [Reject] [Approve Record]     │
                                    └───────────────────────────────┘
```

**Key Features:**
- Table shows 4-5 key columns only
- [⋮] menu in each row
- Drawer opens with full record form
- Can bulk-select with checkboxes
- Quick status indicators in table

---

## View Mode 3: Master-Detail (Complex Schemas)

**When:** 10+ fields, nested arrays/objects, complex validation

**Example:** IT Audit findings
```
Schema: {
  reference: str,
  category: str,
  title: str,
  description: str (long),
  risk_statement: str (long),
  root_cause: str,
  root_cause_category: enum,
  recommendations: List[{
    description: str,
    priority: str,
    timeline: str
  }],
  ... 5 more fields
}
```

### Wireframe

```
┌─────────────────────────────────────────────────────────────────────┐
│ 12 Records │ [Master-Detail ⊞] [Filter ▼]         [Approve All ▼] │
├──────────────────────────┬──────────────────────────────────────────┤
│                          │                                          │
│ Record Navigator (30%)   │ Detail View (70%)                        │
│                          │                                          │
│ ┌─ 12 Records ───── 3 ─┐│ Issue #1: Critical Access Control Gap    │
│ │ [Search...🔍]        ││ ┌────────────────────────────────────────┤
│ └──────────────────────┘│ │ [Form View] [JSON View]                │
│                          │ ├────────────────────────────────────────┤
│ ☑ Record 1              │ │                                        │
│   ISMC-2024-001         │ │ Reference            Category          │
│   Critical Access...    │ │ [ISMC-2024-001]      [Access Control▼] │
│                          │ │                                        │
│ ☐ Record 2   ⚠          │ │ Agency                                 │
│   ISMC-2024-002         │ │ [IT Department___________________]     │
│   Missing Encryption    │ │                                        │
│                          │ │ Title                                  │
│ ☑ Record 3              │ │ ┌────────────────────────────────────┐ │
│   ISMC-2024-003         │ │ │Critical gap in user access mgmt...│ │
│   Patch Management      │ │ └────────────────────────────────────┘ │
│                          │ │                                        │
│ ☐ Record 4              │ │ Subtitle                               │
│   ISMC-2024-004         │ │ [Inadequate segregation of duties__]   │
│   Logging Failures      │ │                                        │
│                          │ │ Description (287 chars)                │
│ ☑ Record 5              │ │ ┌────────────────────────────────────┐ │
│   ISMC-2024-005         │ │ │The current access control framework│ │
│   Backup Issues         │ │ │lacks proper segregation of duties, │ │
│                          │ │ │allowing users to have conflicting  │ │
│ [+] Add Record          │ │ │permissions that could lead to...   │ │
│                          │ │ └────────────────────────────────────┘ │
│                          │ │                                        │
│                          │ │ Risk Statement (215 chars)             │
│                          │ │ [Click to expand..._______________]    │
│                          │ │                                        │
│                          │ │ Root Cause                             │
│                          │ │ [Inadequate training and lack of___]   │
│                          │ │                                        │
│                          │ │ Root Cause Category                    │
│                          │ │ ◉ People  ○ Process  ○ System          │
│                          │ │                                        │
│                          │ │ Recommendations (3) ▼                  │
│                          │ │ ┌────────────────────────────────────┐ │
│                          │ │ │ 1. Implement MFA           [×]     │ │
│                          │ │ │    Priority: High                  │ │
│                          │ │ │    Timeline: 30 days    [Expand▼]  │ │
│                          │ │ ├────────────────────────────────────┤ │
│                          │ │ │ 2. Update policies...      [×]     │ │
│                          │ │ │ 3. Quarterly audits...     [×]     │ │
│                          │ │ │                                    │ │
│                          │ │ │ [+ Add Recommendation]             │ │
│                          │ │ └────────────────────────────────────┘ │
│                          │ │                                        │
│                          │ ├────────────────────────────────────────┤
│                          │ │ [Reject Record] [Approve Record]       │
│                          │ └────────────────────────────────────────┘
└──────────────────────────┴──────────────────────────────────────────┘
```

**Key Features:**
- **Left (30%):** Record list with status
- **Right (70%):** Full form view of selected record
- Search in record list
- Nested arrays expandable (accordion)
- Per-record approval
- Clear visual hierarchy

---

## Detailed Component Breakdown

### Record Navigator (Left Sidebar)

```
┌─────────────────────────┐
│ 12 Records         [3]  │  ← Record count + status badges
├─────────────────────────┤
│ [Search records... 🔍]  │  ← Search/filter
├─────────────────────────┤
│                         │
│ ☑ Record 1              │  ← Checkbox (multi-select)
│   ✓ ISMC-2024-001       │  ← Status icon + identifier
│   Critical Access...    │  ← Title (truncated)
│                         │
│ ☐ Record 2   [!] [✎]    │  ← Warning + unsaved indicator
│   ⧗ ISMC-2024-002       │  ← Pending icon
│   Missing Encryption    │
│                         │
│ ☑ Record 3              │
│   ✓ ISMC-2024-003       │
│   Patch Management      │
│                         │
│     ... (scrollable)    │
│                         │
├─────────────────────────┤
│ 3 selected              │  ← Bulk actions (if any selected)
│ [Approve] [Clear]       │
└─────────────────────────┘

Icons:
✓ = Approved (green)
⧗ = Pending (gray)
✗ = Rejected (red)
[!] = Validation error (amber)
[✎] = Unsaved changes (amber)
```

### Detail View (Right Panel)

**Header:**
```
┌──────────────────────────────────────────┐
│ Issue #1: Critical Access Control Gap    │  ← Record title
├──────────────────────────────────────────┤
│ [Form View] [JSON View]                  │  ← View toggle
├──────────────────────────────────────────┤
```

**Form Sections:**

**1. Header Row (short fields)**
```
│ Reference            Category           Agency              │
│ [ISMC-2024-001]      [Access Ctrl ▼]    [IT Dept______]    │
```

**2. Title Fields (full width)**
```
│ Title                                                        │
│ ┌────────────────────────────────────────────────────────┐  │
│ │Critical gap in user access management                  │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ Subtitle                                                     │
│ [Inadequate segregation of duties_____________________]     │
```

**3. Long Text (expandable)**
```
│ Description (287 chars)                                      │
│ ┌────────────────────────────────────────────────────────┐  │
│ │The current access control framework lacks proper       │  │
│ │segregation of duties, allowing users to have          │  │
│ │conflicting permissions...                             │  │
│ └────────────────────────────────────────────────────────┘  │
```

**4. Mixed Grid (short + medium)**
```
│ Root Cause                      Root Cause Category          │
│ [Inadequate training_____]      ◉ People                    │
│                                  ○ Process                   │
│                                  ○ System                    │
```

**5. Nested Array (accordion)**
```
│ Recommendations (3 items) ▼                                  │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ ┌─ Recommendation 1 ─────────────────────────────── × ┐│  │
│ │ │ Description                                         ││  │
│ │ │ [Implement multi-factor authentication_________]    ││  │
│ │ │                                                     ││  │
│ │ │ Priority           Timeline                         ││  │
│ │ │ [High ▼]           [30 days___]                     ││  │
│ │ └─────────────────────────────────────────────────────┘│  │
│ │                                                         │  │
│ │ ┌─ Recommendation 2 (collapsed) ──────────────────── × ┐│  │
│ │ ┌─ Recommendation 3 (collapsed) ──────────────────── × ┐│  │
│ │                                                         │  │
│ │ [+ Add Recommendation]                                  │  │
│ └────────────────────────────────────────────────────────┘  │
```

**Footer:**
```
├──────────────────────────────────────────────────────────────┤
│ [Reject Record]  [Approve Record]           [Next Record >] │
└──────────────────────────────────────────────────────────────┘
```

---

## Interaction Patterns

### 1. Navigation Flow

**Table View → Drawer:**
```
[Table row] → Click [⋮] → Drawer slides in → Edit → Save → Drawer closes
```

**Master-Detail:**
```
[Record list] → Click record → Detail loads → Edit → Click next record
```

**Keyboard:**
```
↑/↓ arrows → Navigate records
Enter → Open drawer / Select record
Escape → Close drawer / Clear selection
Tab → Next field in form
Ctrl+S → Save
Ctrl+A → Approve
```

### 2. Editing States

**Inline (Table):**
```
Normal:    [Value_______________]
Focus:     [Value_______________]  ← Blue ring
Edited:    |[New Value__________]  ← Orange left border
Error:     [Invalid_____________]  ← Red border + message below
```

**Expanded (Textarea):**
```
Double-click cell → Popover opens
┌──────────────────────────┐
│ Field Name               │
│ ┌────────────────────┐   │
│ │ Expanded text...   │   │
│ │ (scrollable)       │   │
│ │                    │   │
│ └────────────────────┘   │
│           [Done]         │
└──────────────────────────┘
```

### 3. Status Indicators

**Record Status (in navigator):**
```
✓  Approved     (green checkmark)
⧗  Pending      (gray clock)
✗  Rejected     (red X)
[!] Error       (amber alert)
[✎] Edited      (amber pencil)
```

**Badge in Title:**
```
Record 1  [✓ Approved]     ← Green badge
Record 2  [⧗ Pending]      ← Gray badge
Record 3  [✗ Rejected]     ← Red badge
Record 4  [⚠ 2 errors]     ← Amber badge
Record 5  [✎ Unsaved]      ← Amber badge
```

---

## Responsive Breakpoints

### Desktop (> 1280px)
- Full three-panel layout
- Navigator: 30% width
- Document viewer: 60% width
- Data panel: 40% height

### Tablet (768-1280px)
- Stack document viewer above data panel
- Table + drawer for all schemas
- Navigator becomes slide-out panel

### Mobile (< 768px)
- Full-screen views
- Tab navigation: [Document] [Data]
- List view → tap record → full-screen detail

---

## Color Reference

```css
/* Status colors */
.approved    { background: #f0fdf4; color: #166534; }
.pending     { background: #f9fafb; color: #6b7280; }
.rejected    { background: #fef2f2; color: #991b1b; }
.error       { background: #fffbeb; color: #92400e; }
.edited      { background: #fef3c7; color: #92400e; }

/* Interactive */
.selected    { background: #eff6ff; border-left: 4px solid #3b82f6; }
.hover       { background: #f9fafb; }
.focus       { outline: 2px solid #3b82f6; }

/* Borders */
.border      { border-color: #e5e7eb; }
.edited-mark { border-left: 2px solid #f97316; }
.error-mark  { border-color: #ef4444; }
```

---

## Animation Specs

```css
/* Drawer slide-in */
.drawer-enter {
  transform: translateX(100%);
  transition: transform 200ms ease-out;
}

/* Record selection */
.record-select {
  transition: background-color 150ms ease;
}

/* Accordion expand */
.accordion-expand {
  transition: height 200ms ease-out;
}

/* Status badge appear */
.badge-appear {
  animation: fadeIn 150ms ease-in;
}
```

---

## Accessibility Notes

### Keyboard Navigation
- Tab order: Search → Record list → Detail form → Actions
- Arrow keys: Navigate records
- Enter: Select/expand
- Escape: Close/cancel

### Screen Reader
```html
<div role="navigation" aria-label="Record list">
  <button
    role="option"
    aria-selected="true"
    aria-label="Record 1 of 12: ISMC-2024-001, Critical Access Control Gap, Approved"
  >
    ...
  </button>
</div>

<main role="main" aria-label="Record details">
  <form aria-label="Edit record ISMC-2024-001">
    <label for="reference">Reference</label>
    <input id="reference" aria-required="true" />
  </form>
</main>
```

### Focus Indicators
- Always visible (not :focus-visible)
- 2px solid blue outline
- 2px offset from element

---

## Print View Considerations

When printing approved records:

```
┌─────────────────────────────────────────┐
│ InfoTransform Review Report             │
│ Session: IT_Audit_2024                  │
│ Exported: 2024-10-18 14:35             │
├─────────────────────────────────────────┤
│                                         │
│ Record 1: ISMC-2024-001                 │
│ Status: ✓ Approved by John Doe          │
│ Approved: 2024-10-18 14:30             │
│                                         │
│ Reference: ISMC-2024-001                │
│ Category: Access Control                │
│ ...                                     │
│                                         │
├─────────────────────────────────────────┤
│ Record 2: ISMC-2024-002                 │
│ ...                                     │
└─────────────────────────────────────────┘
```

---

## Conclusion

These wireframes show three distinct but cohesive view modes:

1. **Compact Table**: Fast scanning for simple data
2. **Table + Drawer**: Overview with detail on demand
3. **Master-Detail**: Comprehensive editing for complex schemas

All three share:
- Consistent header/footer
- Same color language
- Same interaction patterns
- Same keyboard shortcuts

Choose the view that matches your schema complexity, or let the system auto-detect!
