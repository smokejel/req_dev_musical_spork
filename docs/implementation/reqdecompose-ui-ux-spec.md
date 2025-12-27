# ReqDecompose AI — UI/UX Specification

**Version:** 1.0  
**Date:** December 21, 2025  
**Based on:** Stitch-generated screen designs  
**Purpose:** Detailed specification for frontend implementation

---

## Table of Contents

1. [Design System](#1-design-system)
2. [Screen 1: Landing Page](#2-screen-1-landing-page)
3. [Screen 2: Upload & Configure](#3-screen-2-upload--configure)
4. [Screen 3: Run Progress](#4-screen-3-run-progress)
5. [Screen 4: Dashboard / Results](#5-screen-4-dashboard--results)
6. [Global Components](#6-global-components)
7. [Interaction Patterns](#7-interaction-patterns)
8. [Error States & Edge Cases](#8-error-states--edge-cases)
9. [Responsive Considerations](#9-responsive-considerations)

---

## 1. Design System

### 1.1 Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#0D1117` | Main background |
| `--bg-secondary` | `#161B22` | Card backgrounds, panels |
| `--bg-tertiary` | `#21262D` | Elevated elements, hover states |
| `--border-default` | `#30363D` | Card borders, dividers |
| `--border-accent` | `#388BFD` | Focus states, active elements |
| `--text-primary` | `#F0F6FC` | Headlines, primary text |
| `--text-secondary` | `#8B949E` | Descriptions, labels |
| `--text-muted` | `#6E7681` | Timestamps, metadata |
| `--accent-blue` | `#388BFD` | Primary buttons, links, active states |
| `--accent-green` | `#3FB950` | Success states, completed, high scores |
| `--accent-yellow` | `#D29922` | Warnings, medium scores |
| `--accent-red` | `#F85149` | Errors, critical issues, low scores |
| `--accent-purple` | `#A371F7` | Processing states |

### 1.2 Typography

| Element | Font | Weight | Size | Line Height |
|---------|------|--------|------|-------------|
| H1 (Page Title) | Inter | 600 | 32px | 40px |
| H2 (Section Title) | Inter | 600 | 24px | 32px |
| H3 (Card Title) | Inter | 600 | 18px | 24px |
| Body | Inter | 400 | 14px | 20px |
| Body Small | Inter | 400 | 12px | 16px |
| Label | Inter | 500 | 12px | 16px |
| Code/Mono | JetBrains Mono | 400 | 13px | 20px |

### 1.3 Spacing Scale

- `4px` — Tight spacing (icon gaps)
- `8px` — Compact spacing (within components)
- `12px` — Default internal padding
- `16px` — Component spacing
- `24px` — Section spacing
- `32px` — Large section gaps
- `48px` — Page section separators

### 1.4 Border Radius

- `4px` — Buttons, inputs, badges
- `8px` — Cards, panels
- `12px` — Large cards, modals
- `50%` — Avatars, circular icons

### 1.5 Shadows

- `--shadow-sm`: `0 1px 2px rgba(0,0,0,0.3)` — Subtle elevation
- `--shadow-md`: `0 4px 12px rgba(0,0,0,0.4)` — Cards, dropdowns
- `--shadow-lg`: `0 8px 24px rgba(0,0,0,0.5)` — Modals, popovers

---
### Reference screens
#### Screen 1: Staging_Area/screen1.png
#### Screen 2: Staging_Area/screen2.png
#### Screen 3: Staging_Area/screen3.png
#### Screen 4: Staging_Area/screen4.png

## 2. Screen 1: Landing Page

**Route:** `/`  
**Purpose:** First impression, explain value proposition, provide quick access to recent workflows

### 2.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Global Header]                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Hero Section]                                              │
│   - Badge: "AI-POWERED ENGINEERING"                         │
│   - Headline                                                │
│   - Subheadline                                             │
│   - CTA Buttons                          [Hero Visual]      │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Workflow Explanation Section]                              │
│   - Section title: "The Workflow"                           │
│   - 4 feature cards in row                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Recent Workflows Section]                                  │
│   - Section title + "View All" link                         │
│   - Workflows table                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Specifications

#### Hero Section

| Element | Specification |
|---------|---------------|
| Badge | Pill shape, `--bg-tertiary` background, `--accent-blue` text, sparkle icon |
| Headline | H1, max-width 480px, "Decompose Complex Requirements with AI Precision." |
| Subheadline | Body text, `--text-secondary`, max-width 440px |
| Primary CTA | Blue filled button, "Start New Workflow →", navigates to `/upload` |
| Secondary CTA | Ghost button (transparent with border), "View Demo", opens demo modal or video |
| Hero Visual | Animated visualization showing processing state, can be Lottie or CSS animation |

#### Workflow Cards (4 cards)

| Property | Value |
|----------|-------|
| Layout | 4-column grid, equal width |
| Card background | `--bg-secondary` |
| Icon | 40x40px, rounded background matching node color |
| Title | H3, `--text-primary` |
| Description | Body small, `--text-secondary`, 2-3 lines max |

**Card Content:**

| Card | Icon Color | Title | Description |
|------|------------|-------|-------------|
| 1 | Blue | Extract | Ingest raw PRDs, functional specs, and legacy documentation automatically. |
| 2 | Green | Analyze | Identify core logic, edge cases, and hidden dependencies using semantic AI. |
| 3 | Purple | Decompose | Break down high-level features into atomic, actionable engineering tasks. |
| 4 | Teal | Validate | Cross-reference tasks against technical constraints and architectural standards. |

#### Recent Workflows Table

| Column | Width | Content |
|--------|-------|---------|
| Project Name | 30% | Icon + project name, clickable |
| Source Doc | 20% | Filename with extension |
| Date Created | 20% | Format: "Oct 24, 2023" |
| Status | 15% | Badge: Completed (green), Processing (blue), Failed (red) |
| Actions | 15% | "View" / "Cancel" / "Retry" link based on status |

**Table States:**
- Empty state: "No workflows yet. Start your first workflow to see results here."
- Loading state: Skeleton rows (3 rows)
- Error state: "Unable to load recent workflows. [Retry]"

### 2.3 Interactions

| Action | Behavior |
|--------|----------|
| Click "Start New Workflow" | Navigate to `/upload` |
| Click "View Demo" | Open modal with demo video or start guided tour |
| Click project row | Navigate to `/results/{run_id}` |
| Click "View All" | Navigate to `/workflows` (list page) |
| Hover on workflow row | Row background lightens to `--bg-tertiary` |

---

## 3. Screen 2: Upload & Configure

**Route:** `/upload` or `/projects/{project_id}/upload`  
**Purpose:** Upload specification document, configure analysis parameters

### 3.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Global Header]                                             │
├─────────────────────────────────────────────────────────────┤
│ [Breadcrumb: Projects > Project Alpha > Decompose]          │
├─────────────────────────────────────────────────────────────┤
│ [Page Title: "Upload & Configure"]                          │
│ [Subtitle]                                                  │
├───────────────────────────────┬─────────────────────────────┤
│                               │                             │
│ [Upload Section]              │ [Configuration Panel]       │
│                               │                             │
│ ┌─────────────────────────┐   │ Target Subsystem            │
│ │ Specification Document  │   │ [Input Field]               │
│ │                         │   │                             │
│ │   [Drop Zone]           │   │ Domain                      │
│ │                         │   │ [Dropdown]                  │
│ └─────────────────────────┘   │                             │
│                               │ Human-in-the-Loop Review    │
│ ┌─────────────────────────┐   │ [Toggle Buttons]            │
│ │ Additional Context      │   │                             │
│ │ [Collapsed by default]  │   │ Analysis Mode               │
│ └─────────────────────────┘   │ [Mode Cards]                │
│                               │                             │
│                               │ [Start Decomposition Btn]   │
│                               │                             │
└───────────────────────────────┴─────────────────────────────┘
```

### 3.2 Component Specifications

#### File Upload Zone (Primary)

| Property | Value |
|----------|-------|
| Dimensions | Min-height 240px, full width of left column |
| Border | 2px dashed `--border-default`, 8px radius |
| Border (hover/drag) | 2px dashed `--accent-blue` |
| Background (drag over) | `rgba(56, 139, 253, 0.1)` |
| Icon | Cloud upload, 48px, `--text-muted` |
| Primary text | "Click to upload or drag and drop" |
| Secondary text | "PDF, DOCX, or TXT (MAX. 20MB)" |

**Upload States:**

| State | Appearance |
|-------|------------|
| Empty | Default dashed border, upload icon |
| Drag over | Blue border, blue tint background |
| File selected | Solid border, file icon + filename + size + remove button |
| Uploading | Progress bar overlay |
| Error | Red border, error message below |

**Accepted Files:**
- `.pdf` (application/pdf)
- `.docx` (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- `.txt` (text/plain)
- Max size: 20MB

#### Additional Context Section (Collapsible)

| Property | Value |
|----------|-------|
| Default state | Collapsed |
| Header | Icon + "Additional Context / Reference Material" + chevron |
| Expanded content | Secondary drop zone for multiple files |
| File list | Shows uploaded context files with remove option |

#### Configuration Panel

**Target Subsystem Input:**
| Property | Value |
|----------|-------|
| Type | Text input |
| Placeholder | "e.g., Propulsion Control Unit" |
| Validation | Required field |
| Help text | None (placeholder is descriptive) |

**Domain Dropdown:**
| Property | Value |
|----------|-------|
| Type | Select dropdown |
| Options | "Generic", "Aerospace", "Automotive", "Rail", "Medical", "Software" |
| Default | "Generic" |
| Help text | Optional — shows when non-generic selected |

**Human-in-the-Loop Toggle:**
| Property | Value |
|----------|-------|
| Type | Segmented button group (2 options) |
| Options | "Review Before" / "Review After" |
| Default | "Review Before" selected |
| Help text | Dynamic based on selection |

Help text content:
- Review Before: "Review Before allows you to approve the component breakdown structure before full requirement generation."
- Review After: "Review After lets you review and edit generated requirements before finalizing."

**Analysis Mode Cards:**
| Property | Value |
|----------|-------|
| Type | Radio card group (2 cards) |
| Card 1 | Icon (lightning), "Standard", "Optimized for speed. Single pass analysis." |
| Card 2 | Icon (gear), "Thorough", "Recursive ISO/IEEE compliance checks." |
| Default | "Standard" selected |
| Selected state | Blue border, slightly elevated |

**Thorough Mode Expanded Options (shown when Thorough selected):**
- Quality Threshold slider (0.7 - 0.95, default 0.85)
- Max Iterations dropdown (1-5, default 3)

#### Start Button

| Property | Value |
|----------|-------|
| Type | Primary button, full width of config panel |
| Text | "▶ Start Decomposition" |
| Disabled state | Gray, when no file uploaded or subsystem empty |
| Loading state | Spinner + "Starting..." |

### 3.3 Interactions

| Action | Behavior |
|--------|----------|
| Drop file on zone | Validate type/size, show filename, enable button |
| Click zone | Open file picker |
| Remove file | Clear selection, disable button if subsystem also empty |
| Select "Thorough" mode | Expand advanced options with animation |
| Click "Start Decomposition" | Validate form → POST to API → Navigate to `/run/{id}` |

### 3.4 Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| Specification Document | Required | "Please upload a specification document" |
| Specification Document | Max 20MB | "File exceeds 20MB limit" |
| Specification Document | Valid type | "Unsupported file type. Please upload PDF, DOCX, or TXT" |
| Target Subsystem | Required | "Please enter a target subsystem" |
| Target Subsystem | Max 100 chars | "Subsystem name is too long" |

---

## 4. Screen 3: Run Progress

**Route:** `/run/{run_id}`  
**Purpose:** Real-time visualization of workflow execution, human review interaction

### 4.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Global Header]                                             │
├─────────────────────────────────────────────────────────────┤
│ [Run Title + Status Badge]              [Metrics] [Cancel]  │
│ [Project + Initiator + Time]                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Pipeline Visualization]                                    │
│  Extract ──► Analyze ──► Decompose ◄──┐ ──► Validate       │
│                              │        │                     │
│                              └────────┘ (refinement loop)   │
│                                                             │
│ [Progress Bar]                                              │
│                                                             │
├─────────────────────────────────┬───────────────────────────┤
│                                 │                           │
│ [Log Panel]                     │ [Human Review Panel]      │
│                                 │ (conditional)             │
│ [Tabs: Strategy Log |           │                           │
│        Extracted Data |         │ [Generated Requirements]  │
│        Quality Checks]          │ (mini table)              │
│                                 │                           │
│ [Live log output]               │                           │
│                                 │                           │
├─────────────────────────────────┴───────────────────────────┤
│ [Footer: Trace ID | CPU | Memory]                           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Specifications

#### Run Header

| Element | Specification |
|---------|---------------|
| Run Title | H1, "Decomposition Run #{number}" |
| Status Badge | Pill: PROCESSING (blue), COMPLETED (green), FAILED (red), PAUSED (yellow) |
| Metadata | "Project {name} • Initiated by {user} • {relative_time}" |
| Elapsed Time | Monospace, "00:00:00" format, updates every second |
| Tokens | "~{count}k" approximate token usage |
| Cancel Button | Red outlined button, "Cancel Run" |

#### Pipeline Visualization

**Node States:**

| State | Icon Background | Icon Color | Label Color | Connector |
|-------|-----------------|------------|-------------|-----------|
| Pending | `--bg-tertiary` | `--text-muted` | `--text-muted` | Gray line |
| Active | `--accent-blue` | White | `--accent-blue` | Animated blue line |
| Complete | `--accent-green` | White | `--accent-green` | Green line |
| Error | `--accent-red` | White | `--accent-red` | Red line |

**Refinement Loop:**
- Dashed curved arrow from Validate back to Decompose
- Label: "Refinement Loop"
- Visible when iteration_count > 1

**Progress Bar:**
- Full width below pipeline
- Segmented into 4 sections (one per node)
- Filled segments show completion
- Active segment has gradient animation

#### Log Panel

**Tabs:**
| Tab | Content |
|-----|---------|
| Strategy Log | Real-time log of AI decisions and actions |
| Extracted Data | Preview of extracted requirements (after Extract completes) |
| Quality Checks | Quality validation results (after Validate runs) |

**Log Entry Format:**
```
[HH:MM:SS] ✓ Action completed successfully (green)
[HH:MM:SS] ℹ Information message (blue)
[HH:MM:SS] ⚠ Warning message (yellow)
[HH:MM:SS] ✗ Error message (red)
```

**Live Stream Indicator:**
- Green dot + "Live Stream" label
- Pulses when receiving data

**Currently Processing Highlight:**
```
>>> Generating requirement: REQ-ID
    "Requirement text preview..."
```
- Left blue border
- Slightly elevated background

#### Human Review Panel (Conditional)

**Trigger:** Shown when `requires_human_review: true` in state

| Element | Specification |
|---------|---------------|
| Header | Warning icon + "HUMAN REVIEW SUGGESTED" |
| Description | Explains why review is needed |
| Current Draft | Card showing the requirement text with "Conflict" badge if applicable |
| Edit Button | Secondary button, opens edit modal |
| Approve Button | Primary blue button, continues workflow |

**Edit Modal:**
- Full requirement text in textarea
- Character count
- Cancel / Save Changes buttons

#### Generated Requirements Mini-Table

| Column | Content |
|--------|---------|
| ID | Requirement ID, clickable |
| Description | Truncated text (first 30 chars + "...") |
| Score | Percentage with color coding (green >85%, yellow 70-85%, red <70%, "--" if pending) |

**Footer:** "View All ({count} Generated)" link

#### System Footer

| Element | Content |
|---------|---------|
| Trace ID | "Trace ID: {uuid}" — for debugging |
| CPU | "CPU: {percent}%" |
| Memory | "Mem: {amount}MB" |

### 4.3 Real-Time Updates (SSE)

**Event Types:**

| Event | Payload | UI Action |
|-------|---------|-----------|
| `node_started` | `{node: string}` | Set node to active state |
| `node_completed` | `{node: string, result: object}` | Set node to complete, update preview |
| `log_entry` | `{timestamp, level, message}` | Append to log panel |
| `requirement_generated` | `{id, text, score}` | Add row to mini-table |
| `human_review_required` | `{requirement_id, reason, draft}` | Show review panel |
| `progress_update` | `{percent, tokens}` | Update progress bar and metrics |
| `workflow_completed` | `{final_state}` | Navigate to results page |
| `workflow_failed` | `{error}` | Show error state |

### 4.4 Interactions

| Action | Behavior |
|--------|----------|
| Click "Cancel Run" | Confirmation dialog → API call → Navigate to landing |
| Click "Approve" in review | Hide review panel → Continue workflow |
| Click "Edit" in review | Open edit modal |
| Save edit | Update requirement → Continue workflow |
| Click requirement ID | Expand to show full text |
| Switch tabs | Load corresponding content (may need API call for Extracted Data) |

---

## 5. Screen 4: Dashboard / Results

**Route:** `/results/{run_id}`  
**Purpose:** Comprehensive view of completed workflow, quality analysis, export

### 5.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ [Global Header with Export + New Workflow buttons]          │
├─────────────────────────────────────────────────────────────┤
│ [Breadcrumb]                                                │
│ [Page Title + Status]                   [Run History] [Run] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Summary Cards Row]                     [Quality Breakdown] │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐    │ Completeness 98%  │
│ │Extracted│ │Generated│ │ Quality │    │ Clarity 92%       │
│ │   56    │ │   142   │ │  94/100 │    │ Testability 88%   │
│ └─────────┘ └─────────┘ └─────────┘    │ Traceability 100% │
│                                         └───────────────────┤
│ [Operational Metrics: Time | Cost | Energy]                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Requirements Table]                    [Sidebar]           │
│                                         ┌───────────────────┤
│ [Search] [Filter] [View Toggle]         │ Traceability      │
│                                         │ Focus             │
│ ┌─────────────────────────────────┐    │                   │
│ │ ID | Text | Type | Parent | Scr │    │ Parent: SYS-05    │
│ │─────────────────────────────────│    │ └─ SR-103 ⚠       │
│ │ SR-101 | The system shall... |  │    │                   │
│ │ SR-102 | The flight control... │    ├───────────────────┤
│ │ ...                             │    │ Quality Issues    │
│ └─────────────────────────────────┘    │ [3 Critical]      │
│                                         │                   │
│ [Pagination]                            │ SR-103: Ambiguity │
│                                         │ SR-209: Untestable│
│                                         └───────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Component Specifications

#### Page Header

| Element | Specification |
|---------|---------------|
| Breadcrumb | Projects > {Project Name} > Decomposition Analysis #{number} |
| Title | H1, "Analysis Results: {Subsystem Name}" |
| Status Badge | "● Completed" with green dot |
| Run ID | Monospace, "Run ID: #{short_id}" |
| Timestamp | "Finished at {time} {timezone}" |
| Run History Button | Secondary button, opens history modal/drawer |
| Run Again Button | Secondary button with refresh icon |

#### Summary Cards (3 cards)

**Card 1: Requirements Extracted**
| Property | Value |
|----------|-------|
| Icon | Document with arrow |
| Label | "Requirements Extracted" |
| Value | Large number (e.g., "56") |
| Comparison | "+12% vs last run" (green if positive, red if negative) |

**Card 2: Sub-requirements Generated**
| Property | Value |
|----------|-------|
| Icon | Grid/hierarchy icon |
| Label | "Sub-requirements Generated" |
| Value | Large number (e.g., "142") |
| Comparison | "+8% efficiency" |

**Card 3: Overall Quality Score**
| Property | Value |
|----------|-------|
| Icon | Checkmark badge |
| Label | "Overall Quality Score" |
| Value | Score with denominator (e.g., "94/100") |
| Subtext | Quality label: "Excellent Quality" (green), "Good Quality" (blue), "Needs Improvement" (yellow), "Poor Quality" (red) |

**Quality Thresholds:**
- 90-100: Excellent (green)
- 80-89: Good (blue)
- 70-79: Needs Improvement (yellow)
- <70: Poor (red)

#### Operational Metrics Bar

| Metric | Icon | Format | Example |
|--------|------|--------|---------|
| Time Taken | Clock | "{value}s" or "{value}m {value}s" | "4.2s" |
| Est. Cost | Dollar | "${value}" | "$0.08" |
| Energy | Lightning | "{value} Wh" | "1.2 Wh" |

#### Quality Breakdown Panel

| Dimension | Progress Bar | Value |
|-----------|--------------|-------|
| Completeness | Horizontal bar, colored by threshold | "98%" |
| Clarity | Horizontal bar | "92%" |
| Testability | Horizontal bar | "88%" |
| Traceability | Horizontal bar | "100%" |

**Attention Alert:**
- Warning icon + "Attention Needed: {count} items flagged for ambiguity"
- Clickable — scrolls to Quality Issues section

**View Report Link:** Opens detailed quality report modal or separate page

#### Requirements Table

**Header Controls:**
| Control | Type | Function |
|---------|------|----------|
| Search | Text input with icon | Filter by ID or text content |
| Filter | Dropdown button | Filter by Type, Score range, Has issues |
| View Toggle | Icon buttons | Table view / Card view |

**Table Columns:**

| Column | Width | Sortable | Content |
|--------|-------|----------|---------|
| ID | 10% | Yes | Requirement ID, clickable, blue text |
| Requirement Text | 40% | No | Text, truncated with "...", warning icon if has issues |
| Type | 12% | Yes | Badge: Performance, Safety, Functional, Interface |
| Parent ID | 12% | Yes | Parent requirement ID, clickable |
| Score | 10% | Yes | Percentage, color-coded |

**Type Badge Colors:**
- Performance: Blue
- Safety: Orange
- Functional: Gray
- Interface: Purple

**Row States:**
- Default: `--bg-secondary`
- Hover: `--bg-tertiary`
- Selected: Blue left border
- Has Issues: Warning icon before text

**Pagination:**
- "Showing 1-5 of 142 results"
- Page number buttons
- Previous/Next arrows

#### Traceability Focus Panel

**Purpose:** Show parent-child relationship for selected requirement

| Element | Specification |
|---------|---------------|
| Header | Icon + "Traceability Focus" |
| Parent Card | Parent requirement ID + full text |
| Child Indicator | Nested with connector line |
| Selected Requirement | Highlighted, shows issue badge if applicable |

**Interaction:** Updates when user clicks a row in the table

#### Quality Issues Panel

| Element | Specification |
|---------|---------------|
| Header | Icon + "Quality Issues" + count badge (e.g., "3 Critical") |
| Issue Cards | One card per issue |

**Issue Card:**
| Element | Content |
|---------|---------|
| ID | Requirement ID, clickable |
| Badge | Issue type: AMBIGUITY (yellow), UNTESTABLE (red), INCOMPLETE (orange) |
| Description | Brief description of the issue |
| Action Link | "View Suggestion" — expands to show AI suggestion |

**Footer:** "View All Issues" button — opens modal with full list

### 5.3 Export Functionality

**Export Button (Header):**
- Dropdown with options:
  - Export as Markdown
  - Export as Word Document (.docx)
  - Export as CSV
  - Export as JSON
  - Export Full Package (.zip) — includes all formats + quality report

**Export Process:**
1. Click export option
2. Show loading indicator
3. Generate file on backend
4. Trigger browser download

### 5.4 Interactions

| Action | Behavior |
|--------|----------|
| Click requirement row | Select row, update Traceability Focus panel |
| Click requirement ID | Open detail modal with full info |
| Click parent ID | Navigate to parent (scroll if on page, or switch context) |
| Search | Filter table in real-time (debounced 300ms) |
| Filter by type | Show only matching requirements |
| Sort column | Toggle ascending/descending |
| Click "View Suggestion" | Expand issue card to show AI recommendation |
| Click "Run Again" | Navigate to `/upload` with pre-filled configuration |
| Click "New Workflow" | Navigate to `/upload` with fresh form |
| Click "Export" | Show dropdown, trigger download on selection |

---

## 6. Global Components

### 6.1 Header Navigation

**Structure:**
```
[Logo] [App Name]  |  Dashboard  Projects  Settings  |  [Export] [+ New Workflow] [Avatar]
```

| Element | Behavior |
|---------|----------|
| Logo + App Name | Navigate to landing page |
| Dashboard | Navigate to `/dashboard` (overview of all projects) |
| Projects | Navigate to `/projects` (project list) |
| Settings | Navigate to `/settings` |
| Export | Context-dependent — hidden on some pages |
| + New Workflow | Navigate to `/upload` |
| Avatar | Dropdown: Profile, Sign Out (if auth enabled) |

**Active State:** Current page link has blue underline/highlight

### 6.2 Breadcrumb

**Format:** `Level 1 > Level 2 > Current Page`

- Separator: ">" character with horizontal spacing
- All levels except current are clickable links
- Current page is `--text-primary`, others are `--text-secondary`

### 6.3 Buttons

**Primary Button:**
- Background: `--accent-blue`
- Text: White
- Hover: Slightly lighter blue
- Disabled: Gray background, reduced opacity

**Secondary Button:**
- Background: `--bg-tertiary`
- Border: `--border-default`
- Text: `--text-primary`
- Hover: Lighter background

**Ghost Button:**
- Background: Transparent
- Border: `--border-default`
- Text: `--text-primary`
- Hover: `--bg-tertiary` background

**Danger Button:**
- Background: `--accent-red`
- Text: White

### 6.4 Form Inputs

**Text Input:**
- Background: `--bg-tertiary`
- Border: `--border-default`
- Border (focus): `--accent-blue`
- Placeholder: `--text-muted`
- Text: `--text-primary`

**Dropdown:**
- Same styling as text input
- Chevron icon on right
- Dropdown menu: `--bg-secondary` with shadow

### 6.5 Badges/Pills

| Type | Background | Text |
|------|------------|------|
| Status: Completed | `rgba(63, 185, 80, 0.2)` | `--accent-green` |
| Status: Processing | `rgba(56, 139, 253, 0.2)` | `--accent-blue` |
| Status: Failed | `rgba(248, 81, 73, 0.2)` | `--accent-red` |
| Type: Performance | `rgba(56, 139, 253, 0.2)` | `--accent-blue` |
| Type: Safety | `rgba(210, 153, 34, 0.2)` | `--accent-yellow` |
| Type: Functional | `rgba(110, 118, 129, 0.2)` | `--text-secondary` |
| Issue: Critical | `--accent-red` | White |
| Issue: Major | `--accent-yellow` | Dark |
| Issue: Minor | `--text-muted` | White |

### 6.6 Toast Notifications

**Position:** Top-right corner, stacked

**Types:**
| Type | Icon | Border Color |
|------|------|--------------|
| Success | Checkmark | Green |
| Error | X circle | Red |
| Warning | Alert triangle | Yellow |
| Info | Info circle | Blue |

**Behavior:**
- Auto-dismiss after 5 seconds
- Dismissable via X button
- Max 3 visible at once

---

## 7. Interaction Patterns

### 7.1 Loading States

| Context | Loading Indicator |
|---------|-------------------|
| Page load | Full-page skeleton |
| Button action | Spinner inside button, disabled state |
| Table loading | Skeleton rows |
| Panel loading | Spinner centered in panel |
| API call | Toast: "Saving..." |

### 7.2 Empty States

| Context | Message | Action |
|---------|---------|--------|
| No recent workflows | "No workflows yet. Start your first workflow to see results here." | "Start New Workflow" button |
| No search results | "No requirements match your search." | "Clear filters" link |
| No quality issues | "No issues detected. All requirements meet quality standards." | None |

### 7.3 Confirmation Dialogs

**Used for:**
- Cancel running workflow
- Delete workflow/project
- Discard unsaved changes

**Structure:**
- Modal with overlay
- Title: "Are you sure?"
- Description of action
- Cancel (secondary) + Confirm (primary/danger) buttons

### 7.4 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + N` | New workflow |
| `Cmd/Ctrl + E` | Export (on results page) |
| `Esc` | Close modal |
| `Enter` | Confirm dialog |
| `↑ / ↓` | Navigate table rows |
| `Enter` (on row) | Open requirement detail |

---

## 8. Error States & Edge Cases

### 8.1 API Errors

| Error | User Message | Action |
|-------|--------------|--------|
| 400 Bad Request | "Invalid request. Please check your input." | Highlight invalid fields |
| 401 Unauthorized | "Session expired. Please sign in again." | Redirect to login |
| 403 Forbidden | "You don't have permission to access this resource." | Show message, back button |
| 404 Not Found | "Workflow not found. It may have been deleted." | Link to home |
| 500 Server Error | "Something went wrong. Please try again." | Retry button |
| Network Error | "Unable to connect. Check your internet connection." | Retry button |

### 8.2 Workflow Failures

| Failure Point | UI Treatment |
|---------------|--------------|
| Extract fails | Show error on Extract node, log details, offer "Retry" or "Back to Configure" |
| Validate fails after max iterations | Show warning, proceed to results with quality warnings highlighted |
| SSE connection lost | Show reconnecting indicator, auto-retry 3 times, then show "Connection lost" message |

### 8.3 Edge Cases

| Case | Handling |
|------|----------|
| Zero requirements extracted | Show message: "No requirements found in document. Please check the file format or content." |
| Very long requirement text | Truncate in table, full text in detail modal |
| Large file upload | Show progress bar, allow cancel |
| Concurrent edits (future) | Show "Document updated by another user" notification |

---

## 9. Responsive Considerations

**Primary target:** Desktop (1280px+)

**Breakpoints:**
| Name | Width | Adjustments |
|------|-------|-------------|
| Desktop XL | 1440px+ | Default layout |
| Desktop | 1280px - 1439px | Slightly tighter spacing |
| Tablet | 768px - 1279px | Stack columns, hide sidebar |
| Mobile | < 768px | Single column, simplified navigation |

**Tablet Adjustments:**
- Upload page: Stack upload zone above configuration
- Results page: Hide Traceability Focus sidebar, accessible via modal
- Pipeline visualization: Vertical instead of horizontal

**Mobile Adjustments:**
- Full-width components
- Hamburger menu for navigation
- Simplified table (fewer columns, card view default)
- Collapsible panels

---

## Appendix A: Icon Reference

| Icon Name | Usage |
|-----------|-------|
| `upload-cloud` | File upload zone |
| `file-text` | Document/specification |
| `settings-2` | Configuration |
| `play` | Start action |
| `square` | Stop/cancel |
| `check-circle` | Success/complete |
| `alert-triangle` | Warning |
| `x-circle` | Error |
| `clock` | Time |
| `dollar-sign` | Cost |
| `zap` | Energy |
| `download` | Export |
| `plus` | New/add |
| `search` | Search |
| `filter` | Filter |
| `chevron-down` | Expand/dropdown |
| `chevron-right` | Navigate/breadcrumb |
| `external-link` | Open in new tab |
| `refresh-cw` | Retry/refresh |
| `git-branch` | Traceability |
| `list` | Table view |
| `grid` | Card view |

**Icon Library:** Lucide React (recommended) or similar

---

*End of UI/UX Specification*
