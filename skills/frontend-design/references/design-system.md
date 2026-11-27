# Design System

Use this reference when creating or extending tokens, components, themes, or a design system. A design system is not a component library with a color palette. It is the shared set of decisions that lets a team build consistent interfaces without re-deciding the same things.

## Contents

- [Token architecture](#token-architecture)
- [Color tokens](#color-tokens)
- [Typography tokens](#typography-tokens)
- [Space, layout, and breakpoints](#space-layout-and-breakpoints)
- [Radius, borders, elevation, and layers](#radius-borders-elevation-and-layers)
- [Motion tokens](#motion-tokens)
- [Component contracts](#component-contracts)
- [States](#states)
- [Themes and density](#themes-and-density)
- [Governance](#governance)
- [Handoff and documentation](#handoff-and-documentation)
- [Starter token sheet](#starter-token-sheet)

## Token architecture

Use three layers:

```text
Primitive tokens   -> raw values, never used directly in components
Semantic tokens    -> purpose-based aliases, used in most components
Component tokens   -> optional aliases for a specific component's API
```

Example (illustrative project values, not the starter sheet; the canonical primitives and semantic roles are in `assets/tokens.css`):

```css
/* Primitive: a value */
--blue-500: oklch(0.62 0.16 250);

/* Semantic: a job */
--color-accent: var(--blue-500);
--color-accent-ink: var(--neutral-0);

/* Component: an API */
--button-primary-bg: var(--color-accent);
--button-primary-fg: var(--color-accent-ink);
```

Rules:

- Components use semantic or component tokens, not primitive tokens.
- Raw hex values live only in the primitive layer.
- If a component needs a new value, add a semantic token or a component token; do not hardcode it.
- Tokens are named by role, not by appearance: `--color-danger`, not `--color-red`.
- Keep the token surface small enough to document. A system with 400 tokens nobody understands is not a system.

### Naming

Use a consistent pattern:

```text
--<category>-<role>-<variant>-<state>
```

Examples:

```css
--color-surface
--color-surface-raised
--color-text-muted
--color-border-strong
--color-accent-hover
--space-4
--radius-md
--shadow-2
--duration-fast
--ease-out
--z-modal
```

Avoid abbreviations that only the author understands. Prefer `--color-text-muted` over `--c-tx-m`.

## Color tokens

### Semantic set

Start with this set and add only what the product needs:

```css
--color-canvas
--color-surface
--color-surface-raised
--color-surface-sunken
--color-text
--color-text-muted
--color-text-subtle
--color-border
--color-border-strong
--color-accent
--color-accent-hover
--color-accent-active
--color-accent-ink
--color-accent-subtle
--color-focus
--color-selection
--color-success
--color-success-surface
--color-success-ink
--color-warning
--color-warning-surface
--color-warning-ink
--color-danger
--color-danger-surface
--color-danger-ink
--color-info
--color-info-surface
--color-info-ink
--color-overlay
```

Not every product needs all of these. A marketing page may need six; a dashboard may need twenty. Add roles when they carry meaning, not for completeness.

### Building a scale

Build primitives once as a scale: vary lightness smoothly, keep hue stable, and reduce chroma at the extremes. For neutrals, use a small chroma tinted toward the brand hue; pure gray next to a saturated accent can look dead. OKLCH is optional; the starter sheet uses hex primitives. The canonical primitive and semantic values live in `assets/tokens.css`; extend that file instead of copying a second scale into documentation.

### Semantic mapping

Map primitives to semantic roles once per theme. The canonical light and dark mapping is in `assets/tokens.css`: it defines `--color-canvas`, `--color-surface`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-accent`, `--color-accent-hover`, `--color-accent-active`, `--color-accent-ink`, `--color-focus`, and the semantic state roles. Do not restate those values in another document; update the token sheet and its contrast fixture together.

Prefer explicit theme attributes for user control, and respect `prefers-color-scheme` as the default when no explicit choice is stored. Do not rely on `filter: invert()`.

### Contrast pairs

Validate these pairs in both themes:

- text on canvas;
- text on surface;
- muted text on canvas and surface;
- accent-ink on accent (including hover/active);
- semantic ink on semantic background;
- focus ring against adjacent surfaces;
- borders and dividers against surfaces (3:1 for meaningful boundaries);
- placeholder text if it conveys information;
- disabled text (recognizable, even though WCAG exempts it).

Use `scripts/contrast.py` with a pair file in CI or review.

### Data visualization

Define a separate chart palette:

- categorical: 6–8 hues, similar lightness, colorblind-safe;
- sequential: one hue, light to dark;
- diverging: two hues with a neutral midpoint;
- status: success/warning/danger/info, always paired with icon or label.

Test charts in grayscale and with a colorblind simulator. Do not encode more than the palette can distinguish.

## Typography tokens

`assets/tokens.css` defines the canonical families (`--font-display`, `--font-body`, `--font-mono`), the fluid `--text-*` scale, `--leading-*`, `--tracking-*`, and `--measure` / `--measure-narrow`. The display family in the starter sheet is Archivo. Do not duplicate those values here; extend the token sheet.

Rules:

- Use `rem` for type so user settings and zoom work.
- Use unitless line heights.
- Use `clamp()` for fluid type, but test each step at 320 px and 1440 px.
- Do not create a token for every possible size. Define roles: display, h1, h2, h3, body, small, label, mono.
- Use `font-variant-numeric: tabular-nums` where numbers align.
- Use `font-optical-sizing: auto` for variable optical-size fonts.
- Preload at most one critical font; subset; `font-display: swap` or `optional`.

### Type roles

```css
.type-display { font: 600 var(--text-display)/var(--leading-tight) var(--font-display); letter-spacing: var(--tracking-tight); }
.type-h1      { font: 600 var(--text-3xl)/var(--leading-tight) var(--font-display); }
.type-h2      { font: 600 var(--text-2xl)/var(--leading-snug) var(--font-display); }
.type-h3      { font: 600 var(--text-xl)/var(--leading-snug) var(--font-body); }
.type-body    { font: 400 var(--text-base)/var(--leading-relaxed) var(--font-body); }
.type-small   { font: 400 var(--text-sm)/var(--leading-normal) var(--font-body); }
.type-label   { font: 500 var(--text-sm)/var(--leading-snug) var(--font-body); }
.type-mono    { font: 500 var(--text-sm)/var(--leading-normal) var(--font-mono); font-variant-numeric: tabular-nums; }
```

## Space, layout, and breakpoints

### Space scale

Use a 4 px base with an 8 px rhythm for most UI:

```css
--space-0: 0;
--space-1: 0.25rem;  /* 4 */
--space-2: 0.5rem;   /* 8 */
--space-3: 0.75rem;  /* 12 */
--space-4: 1rem;     /* 16 */
--space-5: 1.25rem;  /* 20 */
--space-6: 1.5rem;   /* 24 */
--space-8: 2rem;     /* 32 */
--space-10: 2.5rem;  /* 40 */
--space-12: 3rem;    /* 48 */
--space-16: 4rem;    /* 64 */
--space-20: 5rem;    /* 80 */
--space-24: 6rem;    /* 96 */
```

Use smaller steps for component internals and larger steps for section rhythm. Do not use every step in every component.

### Containers and gutters

```css
--container-sm: 40rem;
--container-md: 48rem;
--container-lg: 64rem;
--container-xl: 80rem;
--container-2xl: 90rem;
--gutter: clamp(1rem, 4vw, 2.5rem);
--section-space: clamp(3rem, 8vw, 7rem);
```

Cap reading content at `--measure`; cap layout content at a container width. Full-bleed sections can exceed the container, but their inner content should still align to it.

### Breakpoints

Breakpoints are content decisions, not device names. Document them and use consistent values:

```css
/* 30rem = 480px, 48rem = 768px, 64rem = 1024px, 80rem = 1280px */
@media (min-width: 48rem) { /* ... */ }
```

Common starting set: 480, 768, 1024, 1280, 1536 px. A dashboard may need 640 and 1280; a reading site may only need 768. Do not add a breakpoint for every device rumor.

CSS custom properties cannot be used in media queries. Document the values in a comment or use a preprocessor/build-time token if the project supports it.

### Layout tokens

Starter sheet tokens (`assets/tokens.css`):

```css
--container-2xl: 90rem;
--gutter: clamp(1rem, 4vw, 2.5rem);
--measure: 65ch;
--header-height: 4rem;
```

Add optional layout roles (such as sidebar widths) when the product layout needs them. Use `min-height: 100dvh` rather than `100vh` for full-height layouts; `dvh` tracks browser chrome. Test the address bar and on-screen keyboard behavior.

### Z-index scale

```css
--z-base: 0;
--z-raised: 10;
--z-sticky: 100;
--z-dropdown: 200;
--z-overlay: 300;
--z-modal: 400;
--z-toast: 500;
--z-tooltip: 600;
```

Keep the scale small. If a new layer is needed, add it to the system rather than typing `9999`.

## Radius, borders, elevation, and layers

### Radius

Use a scale with hierarchy:

```css
--radius-none: 0;
--radius-xs: 0.125rem;
--radius-sm: 0.25rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1rem;
--radius-2xl: 1.5rem;
--radius-full: 9999px;
```

Not every element needs the same radius. Inputs, buttons, cards, and modals often sit at different levels. A single large radius on everything is a generated-design tell.

### Borders

```css
--border-width: 1px;
--border-width-strong: 2px;
/* Semantic border colors live in assets/tokens.css: --color-border and --color-border-strong */
```

Use borders for structure and grouping; use shadows for elevation, not both at random. In dark mode, borders often do more work than shadows.

### Elevation

`assets/tokens.css` defines `--shadow-1`, `--shadow-2`, and `--shadow-3`. The light shadows are tinted toward the warm background hue rather than pure black. Use one scale; avoid the same soft black shadow on every card. Dark mode uses its own `--shadow-*` overrides and expresses elevation primarily with surface lightness plus borders.

## Motion tokens

`assets/tokens.css` defines the canonical `--duration-*` and `--ease-*` values; `motion.md` maps them to interactions. Use those tokens everywhere. Do not mix 137 ms, 200 ms, and 250 ms transitions in the same component.

## Component contracts

A component is a contract, not a bag of styles. Document:

- anatomy (parts and slots);
- variants (primary, secondary, ghost, danger);
- sizes (sm, md, lg);
- states (default, hover, focus-visible, active, selected, disabled, loading, error, read-only);
- tokens used;
- keyboard behavior;
- ARIA roles and properties;
- content constraints;
- responsive behavior.

### Button

| Property | Guidance |
|---|---|
| Element | `<button>` for actions; `<a>` for navigation |
| Variants | primary, secondary, ghost, danger; no more than needed |
| Sizes | sm 32–36 px, md 40–44 px, lg 48 px |
| States | hover, focus-visible, active, disabled, loading |
| Loading | Preserve width; disable repeated activation; announce busy state |
| Icon-only | Requires accessible name; 44×44 px target |
| Content | Verb-led label; sentence case; no truncation of the action |

Visual button height can be smaller than the touch target. Expand the hit area with padding or a pseudo-element so the interactive target is at least 44×44 px; never ship a 32 px icon-only control with no expanded target.

### Text input

| Property | Guidance |
|---|---|
| Label | Visible, associated with `for`/`id`; not placeholder-only |
| Help | Persistent helper text for format or constraints |
| Error | Inline, specific, linked with `aria-describedby`; `aria-invalid="true"` |
| State | default, focus, filled, disabled, read-only, error |
| Input type | `email`, `tel`, `url`, `number`, `search` as appropriate |
| Autofill | Correct `autocomplete` tokens |
| Mobile | `inputmode`, `enterkeyhint`; at least 16 px text |

### Select, checkbox, radio, switch

- Prefer native controls or a tested headless primitive.
- Give the group a `fieldset`/`legend` or an accessible group label.
- Checkboxes are for independent choices; radios for one-of-many; switches for immediate on/off settings.
- Do not use a switch for a choice that requires a Save action.
- Ensure the label is clickable and the target is at least 44×44 px.

### Dialog

- Use `<dialog>` or a tested primitive with `role="dialog"` and `aria-modal="true"`.
- Provide an accessible name via `aria-labelledby`.
- Move focus into the dialog on open; trap focus; Escape closes; restore focus to the trigger.
- Prevent background scroll without layout shift (`scrollbar-gutter: stable`).
- Confirm before discarding unsaved changes.
- Do not use a modal for primary navigation.

### Menu, tabs, tooltip, toast

- Menu: keyboard arrows, Home/End, Escape; focus returns to trigger.
- Tabs: `role="tablist"`, `role="tab"`, `role="tabpanel"`; arrow-key navigation; selected state.
- Tooltip: hover and focus; dismissible; not the only source of essential information; `aria-describedby`.
- Toast: `aria-live="polite"` or `role="status"`; does not steal focus; dismissible; pause on hover/focus; 3–5 s for simple messages.

### Table

- Use a real `<table>` for tabular data.
- `<caption>` or an associated heading; `<th scope="col">` and `<th scope="row">`.
- Align numbers right with tabular figures.
- Provide a responsive strategy: stacked records, priority columns, or a scroll region with a visible affordance.
- Do not hide essential columns on mobile without a way to reveal them.

### Card

- Use a card only when it groups related content or communicates elevation.
- Do not put every section in a card.
- Make the whole card clickable only when it has one destination; otherwise use a clear link/button.
- If the card is clickable, ensure keyboard focus and a visible focus state.

### Empty, error, loading, success

Design these as first-class components:

- empty: explanation + primary action + optional illustration;
- error: what happened, why, how to recover, retry;
- loading: skeleton matching the final layout, or a progress indicator for longer work;
- success: confirmation of what changed, with a next step or undo where useful.

## States

Every interactive component needs a state matrix:

| State | Visual | Semantic |
|---|---|---|
| Default | Base style | Normal |
| Hover | Subtle change | Pointer only; never the only affordance |
| Focus-visible | 2–3 px ring, 3:1 contrast | Keyboard focus |
| Active/pressed | Slight scale or color shift | Action in progress |
| Selected | Persistent indicator, not color alone | `aria-selected` / `aria-pressed` |
| Disabled | Reduced emphasis, no action | `disabled` or `aria-disabled` |
| Loading | Preserve layout, show progress | `aria-busy` |
| Error | Inline message + icon | `aria-invalid`, `aria-describedby` |
| Read-only | Distinct from disabled | `readonly` |

Do not rely on hover for touch. Do not remove focus styles. Do not animate layout bounds on press.

## Themes and density

### Theme strategy

- Define semantic tokens per theme.
- Use `color-scheme` to tell the browser about form controls and scrollbars.
- Support explicit light/dark/system choice if the product allows it.
- Persist the choice without a flash of the wrong theme (inline script or server-rendered attribute).
- Test both themes for every component, especially borders, shadows, disabled states, and charts.

### Density

Offer comfortable and compact density only if the product needs it. Density changes spacing tokens, not font sizes below readable minimums.

```css
[data-density="compact"] {
  --space-4: 0.75rem;
  --space-6: 1rem;
  --space-8: 1.5rem;
}
```

Do not make compact mode inaccessible: touch targets, focus rings, and text sizes still need to work.

## Governance

A design system decays without rules:

- **Token change process**: propose, review visual impact, update docs, run visual regression.
- **Deprecation**: keep aliases for a migration window; document replacements.
- **Contribution**: new components need anatomy, states, accessibility notes, tests, and a usage example.
- **Audit**: scan for raw hex values, arbitrary spacing, one-off radii, and `!important`.
- **Versioning**: semantic versioning for the package; changelog for visual changes.
- **Ownership**: one named owner or team for the system.
- **Adoption**: measure usage, not just component count.

### Token lint ideas

- No hex colors outside the primitive token file.
- No `px` font sizes in components.
- No `z-index` values outside the scale.
- No `outline: none` without a `:focus-visible` replacement.
- No `transition: all`.
- No `!important` except documented utility exceptions.

## Handoff and documentation

A component is not done until someone else can use it correctly.

Document:

- purpose and when to use / not use;
- anatomy diagram;
- variants and sizes;
- states;
- responsive behavior;
- keyboard and screen-reader behavior;
- content guidance;
- code example;
- do/don't examples;
- accessibility notes;
- related components.

For design-to-code handoff:

- tokens are the source of truth, not screenshots (optionally export W3C Design Tokens Community Group / DTCG JSON with `$value`/`$type` alongside CSS custom properties for multi-platform handoff);
- name components by role, not appearance;
- provide spacing and type specs as tokens, not absolute pixels;
- include error, empty, loading, and long-content examples;
- include dark mode and mobile examples;
- note motion timing and reduced-motion behavior.

## Starter token sheet

`assets/tokens.css` contains a starting point with primitive hex scales, semantic light/dark tokens, the fluid type scale, 4/8 px spacing, containers and breakpoints in comments, radii, borders, shadows, z-index, motion, and base reset/focus styles. Use it as a reference, not a drop-in theme. Replace the brand hue, neutrals, and type families with values that fit the subject. `assets/token-contrast-pairs.json` contains 64 light/dark pairs and 35 semantic combinations covering the starter semantics; run it with:

```bash
python3 scripts/contrast.py --pairs assets/token-contrast-pairs.json --check
```

Update the fixture when you change a token, and check every new pair before shipping.
