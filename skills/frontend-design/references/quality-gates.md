# Quality Gates

Use this before calling UI work done. A gate is an observed verification, not a vibe check; if you cannot verify it, say so. Audit protocol: `assets/audit-report.md`.

## Severity

**P0 / blocker:** inaccessible, broken, or unusable for a real group; data loss; legal risk. Fix before shipping. **P1 / major:** harms comprehension, trust, or task completion; significant responsive breakage. Fix before release. **P2 / minor:** polish, consistency, or edge-case improvement. Fix when possible.

Do not inflate P2s into P0s or hide a P0 among polish. Each finding needs evidence and a fix.

## Gate index

- **[Gate 0 — Brief fit](design-direction.md).** Subject, audience, and job stated; direction from the subject; priority content and action obvious; scope and conventions right. Fail: no organizing idea or buried job.
- **[Gate 1 — Visual design](visual-craft.md).** Clear hierarchy; deliberate type and measure; role-based palette and contrast in both themes; color not alone; intentional layout, imagery, icons, alt. Fail: incoherent hierarchy, type, contrast, or visual language.
- **[Gate 2 — UX and content](ux-patterns.md).** Entry, success, failure, recovery; all states; labeled forms and inline errors; safe destructive actions; consistent navigation; specific copy; no fake proof or dark patterns. Fail: missing failure, empty, or loading states.
- **[Gate 3 — Responsive and touch](responsive-mobile.md).** 320 px no horizontal scroll; phone, tablet, desktop, landscape work; targets ≥44×44 px (AA 24×24) spaced ≥8 px; sticky chrome, safe areas, `dvh`/`svh`, 16 px inputs, images, hover guards. Fail: 320 px scrolls, a primary action is unreachable, or content hides behind fixed chrome.
- **[Gate 4 — Accessibility](accessibility.md).** Semantics; keyboard with no traps; visible, unobscured focus; modal handling; names, alternatives, labels, errors, status; contrast 4.5:1/3:1; color not alone; reflow and zoom; reduced motion, flash, pause, drag alternatives; screen reader tested or gap reported. Fail: keyboard-inaccessible action, contrast failure, invisible focus, or unassociated error.
- **[Gate 5 — Motion](motion.md).** Named purpose; one moment; token durations/easings; transform/opacity only; no layout shift; input never blocked; cancellation; reduced motion keeps the final state; auto-rotation pause; visible focus; mid-range test. Fail: motion blocks input, shifts layout, or ignores reduced motion.
- **[Gate 6 — Performance](implementation.md).** LCP ≤2.5 s, INP ≤200 ms, CLS ≤0.1 at p75 mobile; responsive images with dimensions; LCP image eager; subset fonts; route-split JS within budget; virtualized lists; throttled handlers; no layout thrash; mid-range test. Fail: jank on a mid-range phone or a heavy dependency for a trivial function.
- **[Gate 7 — Code quality](implementation.md).** Conventions and tokens; semantic HTML; no raw values or arbitrary spacing; no `outline: none`, `transition: all`, or `z-index: 9999`; no dead code; clean API and cleanup; no console errors or broken routes; tests; no accessibility regressions. Fail: fights the system, leaks memory, or logs errors.
- **[Gate 8 — Final critique](design-direction.md#critique-prompts).** Logo-removal and subject-swap tests; one-sentence idea; one memorable moment; removal test; long content and 320 px; dark mode and reduced motion; better than the template. Fail: still generated with nothing to remove.

## Definition of done

A UI change is done when it fits the brief and product; has a deliberate direction with one memorable idea; works at 320 px, on a real phone, and on desktop; is keyboard accessible, screen-reader sane, and contrast-compliant; has loading, empty, error, and success states; respects reduced motion and performs on a mid-range device; uses the design system without one-off debt; and reports evidence and known gaps.

If any is false, the work is not done. Say what remains.
