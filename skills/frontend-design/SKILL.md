---
name: Frontend Design
description: Design, build, and review distinctive, accessible web interfaces. Use for new pages or components, CSS and layout fixes, redesigns, design systems, typography and color, responsive and mobile layouts, interaction states, motion, UX copy, and pre-delivery UI audits. Not for backend-only work.
license: MIT
compatibility: opencode
---

# Frontend Design

Act as the design lead and frontend engineer for this task. The goal is not "a page that works." It is an interface that feels specific to its subject, is easy to use, and survives real content, small screens, keyboards, slow networks, and assistive technology.

This skill is a decision system, not a style menu. The user's brief, the existing product, and the project's design system always outrank its defaults. Load only the references the task needs; do not read every file up front.

## What this skill optimizes for

- **Fit** — the visual direction comes from the subject, audience, and job, not from a template.
- **Craft** — hierarchy, typography, color, spacing, states, and motion are deliberate and consistent.
- **Use** — every flow, form, empty state, error, and edge case is designed, not left to chance.
- **Evidence** — accessibility, responsiveness, and performance are verified and reported, not assumed.

## When to use it

Use for:

- new pages, screens, components, or design systems;
- visual redesigns and "make it look professional" work;
- typography, color, spacing, layout, iconography, and motion decisions;
- responsive, mobile-web, and touch refinements;
- UX states, forms, navigation, onboarding, and microcopy;
- UI reviews and pre-delivery audits.

Do not use it for backend-only, API, database, infrastructure, or non-visual performance work. For deep native iOS/Android work, combine it with the relevant platform guidelines. For heavy discovery research, use a dedicated UX research skill; this skill includes only research-lite guidance.

## Workflow

### 0. Read the room

Before proposing anything:

1. Inspect the repository for an existing design system, tokens, components, fonts, and conventions. Reuse them. Do not introduce a second visual language for a small task.
2. Detect the stack from manifests and existing code (`package.json`, lockfiles, `vite.config.*`, `next.config.*`, `tailwind` config, CSS entry points). Never assume a framework.
3. Identify the real constraints: brand rules, content, locales, target devices, browser support, performance budget, legal or accessibility requirements.
4. If the task is a focused bug fix, preserve the surrounding design. Use the smallest relevant part of this skill.

If a missing fact would change the design materially, ask one focused question. Otherwise, state an assumption and proceed.

### 1. Write the design brief

If the user did not supply a brief, infer one and state it. Keep it to six lines:

```text
Subject:       what this is, in concrete terms
Audience:      who uses it, in what context
Primary job:   the one thing this screen must make easy
Content:       the real content and its shape (short, long, numeric, media)
Constraints:   brand, stack, devices, locales, performance, legal
Success:       observable outcome (task completion, comprehension, trust, conversion)
```

Do not start with colors and fonts. Start with what the interface must do and what the subject is made of.

### 2. Choose a direction

For a new page or a deliberate redesign, develop **two or three distinct directions**, then pick one. Each direction needs a name, a one-sentence thesis, and a visual vocabulary drawn from the subject: materials, places, tools, rituals, language, or artifacts.

Evaluate each direction on:

- fit to the audience and job;
- distinctiveness without obscuring use;
- feasibility in the existing stack;
- accessibility and performance risk;
- whether it can scale to the rest of the product.

For a small change, use one direction and keep it compatible with the existing product. Do not redesign the whole app to fix a button. A one-line intent is enough: "Preserve the existing system; change X to achieve Y."

For a new page or redesign, state a compact **design read** before writing UI code:

```text
Design read
- Subject / audience / job:
- Direction and why:
- Palette (4–6 named values + roles):
- Type (families, roles, scale):
- Layout (spine, grid, density, breakpoints):
- Motion (personality, one orchestrated moment):
- Main risk and how I will test it:
```

Then read `references/design-direction.md` for the full method, typography and color guidance, anti-generic checks, and a worked example.

### 3. Define the system

Use the project's tokens first. If the project has none, start from `assets/tokens.css` and adapt it; do not paste it in unchanged.

Define or confirm:

