# Visual Craft

Use with `design-direction.md` for visual craft. `../assets/tokens.css` is the canonical starter sheet: use its `var(--...)` roles rather than copied values. `design-system.md` covers tokens, components, themes, and handoff.

## Typography

Define roles before sizes: **display** (one expressive moment), **H1**, **H2/H3**, **body** (16–18 px, line-height 1.5–1.7, measure 45–75 ch), **UI label** (14–16 px, medium, sentence case), **small/meta** (12–14 px, legible, never low-contrast filler), and **mono** (code, IDs, timestamps, tabular figures, not prose).

Use one family with multiple weights and widths, or two clearly distinct families. Choose a superfamily for product UI, display plus text for marketing, serif plus sans for long-form, or condensed plus humanist for data-dense work. Choose a licensed family that fits the subject; do not default to Inter. Prefer OFL/Apache, self-host, subset, use `font-display: swap` or `optional`, and preload at most one critical face.

Choose a scale ratio from density: 1.125 compact for dense UI; 1.2 balanced for most apps; 1.25 editorial; 1.333 dramatic for landing pages. Use `rem` and the fluid `--text-*` roles in `../assets/tokens.css`; do not add `--step-*` aliases. Test at 320, 768, and 1440 px: a display size that works at 1440 px may wrap to five lines at 320 px.

Set text deliberately: body line-height 1.5–1.7 (serif can take more), display 1.05–1.2, measure 45–75 characters (about 65 ch; mobile 35–60). Left-align body for LTR, center only short blocks, justify only with hyphenation and support. Use negative tracking for large display, zero for body, positive only for short all-caps labels. Use `text-wrap: balance` for headings and `pretty` for body, and `font-variant-numeric: tabular-nums` for aligned numbers. Avoid all-caps body, fake small caps, gradient or outlined text, and tight tracking on lowercase prose. Do not accent one headline word with italic, bold, or color by default.

Use type as structure only when it encodes real information: a folio number for a numbered sequence, a masthead, a hanging label column, or a width/weight change that signals voice. Decorative numbering is noise.

## Color

A palette is a set of jobs, not swatches: **canvas**, **surface**, **ink**, **muted**, **line**, **accent**, **accent ink**, **focus**, and semantic **success/warning/danger/info**, mapped in `../assets/tokens.css`. Four to six core values suffice.

Choose a seed from the subject's materials: safety orange, oxide red, chlorophyll green, blueprint blue. Build a scale around it. OKLCH is optional; the starter sheet uses hex primitives. Keep hue roughly stable and vary lightness and chroma. Define primitives once and map semantic roles in `../assets/tokens.css`; do not maintain a second mapping in prose.

Tint a neutral toward the brand hue at very low chroma: warm for editorial, cool for technical, green-gray for natural, brown-gray for craft. Do not mix warm and cool neutrals without a reason. Use one accent for action and emphasis; a second is a system decision. If everything is accent-colored, nothing is. The 60-30-10 heuristic is a sanity check, not a law.

Dark mode is a separate tonal system, not an inversion: avoid pure black; lower chroma on large surfaces; desaturate bright accents; express elevation with lighter surfaces and borders, not only shadows; keep semantic colors legible; test contrast independently; design both themes together. Never rely on `filter: invert()`.

Check every text/background pair and meaningful non-text boundary: normal text 4.5:1; large text (≥24 px regular or ≥18.66 px bold) 3:1; UI components, icons, focus indicators, and graphics 3:1; disabled text is exempt but should stay recognizable; placeholders are text and need contrast if informative. Use `scripts/contrast.py` for pairs and palettes, including alpha compositing.

Never use red/green alone for error/success; add an icon, label, or pattern. Use a colorblind-safe categorical palette for charts and test with a simulator. Do not encode more categories than a legend can support, and check cultural associations for the locale.

Avoid the default purple/indigo "tech" palette, pure black and white everywhere, low-contrast gray body text on tinted backgrounds, rainbow or gradient text, neon glows without a subject reason, a different accent per section, and decorative semantic colors.

