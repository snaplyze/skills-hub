# Quality Gates

Use this reference before calling UI work done. A gate is not a vibe check. It is a concrete verification with an observed result. If you cannot verify something, say so rather than implying it passed.

## Contents

- [Severity](#severity)
- [Gate 0: Brief fit](#gate-0-brief-fit)
- [Gate 1: Visual design](#gate-1-visual-design)
- [Gate 2: UX and content](#gate-2-ux-and-content)
- [Gate 3: Responsive and touch](#gate-3-responsive-and-touch)
- [Gate 4: Accessibility](#gate-4-accessibility)
- [Gate 5: Motion](#gate-5-motion)
- [Gate 6: Performance](#gate-6-performance)
- [Gate 7: Code quality](#gate-7-code-quality)
- [Gate 8: Final critique](#gate-8-final-critique)
- [Audit protocol](#audit-protocol)
- [Audit report template](#audit-report-template)
- [Definition of done](#definition-of-done)

## Severity

| Severity | Definition | Action |
|---|---|---|
| **P0 / blocker** | Inaccessible, broken, or unusable for a real group of users; data loss; legal risk | Fix before shipping |
| **P1 / major** | Clearly harms comprehension, trust, or task completion; significant responsive breakage | Fix before release |
| **P2 / minor** | Polish, consistency, or edge-case improvement; does not block the task | Fix when possible |

Do not inflate P2s into P0s. Do not hide a P0 in a list of minor polish. Each finding needs evidence and a fix.

## Gate 0: Brief fit

- [ ] The subject, audience, and primary job are stated.
- [ ] The design direction follows from the subject, not a template.
- [ ] The most important content is visually first.
- [ ] The primary action is obvious and reachable.
- [ ] The page does not look like it could belong to any competitor.
- [ ] Existing brand and product conventions are respected, or the deviation is justified.
- [ ] The scope matches the request; a button fix did not become a redesign.

**Fail if:** the design has no organizing idea, the hero is generic, or the primary job is buried.

## Gate 1: Visual design

### Hierarchy

- [ ] There is a clear first, second, and third thing on each screen.
- [ ] Size, weight, spacing, and contrast reinforce the same hierarchy.
- [ ] Section spacing is visibly larger than component spacing.
- [ ] The eye is not pulled in five directions.

### Typography

- [ ] One or two families with clear roles.
- [ ] A deliberate scale, not arbitrary sizes.
- [ ] Body measure 45–75 characters; mobile 35–60.
- [ ] Line height 1.5–1.7 for body; tighter for display.
- [ ] No all-caps body, gradient text, or tight tracking on prose.
- [ ] No single-word accent in a headline as a default gimmick.
- [ ] Numbers align with tabular figures where needed.
- [ ] Text wraps at 320 px without clipping or overflow.

### Color

- [ ] Palette has roles, not just swatches.
- [ ] One accent carries action/emphasis.
- [ ] Contrast checked in light and dark themes.
- [ ] Color is not the only indicator of meaning.
- [ ] No default purple gradient, neon glow, or rainbow without a subject reason.
- [ ] Images and overlays do not undermine text contrast.

### Layout

- [ ] Grid and alignment are intentional; edges line up.
- [ ] Whitespace groups and separates.
- [ ] Density matches the task.
- [ ] Cards are used for grouping/elevation, not as a default wrapper.
- [ ] No identical three-card feature row unless the content is truly three peers.
- [ ] No one-radius-for-everything.
- [ ] The composition has one deliberate asymmetry or focal point, not accidental misalignment.

### Imagery and icons

- [ ] Images are subject-specific and consistently treated.
- [ ] Icons come from one family with consistent stroke/size.
- [ ] No emoji as structural icons.
- [ ] Decorative images are hidden from assistive tech.
- [ ] Meaningful images have useful alt text.
- [ ] Brand assets are official and correctly proportioned.

**Fail if:** the hierarchy is unclear, the type is unreadable, contrast fails, or the visual language is incoherent.

## Gate 2: UX and content

- [ ] The primary flow has entry, success, failure, and recovery states.
- [ ] Loading, empty, error, success, disabled, and read-only states are designed.
- [ ] Forms have visible labels, help text, and inline errors.
- [ ] Errors are specific and say how to recover.
- [ ] Destructive actions are confirmed and reversible where possible.
- [ ] Navigation is consistent; current location is clear.
- [ ] Back behavior preserves state and scroll.
- [ ] Content is specific, plain, and consistent through the flow.
- [ ] CTAs name the outcome.
- [ ] No filler, jargon, or AI copy clichés.
- [ ] No fake data, testimonials, metrics, or urgency.
- [ ] No dark patterns.
- [ ] Long content, empty content, and translated content have been considered.

**Fail if:** the happy path works but failure/empty/loading states do not.

## Gate 3: Responsive and touch

- [ ] 320 px: no horizontal page scroll; content reflows.
- [ ] 360–390 px: real phone layout works; bottom nav and keyboard checked.
- [ ] 768 px: tablet layout works; touch targets remain comfortable.
- [ ] 1024/1440 px: desktop layout uses space well; reading measure capped.
- [ ] Landscape phone: height-constrained layout works.
- [ ] Touch targets ≥ 44×44 px (WCAG AA minimum 24×24 with exceptions).
- [ ] At least 8 px between adjacent targets.
- [ ] Sticky bars do not cover content or focus.
- [ ] Safe-area insets respected.
- [ ] `100dvh`/`100svh` used instead of `100vh` for full-height sections.
- [ ] Inputs are ≥16 px on mobile.
- [ ] Images have dimensions and responsive sources.
- [ ] Hover-only styles are guarded with `@media (hover: hover)`.

**Fail if:** the page scrolls horizontally at 320 px, a primary action is unreachable on mobile, or content is hidden behind fixed chrome.

## Gate 4: Accessibility

- [ ] Semantic landmarks and heading hierarchy.
- [ ] All actions keyboard operable; no traps.
- [ ] Visible focus everywhere; focus not obscured.
- [ ] Focus order matches visual order.
- [ ] Modals/dialogs trap focus, close on Escape, and restore focus.
- [ ] Every control has an accessible name.
- [ ] Icon-only buttons have labels.
- [ ] Images have appropriate alt text; decorative images hidden.
- [ ] Forms have labels, instructions, and linked errors.
- [ ] Errors are announced and associated with fields.
- [ ] Status messages use live regions without moving focus.
- [ ] Contrast: 4.5:1 normal, 3:1 large/non-text.
- [ ] Color is not the only indicator.
- [ ] Reflow at 320 px and 400% zoom.
- [ ] Text spacing changes do not clip content.
- [ ] Reduced motion respected.
- [ ] No flashing above three times per second.
- [ ] Auto-rotating content has pause/stop.
- [ ] Dragging has a non-drag alternative.
- [ ] Tested with keyboard and at least one screen reader, or the gap is reported.

**Fail if:** any primary action is inaccessible by keyboard, contrast fails, focus is invisible, or a form error is not programmatically associated.

## Gate 5: Motion

- [ ] Every animation has a named purpose.
- [ ] One orchestrated moment, not effects on every section.
- [ ] Durations/easings come from tokens.
- [ ] Entrances ease-out; exits ease-in and are faster.
- [ ] Only transform/opacity animate for movement.
- [ ] No layout shift or CLS from animation.
- [ ] Input is never blocked.
- [ ] Rapid state changes cancel prior animations.
- [ ] Reduced motion removes non-essential motion and keeps the final state.
- [ ] Auto-rotating content pauses on focus/hover and under reduced motion.
- [ ] Focus remains visible during and after transitions.
- [ ] Tested on a mid-range mobile device.

**Fail if:** motion blocks input, causes layout shift, or ignores reduced motion.

## Gate 6: Performance

- [ ] LCP target defined and checked (target ≤2.5 s p75 mobile).
- [ ] INP target defined and checked (target ≤200 ms p75).
- [ ] CLS target defined and checked (target ≤0.1 p75).
- [ ] Images use modern formats, responsive sizes, and dimensions.
- [ ] LCP image is not lazy-loaded; below-fold images are.
- [ ] Fonts are subset, `font-display` set, and at most one critical font preloaded.
- [ ] JS is route-split; no unnecessary heavy dependencies.
- [ ] Long lists are virtualized where needed.
- [ ] High-frequency handlers are debounced/throttled.
- [ ] No layout thrash or long tasks on the main thread.
- [ ] Third-party scripts are audited and deferred.
- [ ] Bundle size is within the project's budget.
- [ ] Tested on a mid-range device with CPU/network throttling.

**Fail if:** the page is visibly janky on a mid-range phone, the LCP image is lazy-loaded, or a heavy dependency is added for a trivial function.

## Gate 7: Code quality

- [ ] Follows project conventions and design tokens.
- [ ] Semantic HTML; no div buttons.
- [ ] No raw hex values or arbitrary spacing in components.
- [ ] No `outline: none`, `transition: all`, or `z-index: 9999`.
- [ ] No unused CSS, JS, or dead components.
- [ ] Component API is clear and composable.
- [ ] State is in the simplest appropriate place.
- [ ] Effects/listeners/observers are cleaned up.
- [ ] No console errors or warnings introduced.
- [ ] No broken images, links, or routes.
- [ ] Tests cover the new behavior.
- [ ] No accessibility regressions in the component library.
- [ ] The code is readable without comments explaining every line.

**Fail if:** the implementation fights the design system, leaks memory, or introduces console errors.

## Gate 8: Final critique

- [ ] Remove the logo: is it still recognizable?
- [ ] Swap the subject with a competitor: does it still fit? If yes, it is generic.
- [ ] Can you name the organizing idea in one sentence?
- [ ] Is there one memorable moment, or five competing ones?
- [ ] What can be removed without losing meaning? Remove it.
- [ ] Does it survive twice the text, no images, and a 320 px screen?
- [ ] Does it work in dark mode and with reduced motion?
- [ ] Would a skeptical senior designer defend it without saying "it looks clean"?
- [ ] Are the bold choices concentrated, or spread thin?
- [ ] Is the result better than the obvious template? If not, revise.

**Fail if:** the answer to "what would make this feel handmade rather than generated?" is "nothing."

## Audit protocol

### 1. Freeze the scope

List the screens, components, and states in scope. Do not audit the whole app when the change is one flow.

### 2. Capture evidence

Take screenshots at:

- 320 px, 375/390 px, 768 px, 1024 px, 1440 px;
- light and dark themes;
- default, loading, empty, error, and success states;
- 200% text zoom;
- reduced motion.

If you cannot screenshot, inspect the DOM/CSS and state the limitation.

### 3. Test interactions

- Keyboard-only pass: Tab, Shift+Tab, Enter, Space, arrows, Escape.
- Form pass: submit empty, submit invalid, submit valid, network error, double submit.
- Modal pass: open, focus, Escape, close, focus restore.
- Navigation pass: back, deep link, refresh, scroll restore.
- Responsive pass: resize, rotate, keyboard open, zoom.

### 4. Measure

- Contrast with `scripts/contrast.py`.
- Lighthouse/axe if available.
- Bundle size if relevant.
- Core Web Vitals in the lab; field data if available.
- Target sizes with DevTools.

### 5. Report

Use the template below. Separate observed facts from judgments. Do not claim a check you did not run.

## Audit report template

```markdown
# UI audit: [screen/flow]

## Scope
- Screens:
- States:
- Viewports:
- Themes:
- Browser/device:

## Summary
- P0:
- P1:
- P2:
- Overall recommendation:

## Findings

### P0 — [title]
- **Where:** [screen / selector / component]
- **Evidence:** [screenshot, measurement, reproduction]
- **Impact:** [who is blocked and how]
- **Fix:** [concrete change]
- **Verified after fix:** [yes/no/not run]

### P1 — [title]
...

### P2 — [title]
...

## Checks performed
- [ ] Keyboard
- [ ] Screen reader
- [ ] Contrast
- [ ] 320 px reflow
- [ ] 200% zoom
- [ ] Reduced motion
- [ ] Dark mode
- [ ] Loading/empty/error
- [ ] Performance

## Checks not performed
- ...

## Notes
- Assumptions:
- Follow-ups:
```

## Definition of done

A UI change is done when:

1. It fits the brief and the existing product.
2. It has a deliberate visual direction with one memorable idea.
3. It works at 320 px, on a real phone, and on desktop.
4. It is keyboard accessible, screen-reader sane, and contrast-compliant.
5. It has loading, empty, error, and success states.
6. It respects reduced motion and performs acceptably on a mid-range device.
7. It uses the design system and adds no one-off debt.
8. The verification evidence is reported, and known gaps are explicit.

If any of these is not true, the work is not done. Say what remains.
