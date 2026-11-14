# Sources, Standards, and Licenses

This skill is an original synthesis. It distills ideas, heuristics, and standards from the sources below without reproducing their text wholesale. Where a source has a license, the license is noted. The skill's own text is MIT-licensed as part of this repository.

## Primary inspiration

| Source | What informed this skill | License |
|---|---|---|
| [Anthropic — frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Subject-grounded aesthetic direction, anti-generic visual tells, typography and layout principles, two-pass design planning, restraint, interface writing | Apache-2.0 |
| [nextlevelbuilder — ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/main/.claude/skills/ui-ux-pro-max) | UX rule categories, accessibility and interaction checklists, style taxonomy, component and stack guidance, pre-delivery discipline | MIT |
| [Alireza Rezvani — ux-researcher-designer](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/skills/ux-researcher-designer) | Research-lite methods: personas, journey maps, usability tests, synthesis, severity | MIT |
| [Alireza Rezvani — ui-design-system](https://github.com/alirezarezvani/claude-skills/tree/main/product-team/skills/ui-design-system) | Token architecture, type scales, spacing systems, component contracts, responsive tokens, handoff | MIT |
| [Alireza Rezvani — senior-frontend](https://github.com/alirezarezvani/claude-skills/tree/main/engineering-team/skills/senior-frontend) | Performance budgets, rendering profiles, bundle discipline, accessibility and framework review | MIT |
| [sickn33 — mobile-design](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/mobile-design) | Mobile-first constraints, touch psychology, platform conventions, mobile performance, release checklist | See repository |
| [addyosmani — frontend-ui-engineering](https://github.com/addyosmani/agent-skills/tree/main/skills/frontend-ui-engineering) | Production UI engineering, AI-aesthetic avoidance, component architecture, state and verification | MIT |
| [Leonxlnx — taste-skill](https://github.com/Leonxlnx/taste-skill) | Anti-generic layout and typography constraints, motion and density dials, performance guardrails | See repository |

## Standards and canonical references

| Reference | Use in this skill |
|---|---|
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Accessibility criteria, conformance targets, target size, reflow, focus, authentication |
| [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) | Keyboard and ARIA patterns for menus, tabs, dialogs, comboboxes, grids |
| [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/) | Roles, states, properties, accessible names |
| [MDN Web Docs](https://developer.mozilla.org/) | HTML, CSS, and browser API accuracy |
| [web.dev — Core Web Vitals](https://web.dev/articles/vitals) | LCP, INP, CLS thresholds and optimization |
| [web.dev — Learn Performance](https://web.dev/learn/performance) | Loading, rendering, and runtime performance |
| [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) | Touch targets, platform conventions, motion, typography |
| [Material Design 3](https://m3.material.io/) | Touch targets, state layers, adaptive layout, motion |
| [Inclusive Components](https://inclusive-components.design/) | Accessible component patterns |
| [The Elements of Typographic Style](https://en.wikipedia.org/wiki/The_Elements_of_Typographic_Style) | Type scale, measure, rhythm, typographic craft |
| [Nielsen Norman Group](https://www.nngroup.com/) | Heuristics, usability testing, interaction patterns |
| [Laws of UX](https://lawsofux.com/) | Fitts's law, Hick's law, Jakob's law, and related principles |
| [Refactoring UI](https://www.refactoringui.com/) | Hierarchy, spacing, color, depth, and practical UI craft |

## Standards notes

- **Target size:** WCAG 2.2 AA (2.5.8) requires 24×24 CSS px with exceptions; 44×44 CSS px is AAA (2.5.5) and the practical design default. Apple recommends 44×44 pt; Material recommends 48×48 dp. Do not treat one platform's unit as a web conformance rule.
- **Contrast:** WCAG 2.2 AA requires 4.5:1 for normal text and 3:1 for large text and meaningful non-text UI. APCA is a newer perceptual model but is not a WCAG 2.2 conformance requirement; do not present it as a substitute.
- **Focus appearance:** 2.4.13 is AAA. The AA requirements are 2.4.7 (visible focus) and 2.4.11 (focus not obscured). A strong 2–3 px indicator is good practice.
- **Motion:** 2.3.3 (animation from interactions) is AAA. `prefers-reduced-motion` is a best practice and a practical requirement for vestibular safety.
- **AI disclosure:** labeling synthetic content and AI-generated media is a trust and safety practice; specific legal requirements vary by jurisdiction.
- **Performance:** Core Web Vitals thresholds are field-data targets at p75. Lab scores are diagnostic, not a guarantee.

## Scope note

This skill is design and engineering guidance, not legal advice. Accessibility, privacy, consent, advertising, and AI-disclosure requirements vary by jurisdiction and industry. Verify the applicable rules with the project's legal or compliance owner.

## License compliance

- The Anthropic `frontend-design` skill is licensed under Apache-2.0. This repository does not include its source text; it cites the skill and synthesizes its ideas.
- The `ui-ux-pro-max`, Alireza Rezvani, and addyosmani skills are MIT-licensed. Their ideas are cited; no substantial text is copied.
- The `mobile-design` and `taste-skill` sources carry their own repository terms. Consult the upstream repositories before redistributing their text or assets.
- All trademarks, product names, and brand assets belong to their respective owners.
- If you contribute adapted text from another source, add it to this file with the license and a link.

## How to update this skill

When updating:

1. Check the current WCAG recommendation and the WAI-ARIA APG for changed guidance.
2. Re-check browser support for modern CSS features before presenting them as baseline.
3. Re-check platform target-size guidance; do not conflate pt, dp, and CSS px.
4. Keep the skill's own voice and structure; do not paste large source excerpts.
5. Run the validation steps in the repository README: frontmatter, internal links, contrast script, and installer dry run.