## Layout and composition

Rank content: what must the user see first to act; second to trust or decide; supporting detail; what can move to another screen. The layout follows this ranking. Do not start with a grid and pour content into it.

Choose a spine: measured column, editorial split, modular or asymmetric grid, dashboard, timeline, full-bleed media, bento, or document. Bento and card grids impose equal weight on unequal content; use them only for true peers.

Use CSS Grid for two dimensions and flexbox for one. A 12-column grid is a useful default for marketing; dashboards often need 4/8/12. Set gutters and margins with tokens. Use `minmax()` and `auto-fit`/`auto-fill` for card grids, but cap max width. Prefer content-driven breakpoints; add one when content breaks. Use container queries for components in different regions.

Whitespace groups and paces: smaller gaps within a group, larger between groups, section spacing visibly larger than component spacing. Avoid uniform padding; it flattens hierarchy. On mobile reduce horizontal margins but keep vertical rhythm; on large screens cap the measure. Match density to the task: gallery (generous, large type), daily app (comfortable, clear groups), cockpit (tight, aligned, tabular numbers, no decorative cards).

Open with the most characteristic thing in the subject's world in the best form: headline, image, animation, live demo, search box, map, or tool. A big number with a small label, stats, and a gradient accent is the default treatment; use it only when truly best. The hero must answer what this is, who it is for, and what I can do now.

Do not shrink the desktop layout; recompose. Convert multi-column sections to a deliberate single-column order. Turn wide tables into stacked records or a scroll region with a clear affordance. Move secondary navigation into a drawer or bottom nav. Keep primary actions within reach. Reduce decorative media before content. Test the order when columns stack. Avoid identical three-card rows, uniform card shadows, centered everything, >80-character lines, fixed-height text, nested scroll, sticky headers over focus, and sidebars that crowd mobile.

## Imagery and iconography

Define subject and crop (product, people, place, detail); aspect ratios per role (hero, card, thumbnail, avatar); treatment (natural, duotone, grain, high contrast); consistency; and licensing. Use real product or context imagery when possible. Avoid generic stock scenes; if you use placeholders, use stable licensed sources, label them, and do not depend on a remote service in production.

Describe alt text by purpose in context, not pixels. Decorative images use `alt=""` and `aria-hidden="true"` where appropriate. Functional images describe destination or action. Complex images need short alt plus a longer description or data table.

Use one icon family and visual style; do not mix filled, outline, rounded, and sharp at the same level. Use a consistent 16/20/24 px grid and stroke width. Icon-only buttons need an accessible name; decorative icons beside text are hidden from the accessibility tree. Do not use emoji as structural icons; they render differently and cannot be themed. Meaningful icons need 3:1 contrast and optical alignment. Keep illustration palette, line weight, detail, and perspective consistent; mixing 3D, flat vectors, and sketches reads as indecision.

## Voice and interface copy

Words are design material; `ux-patterns.md` covers full form, feedback, and content patterns. Choose three voice adjectives such as *plain, warm, precise*. Tone shifts with context; voice stays consistent. Write in user vocabulary with plain language and concrete verbs, active voice, sentence case, one name per thing, important information first, and no filler or marketing superlatives.

CTAs name the outcome: "Save changes" not "Submit"; "Create account" not "Get started"; "See how lending works" not "Learn more". A button that says **Publish** should produce **Published**, not **Success!**.

Errors say what happened, why, and what to do now. Put the message next to the field or action, use specific language not codes alone, do not blame the user or apologize instead of explaining, preserve entered data, and provide a focusable summary plus inline messages for multiple errors. Empty states explain what would be here, why it is empty, and one next action; a sad illustration is not enough. Confirm irreversible actions with the object and consequence, offer undo, separate destructive actions from primary ones, and avoid confirmshaming.

Use realistic, locale-aware formats and tabular figures for aligned data. Label synthetic data. Do not invent testimonials, metrics, or activity, and avoid generic names and placeholder companies.
