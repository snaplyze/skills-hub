# Design brief and plan

The canonical brief, design-plan, and design-read template. Fill it before writing UI code; keep it short enough to use and specific enough to guide decisions. Delete sections that do not apply.

## 1. Brief

| Field | Answer |
|---|---|
| Subject |  |
| Audience |  |
| Primary job |  |
| Content |  |
| Constraints |  |
| Success |  |

### Assumptions

List anything you inferred because the user did not specify it:

-
-

### Non-goals

What this work deliberately does not change:

-
-

## 2. Direction

### Options considered

| Name | Thesis | Fit | Distinctiveness | Risk |
|---|---|---|---|---|
| A |  |  |  |  |
| B |  |  |  |  |
| C |  |  |  |  |

### Chosen direction

- **Name:**
- **Thesis:** For [audience] who need [job], this should feel like [metaphor], expressed through [three devices].
- **Spine:**
- **Why it fits:**
- **Why it might fail:**
- **What would make it generic:**

### Design read

```text
Subject / audience / job:
Direction and why:
Palette (4–6 named values + roles):
Type (families, roles, scale):
Layout (spine, grid, density, breakpoints):
Motion (personality, one orchestrated moment):
Main risk and how I will test it:
```

## 3. System

### Color

| Token | Value | Role | Contrast checked against |
|---|---|---|---|
| `--color-canvas` |  |  |  |
| `--color-surface` |  |  |  |
| `--color-text` |  |  |  |
| `--color-text-muted` |  |  |  |
| `--color-border` |  |  |  |
| `--color-accent` |  |  |  |
| `--color-accent-ink` |  |  |  |
| `--color-focus` |  |  |  |

Dark mode notes:

-

### Typography

| Role | Family | Size | Weight | Line height | Tracking |
|---|---|---|---|---|---|
| Display |  |  |  |  |  |
| H1 |  |  |  |  |  |
| H2 |  |  |  |  |  |
| Body |  |  |  |  |  |
| Label |  |  |  |  |  |
| Mono |  |  |  |  |  |

Measure: `___ch`. Font loading: `___`.

### Space and layout

- Base unit:
- Spacing scale:
- Container:
- Gutter:
- Section spacing:
- Breakpoints:
- Density:

### Radius, border, elevation, motion

- Radius:
- Borders:
- Shadows:
- Z-index layers:
- Motion durations/easings:
- One orchestrated motion moment:

## 4. Wireframe

```text
+--------------------------------------------------+
|                                                  |
|                                                  |
|                                                  |
+--------------------------------------------------+
```

## 5. States

| State | What it looks like | How it is announced |
|---|---|---|
| Loading |  |  |
| Empty |  |  |
| Error |  |  |
| Success |  |  |
| Disabled |  |  |
| Focus |  |  |

## 6. Responsive plan

| Width | Layout change |
|---|---|
| 320 px |  |
| 390 px |  |
| 768 px |  |
| 1024 px |  |
| 1440 px |  |

## 7. Risks and unknowns

- What could make the direction fail?
- What is assumed rather than evidenced?
- What remains unverified?

## 8. Verification and critique

Plan and run the gates in `../references/quality-gates.md`; record results in `audit-report.md`. Use the critique prompts in `../references/design-direction.md#critique-prompts`. Do not duplicate those checklists here.