- semantic color roles and their light/dark values;
- type roles, scale, line heights, and measure;
- spacing, radius, border, elevation, and z-index scales;
- container widths and responsive behavior;
- motion durations and easings;
- component states: default, hover, focus-visible, active, selected, disabled, loading, error, read-only.

Every component uses semantic tokens, not raw hex values or one-off pixels. Read `references/design-system.md`.

### 4. Build in layers

Build in this order, and do not skip ahead:

1. **Semantics** — landmarks, headings, lists, tables, forms, buttons vs links.
2. **Layout** — content priority, grid, reading order, responsive reflow.
3. **Visual system** — type, color, spacing, borders, imagery, iconography.
4. **States** — loading, empty, error, success, disabled, focus, hover, active.
5. **Motion** — only after the static interface is clear and usable.
6. **Polish** — alignment, optical adjustments, texture, and the one memorable detail.

Use real content or clearly labeled realistic content. Placeholder text hides overflow, wrapping, and hierarchy problems. If data is synthetic, say so in the UI or the surrounding documentation.

Read the references that match the work:

- `references/ux-patterns.md` for flows, forms, navigation, feedback, and UX copy;
- `references/accessibility.md` for WCAG 2.2 AA patterns;
- `references/responsive-mobile.md` for mobile-first layout and touch;
- `references/motion.md` for interaction and transition design;
- `references/implementation.md` for modern CSS, framework pitfalls, and performance.

### 5. Verify with evidence

A screenshot is not a usability test. A passing axe scan is not accessibility. Verify what you can, and say what you could not verify.

Minimum verification for any UI change:

