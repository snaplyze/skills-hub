# Design brief and plan

Canonical brief, design-plan, and design-read template. Fill before coding; delete sections that do not apply.

## 1. Brief

- **Subject / Audience / Primary job:**
- **Content / Constraints / Success:**
- **Assumptions (inferred):**
- **Non-goals:**

## 2. Direction

Options considered (`A / B / C` — name, thesis, fit, distinctiveness, risk):

- **Chosen direction:** name, spine, why it fits, why it might fail, what would make it generic.
- **Thesis:** For [audience] who need [job], this should feel like [metaphor], expressed through [three devices].

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

- **Color tokens** (value, role, contrast pair): `--color-canvas`, `--color-surface`, `--color-text`, `--color-text-muted`, `--color-border` (decorative), `--color-border-strong` (3:1 UI boundaries), `--color-accent`, `--color-accent-ink`, `--color-focus`; dark mode notes.
- **Typography:** Display, H1, H2/H3, Body, Label, Mono (family, size, weight, line-height, tracking); measure `___ch`; font loading `___`.
- **Space & layout:** base unit, scale, container, gutter, section spacing, breakpoints, density.
- **Radius, borders, shadows, z-index, motion:** tokens + one orchestrated motion moment.

## 4. Wireframe & states

Sketch the primary layout spine, then specify **States** (loading, empty, error, success, disabled, focus — appearance + announcement) and **Responsive changes** across `320 / 390 / 768 / 1024 / 1440 px`.

## 5. Risks & verification

- Risks, unverified assumptions, and unknowns.
- Run gates in `references/quality-gates.md`, record evidence in `assets/audit-report.md`, and run critique prompts from `references/design-direction.md`.