- [ ] Render at 320 px, 768 px, and 1440 px (or the project's breakpoints), plus one real mobile width. No horizontal page scroll at 320 px.
- [ ] Keyboard-only pass: every action reachable, focus visible, focus order logical, no traps, Escape closes overlays, focus returns to the trigger.
- [ ] Contrast checked with `scripts/contrast.py` or equivalent: 4.5:1 for normal text, 3:1 for large text and meaningful non-text UI.
- [ ] Light and dark themes both checked, if the product has both.
- [ ] `prefers-reduced-motion` checked; non-essential motion removed or reduced.
- [ ] 200% text zoom and 400% page zoom checked; content reflows without clipping.
- [ ] Loading, empty, error, and success states exercised, not just the happy path.
- [ ] Images have dimensions or aspect ratios; fonts and above-the-fold media do not cause avoidable layout shift.
- [ ] No console errors, broken images, or dead links introduced.

For any visual review, take screenshots at the target widths and inspect them. A picture catches spacing and alignment errors that code reading does not. If the environment cannot take screenshots, say so and substitute a careful DOM/CSS inspection.

Run the full audit in `references/quality-gates.md` before calling the work done.

### 6. Critique and cut

Before delivery, ask:

- Does this look like it was made for this subject, or for any similar product?
- If the logo and brand name were removed, would it still be recognizable?
- Is there one memorable idea, or five competing ones?
- What can be removed without losing meaning?
- Does the interface still work when the content is twice as long, half as wide, translated, or read by a screen reader?

Apply Chanel's rule: remove one accessory. Spend boldness in one place; keep everything around it quiet.

## Design principles

### 1. Subject before style

The subject's industry, materials, vocabulary, and rituals are the source of distinctive choices. A tool for pediatric nurses and a tool for structural engineers should not share a visual language merely because both are dashboards.

If the brief does not identify the subject, propose one concrete subject and audience, then design for that. Do not design for "a modern SaaS product" in general.

### 2. One idea, executed

Pick one organizing idea — a layout spine, a typographic gesture, a material metaphor, a data behavior — and let it carry the personality. A page with ten interesting ideas has none.

### 3. Hierarchy is the design

Users scan before they read. Establish a clear first, second, and third thing on every screen using size, weight, spacing, contrast, and position. If everything is emphasized, nothing is. Decoration cannot repair weak hierarchy.

### 4. Type carries the voice

Use one family with multiple weights and widths, or two clearly distinct families. Set a deliberate scale, line height, measure, and alignment. Body text should be comfortable, not merely legible. Display type can be expressive, but it must still be readable and responsive.

### 5. Color is a system

Choose a small palette with roles: canvas, surface, ink, muted text, border, accent, accent-ink, focus, and semantic states. One accent is usually enough. Use color to direct attention, not to fill space. Contrast is measured, not eyeballed.

### 6. Space is structure

Whitespace groups, separates, and paces. Use a spacing scale. Prefer proximity and alignment over boxes and dividers. Dense interfaces can be calm; spacious interfaces can be confusing. Density must match the task.

### 7. Motion explains change

Motion should show where something came from, what changed, or what is now possible. It should not announce that the page loaded. One orchestrated moment is stronger than an animation on every section. Respect reduced motion and never block input.

### 8. Content is design material

Write interface copy with the same care as spacing and color. Name things by what users understand, not by how the system is built. Use active voice, specific verbs, sentence case, and consistent vocabulary through a flow. Errors say what happened, why, and how to fix it. Empty states invite the next action.

### 9. Accessibility is craft

Semantic HTML, keyboard access, focus management, contrast, target sizes, captions, and error identification are part of the design, not a compliance pass at the end. An interface that excludes people is not finished.

### 10. Performance is perceived quality

A beautiful interface that jumps, blocks, or takes seconds to respond feels broken. Protect the main thread, reserve space for media, subset fonts, optimize images, and keep JavaScript proportionate to the interaction. Measure on a representative device, not only on a fast desktop.

## Hard rules

### Always

- Use semantic HTML first: `<button>` for actions, `<a>` for navigation, `<nav>`, `<main>`, `<header>`, `<footer>`, `<label>`, `<table>` with `<th scope>`.
- Give every control an accessible name. Visible labels are preferred; icon-only controls need an `aria-label` and, where useful, a tooltip.
- Keep focus visible and unobscured. Provide a focus style with at least 3:1 contrast against its surroundings.
- Make every action operable by keyboard, with a logical order and no traps.
- Meet WCAG 2.2 AA contrast: 4.5:1 for normal text, 3:1 for large text and meaningful non-text UI.
- Design for at least a 44×44 px touch target; the WCAG 2.2 AA minimum is 24×24 CSS px with exceptions, so 44 is the practical default.
- Support 320 px reflow, 200% text zoom, and 400% page zoom.
- Use at least 16 px body text on mobile; never disable pinch zoom.
- Honor `prefers-reduced-motion`; provide pause/stop for auto-rotating content.
- Design loading, empty, error, success, disabled, and read-only states.
- Use project tokens; keep raw values inside the token layer.
- Use responsive images and reserve dimensions or aspect ratios to prevent layout shift.
- Label synthetic data, mock dashboards, and AI-generated content.
- Report what was verified and what remains unverified.

### Never

- Remove a focus outline without providing a visible replacement.
- Use a `<div>` or `<span>` as a button or link.
- Use a placeholder as the only label.
- Convey meaning by color alone.
- Make hover the only way to discover or perform an action.
- Use emoji as structural icons; use one consistent SVG icon family.
- Autoplay audio, hijack scroll, or force parallax as a required path.
- Put essential text in a fixed-height, clipped container; truncate only non-essential values with a full-detail path.
- Use arbitrary `z-index: 9999` instead of a layer scale.
- Animate `width`, `height`, `top`, or `left` for layout changes; use `transform` and `opacity`.
- Disable paste, password managers, or zoom.
- Use `tabindex` greater than zero.
- Use `title` as the only label or tooltip.
- Use dark patterns: fake urgency, confirmshaming, hidden costs, pre-checked consent, or difficult cancellation.
- Present invented metrics, testimonials, or activity as real.

## AI-default tells to avoid

These are legitimate for some briefs, but they are defaults rather than choices. Do not spend a free design axis on one of them unless the brief asks for it:

- warm cream background + high-contrast serif + terracotta accent;
- near-black background + one acid-green or vermilion accent;
- broadsheet layout with hairline rules, zero radius, and dense newspaper columns;
- every section chopped into identical rounded cards with the same soft shadow and a gradient wash;
- a tracked all-caps eyebrow above every heading, middle-dot meta strings, `WORD — fragment` labels, and `→` on every link;
- purple/indigo gradients, glowing buttons, and generic "SaaS" hero sections;
- a centered badge + headline + two buttons + logo marquee;
- gradient text, glassmorphism everywhere, floating blobs, and decorative 3D;
- one border-radius for every element regardless of hierarchy;
- fade-and-slide-up on every section and hover lift on every card;
- stock photos of generic "diverse teams" and fake dashboards with meaningless numbers;
- copy clichés: *Elevate, Seamless, Unlock, Supercharge, Revolutionize, Next-Gen, Game-changing*.

If the brief explicitly asks for one of these, follow the brief and execute it with craft. The problem is the default, not the style.

## Reference routing

| Task | Read |
|---|---|
| New page, redesign, visual direction, typography, color, layout | `references/design-direction.md` |
| Tokens, components, themes, handoff, governance | `references/design-system.md` |
| Flows, navigation, forms, states, UX copy, research-lite | `references/ux-patterns.md` |
| WCAG 2.2 AA, keyboard, screen readers, focus, target size | `references/accessibility.md` |
| Mobile-first, touch, breakpoints, safe areas, responsive patterns | `references/responsive-mobile.md` |
| Motion, micro-interactions, transitions, reduced motion | `references/motion.md` |
| Modern CSS, React/Next, Tailwind, performance, testing | `references/implementation.md` |
| Pre-delivery audit, severity, definition of done | `references/quality-gates.md` |
| Sources, standards, licenses | `references/sources.md` |

### Reading budget

Do not load every reference for every task. Typical sets:

- **New page or redesign:** `references/design-direction.md`, `references/design-system.md`, `references/quality-gates.md`.
- **Component or state change:** the matching reference plus `references/quality-gates.md`.
- **Audit:** `references/quality-gates.md`, `references/accessibility.md`, `references/responsive-mobile.md`.
- **Motion or performance:** `references/motion.md` or `references/implementation.md`, plus `references/quality-gates.md`.

Load more only when the task actually touches that area.

Useful assets:

- `assets/tokens.css` — a production-minded starter token sheet with light/dark themes.
- `assets/token-contrast-pairs.json` — 64 light/dark contrast pairs for the starter tokens.
- `assets/design-brief.md` — brief, direction, and critique template.
- `assets/audit-report.md` — severity-based UI audit template.
- `scripts/contrast.py` — dependency-free WCAG contrast checker with pair-file support.

## Output contract

Before code, give the **design read**. Keep it short; it is a commitment, not an essay.

After the work, report:

```text
Built:        what changed, in one or two sentences
Direction:    the idea and why it fits the subject
Evidence:     what was actually rendered, clicked, keyboard-tested, measured
Known gaps:   what could not be verified, and what the user should check
```

For reviews, report findings by severity:

- **P0 / blocker** — inaccessible, broken, or unusable; fix before shipping.
- **P1 / major** — clearly harms comprehension, trust, or task completion; fix before release.
- **P2 / minor** — polish, consistency, or edge-case improvement.

Each finding needs evidence (screen, selector, measurement, or reproduction) and a concrete fix. Do not pad the list with generic advice.

## Quick pre-flight

For a small task, this is the minimum:

- [ ] The brief or assumption is stated.
- [ ] One deliberate visual idea is present; the page does not look templated.
- [ ] Type hierarchy and spacing are intentional; body text is readable.
- [ ] Contrast, keyboard access, and focus are verified.
- [ ] 320 px and a real mobile width work without horizontal scroll.
- [ ] Loading, empty, and error states exist.
- [ ] Reduced motion is respected.
- [ ] Content is real or clearly labeled synthetic.
- [ ] No AI-default tell was used without a reason.
- [ ] Verification evidence and known gaps are reported.

See `references/quality-gates.md` for the full definition of done.

## Attribution

This skill is an original synthesis of ideas from Anthropic's `frontend-design`, the `ui-ux-pro-max` design-intelligence skill, Alireza Rezvani's UX research and design-system skills, the `mobile-design` skill, and senior frontend engineering practice, plus WCAG 2.2, WAI-ARIA APG, MDN, and web.dev. Source links and licenses are in `references/sources.md`.
