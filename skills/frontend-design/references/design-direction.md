# Design Direction

Use this reference for new pages, redesigns, visual identity work, and any task where "make it look good" is part of the job. The goal is a direction that could only belong to this subject — not a style applied from the outside.

## Contents

- [The brief](#the-brief)
- [Direction method](#direction-method)
- [Three directions, one choice](#three-directions-one-choice)
- [The design plan](#the-design-plan)
- [Typography](#typography)
- [Color](#color)
- [Layout and composition](#layout-and-composition)
- [Imagery and iconography](#imagery-and-iconography)
- [Voice and interface copy](#voice-and-interface-copy)
- [Anti-generic audit](#anti-generic-audit)
- [Worked example: the tool library](#worked-example-the-tool-library)
- [Critique prompts](#critique-prompts)

## The brief

A design brief is not a feature list. It is a statement of subject, audience, job, content, constraints, and success. If the user gives you only a feature list, infer the rest and say so.

| Field | Question | Bad | Good |
|---|---|---|---|
| Subject | What is this, concretely? | "A platform" | "A neighborhood tool-lending library" |
| Audience | Who uses it, in what context? | "Users" | "Renters and homeowners within walking distance, often on a phone, often not technical" |
| Primary job | What must this screen make easy? | "Browse" | "Find whether a specific tool is available this weekend and reserve it in under two minutes" |
| Content | What is the real content shape? | "Some cards" | "42 tools with photos, availability windows, replacement values, and pickup instructions" |
| Constraints | What cannot change? | "Make it modern" | "Mobile-first, existing green brand, no budget for custom photography, WCAG 2.2 AA" |
| Success | What observable outcome counts? | "Looks better" | "A first-time user can reserve a drill without help; no horizontal scroll at 320 px" |

Write the brief before choosing colors. If you cannot state the primary job in one sentence, the design has nothing to organize around.

## Direction method

### 1. Write a thesis

Complete this sentence:

> For **[audience]** who need **[job]**, this interface should feel like **[concrete metaphor or material]**, expressed through **[three visual devices]**.

Examples:

- "For neighbors borrowing tools, this should feel like a well-kept pegboard: labeled bins, hooks, safety orange, and everything visible at a glance."
- "For a research archive, this should feel like a reading room: warm paper, precise rules, quiet typography, and no decorative noise."
- "For a live incident console, this should feel like a flight deck: dense data, monospaced numbers, calm surfaces, and unambiguous status."

The metaphor is a source of decisions, not a costume. If it starts to fight the job, change the metaphor.

### 2. Build a visual vocabulary

Collect concrete material from the subject's world:

- **Objects**: tools, labels, tickets, ledgers, seed packets, control panels, instruments.
- **Places**: workshop, library, market, studio, laboratory, station, field.
- **Materials**: paper, canvas, cork, steel, glass, clay, ink, fabric.
- **Language**: the words people in this domain actually use.
- **Rituals**: how the work gets done, what gets checked, what gets signed.
- **References**: print, signage, industrial design, film, fashion, architecture, music.

Then translate the vocabulary into design axes:

| Axis | Low end | High end | Use for |
|---|---|---|---|
| Density | Airy, gallery-like | Packed, cockpit-like | Matching the task's information load |
| Temperature | Cool, clinical | Warm, organic | Setting emotional tone |
| Contrast | Soft, tonal | Stark, graphic | Energy and legibility |
| Geometry | Rounded, organic | Rigid, orthogonal | Material personality |
| Era | Historical, analog | Futuristic, technical | Cultural positioning |
| Energy | Calm, still | Kinetic, loud | Brand expression |
| Finish | Utilitarian, raw | Refined, luxurious | Perceived value |
| Familiarity | Conventional | Experimental | Risk tolerance |

Choose a position on each axis. A direction is a set of positions, not a mood board.

### 3. Find the spine

The spine is the one organizing idea that shapes layout, type, color, and motion. Examples:

- a **pegboard** with labeled bins and hooks;
- a **newspaper front page** with columns and a masthead;
- a **lab notebook** with ruled margins and specimen labels;
- a **departure board** with rows, times, and status;
- a **seed catalog** with plates, captions, and botanical names;
- a **control room** with panels, gauges, and a strict grid;
- a **reading room** with a measured column and generous margins.

The spine should be visible in the wireframe before you write CSS. If you cannot draw it, it is not a direction yet.

#### Direction archetypes

Use these as reference points after you have a thesis, not as a menu. Two projects in the same archetype should still look different because their subjects, content, and audiences differ.

| Archetype | Spine | Type | Color and material | Best for | Main risk |
|---|---|---|---|---|---|
| **Reading room** | Measured column, margins, footnotes | Text serif + neutral sans | Paper, ink, one quiet accent | Publishing, research, docs, long-form | Becomes beige and forgettable |
| **Workshop** | Pegboard, bins, labels, visible tools | Condensed grotesque + mono | Galvanized gray, safety color, ink | Tools, repair, making, logistics | Becomes costume without real utility |
| **Institutional** | Strict grid, rules, numbered sections | Neo-grotesque, few weights | White, ink, one signal color | Government, finance, healthcare | Cold and bureaucratic |
| **Field guide** | Plates, captions, specimen labels | Humanist sans + text serif | Earth pigments, paper, botanical green | Nature, wellness, education, food | Slides into generic "organic" |
| **Control room** | Dense panels, gauges, status rows | Condensed sans + tabular mono | Dark surfaces, luminous status | Dashboards, ops, monitoring | Unreadable density and alarm fatigue |
| **Atelier** | Generous space, one dramatic object | Display serif or refined grotesque | Off-white, deep neutral, metallic accent | Luxury, fashion, architecture, beauty | Style over substance; inaccessible contrast |
| **Toybox** | Chunky modules, playful geometry | Rounded display + friendly sans | Bright primaries, soft surfaces | Kids, games, creative tools, community | Clutter and low credibility |
| **Archive** | Index cards, catalog numbers, tabs | Mono + grotesque | Kraft, ink, faded color | Culture, music, collections, portfolios | Nostalgia without navigation |
| **Terminal** | Monospaced grid, command surface | Mono + grotesque | Near-black, phosphor accent | Developer tools, security, data | Novelty hurts readability |
| **Market stall** | Handbills, price tags, stacked goods | Bold display + humanist body | Saturated color, paper, ink | Retail, food, local commerce, events | Chaos without hierarchy |

Pick an archetype, then push it through the subject's specific vocabulary. "Workshop" is not a direction; "a pegboard for a neighborhood tool library, with bin codes and safety-orange availability tags" is.

### 4. Define the devices

A direction becomes executable when it specifies devices:

- **Grid**: how many columns, what gutters, where the content sits, where it breaks.
- **Type**: families, roles, scale, weights, widths, alignment, measure.
- **Color**: 4–6 named values with roles, plus semantic states.
- **Surface**: borders, radii, shadows, texture, translucency, or none.
- **Imagery**: crop, aspect ratio, treatment, color grade, illustration style.
- **Icons**: family, stroke, size grid, filled/outline discipline.
- **Motion**: one entrance moment, feedback behavior, easing personality.

### 5. Test the thesis against the job

Ask:

- Does the direction make the primary job easier, or merely more interesting?
- Does it survive the densest screen, the longest content, and the smallest viewport?
- Can a new team member extend it without guessing?
- Does it require effects or assets the project cannot afford?
- Does it still work in dark mode, at 200% zoom, and with reduced motion?

A direction that only works on a desktop hero is a poster, not a product.

## Three directions, one choice

For a new page or a deliberate redesign, generate three directions with different risk profiles. Do not generate three variations of the same idea.

| Direction | What it is | When to use |
|---|---|---|
| **Grounded** | The category's conventions, made specific with one strong device | Most product UI, dashboards, forms, B2B |
| **Adjacent** | Borrows a visual system from a neighboring domain | Brands that need differentiation without confusion |
| **Wildcard** | A high-concept direction with a strong organizing metaphor | Portfolios, campaigns, launches, cultural projects |

For each, write:

```text
Name:
Thesis:
Spine:
Palette:
Type:
Layout:
Motion:
Risk:
Why it fits:
Why it might fail:
```

Choose with explicit tradeoffs, not by vibes. For a B2B dashboard, a wildcard that slows scanning is a bad choice even if it looks striking. For a portfolio, a grounded direction that looks like every other portfolio is also a bad choice.

## The design plan

Before coding, produce a compact plan. Keep it to one page.

```markdown
# Design plan

## Brief
Subject:
Audience:
Primary job:
Content:
Constraints:
Success:

## Direction
Name:
Thesis:
Spine:
Why this fits:

## Tokens
Color: name + value + role (4–6 values)
Type: family + role + scale
Space: base unit + scale
Radius:
Elevation:
Motion:

## Layout
Spine:
Grid:
Density:
Breakpoints:
ASCII wireframe:

## States
Loading:
Empty:
Error:
Success:
Disabled:
Focus:

## Risks
- ...
- ...
```

### ASCII wireframes

Use ASCII to compare compositions before committing to CSS. Example:

```text
+--------------------------------------------------+
| logo        browse   how it works   join   [search] |
+--------------------------------------------------+
|  FIND A TOOL                                     |
|  [ search by name or category........ ]  [Search] |
|                                                  |
|  +--------+  +--------+  +--------+  +--------+  |
|  | drill  |  | ladder |  | saw    |  | tent   |  |
|  | avail. |  | avail. |  | wait   |  | avail. |  |
|  +--------+  +--------+  +--------+  +--------+  |
|                                                  |
|  Popular this week        Pickup hours        |
|  ------------------       ----------------     |
+--------------------------------------------------+
```

Wireframes expose hierarchy problems early. If the wireframe is generic, the visual design will be generic too.

## Typography

Typography is the fastest way to make an interface feel specific. It is also the easiest to overdo.

### Roles, not sizes

Define roles first:

| Role | Purpose | Typical treatment |
|---|---|---|
| Display | The one expressive moment | Large, tight, often a distinctive family |
| H1 | Page title | One per page, clear hierarchy |
| H2 / H3 | Sections and subsections | Decreasing scale, consistent rhythm |
| Body | Reading text | 16–18 px, line-height 1.5–1.7, measure 45–75 ch |
| UI label | Buttons, tabs, fields | 14–16 px, medium weight, sentence case |
| Small / meta | Secondary information | 12–14 px, still legible, never low-contrast filler |
| Mono | Code, IDs, timestamps, tabular data | Tabular figures, not for long prose |

### Choosing families

Use one family with multiple weights and widths, or two clearly distinct families. Two similar sans-serifs create visual noise without contrast.

| Strategy | Example | Best for |
|---|---|---|
| One superfamily | A grotesque with text, display, and mono cuts | Product UI, dashboards, systems |
| Display + text | A characterful display face + a restrained text face | Marketing, editorial, brand pages |
| Serif + sans | A text serif + a neutral sans | Publishing, culture, long-form |
| Condensed + humanist | A condensed display + a readable body | Signage, industrial, data-dense |

Font categories and open-source examples — a starting point, not a menu:

- **Neo-grotesque**: Inter, Public Sans, Archivo, Geist (check license).
- **Humanist sans**: Source Sans 3, IBM Plex Sans, Fira Sans.
- **Geometric sans**: Outfit, Manrope, Sora.
- **Condensed**: Archivo Narrow, Barlow Condensed, Oswald.
- **Text serif**: Source Serif 4, Literata, Newsreader, Crimson Pro.
- **Display serif**: Fraunces, Instrument Serif, Bodoni Moda, Playfair Display (widely used; justify it).
- **Mono**: JetBrains Mono, IBM Plex Mono, Space Mono.
- **Characterful**: Bricolage Grotesque, Syne, Unbounded.

Do not default to Inter for every project. Inter is an excellent UI face; it is not a personality. If you use it, let another device carry the identity.

Check licensing before shipping. Prefer OFL/Apache fonts, self-host them, subset the character sets you need, and use `font-display: swap` or `optional`. Preload at most one critical face.

### Scale

Choose a ratio based on density:

| Ratio | Character | Use |
|---|---|---|
| 1.125 | Compact, subtle | Dense product UI |
| 1.2 | Balanced | Most web apps |
| 1.25 | Clear, editorial | Marketing, content |
| 1.333 | Dramatic | Landing pages, portfolios |

Use `rem` so user font settings work. Fluid type with `clamp()`:

```css
:root {
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: clamp(1.125rem, 1.05rem + 0.35vw, 1.25rem);
  --text-xl: clamp(1.25rem, 1.1rem + 0.7vw, 1.5rem);
  --text-2xl: clamp(1.5rem, 1.25rem + 1.2vw, 2rem);
  --text-3xl: clamp(1.875rem, 1.4rem + 2.2vw, 2.75rem);
  --text-display: clamp(2.5rem, 1.6rem + 4.5vw, 6rem);
}
```

Do not let display type overwhelm the viewport. Test at 320 px, 768 px, and 1440 px. A display size that works at 1440 px may wrap into five lines at 320 px.

### Setting text

- Body line-height: 1.5–1.7; serif body can take slightly more.
- Display line-height: 1.05–1.2; tighten large type optically.
- Measure: 45–75 characters; about 65 ch is a good default. Mobile: 35–60.
- Alignment: left-aligned body for LTR. Center only short blocks. Justify only with hyphenation and reliable support.
- Letter-spacing: negative for large display, zero for body, positive only for short all-caps labels.
- Use `text-wrap: balance` for headings and `text-wrap: pretty` for body as progressive enhancement.
- Use `font-variant-numeric: tabular-nums` for tables, prices, timers, and aligned numbers.
- Avoid all-caps body text, fake small caps, gradient text, outlined text, and tight tracking on lowercase prose.
- Do not accent a single word in a headline with italic, bold, or color as a default move; it is one of the most common generated-page tells.

### Type as structure

Type can do more than deliver content:

- a large folio number as a section marker, if the content is genuinely numbered;
- a masthead that establishes the publication;
- a hanging label column that makes a data table scannable;
- a change in width or weight that signals a change in voice;
- a caption system that treats metadata as part of the composition.

Use these devices only when they encode real information. A decorative "01 / 02 / 03" over content that is not a sequence is noise.

## Color

### Roles first

A palette is a set of jobs, not a collection of swatches.

| Role | Purpose | Example |
|---|---|---|
| Canvas | The page background | `--color-canvas` |
| Surface | Cards, panels, raised areas | `--color-surface` |
| Ink | Primary text | `--color-text` |
| Muted | Secondary text, metadata | `--color-text-muted` |
| Line | Borders, dividers, rules | `--color-border` |
| Accent | Primary action, emphasis | `--color-accent` |
| Accent ink | Text on accent | `--color-accent-ink` |
| Focus | Focus ring | `--color-focus` |
| Success / warning / danger / info | Semantic states | `--color-success`, etc. |

Four to six core values are usually enough: canvas, surface, ink, muted, line, accent. Add semantic states only when the product needs them.

### Build from the subject

Choose a seed from the subject's materials or context: safety orange from a workshop, oxide red from a brick, chlorophyll green from a seed catalog, blueprint blue from a drawing, ink black from a letterpress. Then build a scale around it.

OKLCH makes perceptual scales easier:

```css
:root {
  --brand-50:  oklch(0.97 0.02 55);
  --brand-100: oklch(0.93 0.04 55);
  --brand-300: oklch(0.80 0.10 55);
  --brand-500: oklch(0.62 0.16 55);
  --brand-700: oklch(0.48 0.14 55);
  --brand-900: oklch(0.30 0.08 55);
}
```

Keep the hue roughly stable and vary lightness and chroma. A scale that jumps hue at every step looks muddy.

### Neutrals

Choose a neutral temperature and tint it toward the brand hue at very low chroma. Warm gray for editorial, cool gray for technical, green-gray for natural, brown-gray for craft. Do not mix warm and cool neutrals in the same interface without a reason.

### One accent

Use one accent for action and emphasis. A second accent is a system decision, not a decoration. If everything is accent-colored, nothing is.

Use the 60-30-10 heuristic as a sanity check, not a law: about 60% canvas/neutral, 30% surface/secondary, 10% accent.

### Dark mode

Dark mode is not an inversion. It is a separate tonal system:

- avoid pure black; use a near-black with a slight hue;
- lower chroma for large surfaces; bright accents often need desaturating;
- express elevation with lighter surfaces and borders, not only shadows;
- keep semantic colors legible against dark surfaces;
- test contrast independently; light-mode values rarely carry over;
- design both themes together so hierarchy survives.

### Contrast

Check every text/background pair and every meaningful non-text boundary:

- normal text: 4.5:1 minimum;
- large text (≥24 px regular or ≥18.66 px bold): 3:1;
- UI components, icons, focus indicators, and graphical objects: 3:1;
- disabled text is exempt from WCAG contrast, but should still be recognizable;
- placeholders are text; if they carry information, they need contrast.

Use `scripts/contrast.py`:

```bash
python3 scripts/contrast.py "#1E1A16" "#F3EEE3"
python3 scripts/contrast.py --pairs palette.json
```

### Color and meaning

- Never use red/green alone for error/success. Add an icon, label, or pattern.
- Use a colorblind-safe categorical palette for charts; test with a simulator.
- Do not use color to encode more categories than a legend can support.
- Check cultural associations for the target locale; color meanings vary.

### Color anti-patterns

- purple/indigo gradient as the default "tech" palette;
- pure black `#000` and pure white `#fff` everywhere;
- low-contrast gray body text on a tinted background;
- rainbow gradients, gradient text, and neon glows without a subject reason;
- a different accent color on every section;
- semantic colors used decoratively.

## Layout and composition

### Start with content priority

Rank the content:

1. What must the user see first to act?
2. What must they see second to trust or decide?
3. What is supporting detail?
4. What can be moved to another screen?

The layout follows this ranking. Do not start with a grid and pour content into it.

### Choose a spine

| Spine | Structure | Good for |
|---|---|---|
| Single column | One measured column, generous margins | Reading, documentation, manifestos |
| Editorial split | Asymmetric text/media split | Landing pages, stories, product detail |
| Modular grid | Repeating cards or tiles | Catalogs, dashboards, galleries |
| Asymmetric grid | Unequal columns, varied spans | Magazines, portfolios, feature pages |
| Dashboard | Fixed regions, dense widgets, persistent nav | Operational tools, analytics |
| Timeline | Ordered sequence with markers | Processes, history, onboarding |
| Full-bleed media | Image or video carries the page | Travel, fashion, product launches |
| Bento | Varied tiles in a grid | Feature overviews, app home screens |
| Document | Header, body, margin notes | Reports, policies, long-form |

Bento and card grids are not neutral. They impose equal visual weight on unequal content. Use them when the content really is a set of peers.

### Grid

- Use CSS Grid for two-dimensional layout; use flexbox for one-dimensional flow.
- A 12-column grid is a useful default for marketing and content; dashboards often need a 4/8/12 adaptive grid.
- Set gutters and margins with tokens, not ad hoc values.
- Use `minmax()` and `auto-fit`/`auto-fill` for responsive card grids, but cap the max width so cards do not become billboards.
- Prefer content-driven breakpoints over device labels. Add a breakpoint when the content breaks, not because a device exists.
- Use container queries for components that appear in different regions.

```css
.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 16rem), 1fr));
  gap: var(--space-4);
}
```

### Whitespace

Whitespace is not empty space; it is grouping and pacing.

- Use smaller gaps within a group, larger gaps between groups.
- Section spacing should be visibly larger than component spacing.
- Avoid uniform padding everywhere; it flattens hierarchy.
- On mobile, reduce horizontal margins but keep vertical rhythm.
- On large screens, cap the reading measure; do not let paragraphs run edge to edge.

### Density

Match density to the task:

- **Gallery**: generous spacing, large type, few elements per screen.
- **Daily app**: comfortable spacing, clear groups, moderate density.
- **Cockpit**: tight spacing, strong alignment, monospaced numbers, no decorative cards.

A dashboard does not need to be spacious to be calm. It needs alignment, grouping, and consistent rhythm.

### Above the fold

Open with the most characteristic thing in the subject's world, in the most appropriate form: a headline, an image, an animation, a live demo, a search box, a map, a tool. A big number with a small label, supporting stats, and a gradient accent is the default treatment; use it only when it is truly the best option.

The hero must answer: what is this, who is it for, and what can I do now? It does not need to be a full-screen image.

### Responsive composition

Do not shrink the desktop layout. Recompose:

- convert multi-column sections to a deliberate single-column order;
- turn wide tables into stacked records or a scrollable region with a clear affordance;
- move secondary navigation into a drawer or bottom nav;
- keep primary actions within reach;
- reduce decorative media before reducing content;
- test the order of content when columns stack.

### Layout anti-patterns

- identical three-card feature rows as the default;
- every section in a rounded card with the same shadow;
- centered everything;
- text lines longer than 80 characters;
- fixed-height text containers that clip when content grows;
- nested scroll regions that fight the page;
- sticky headers that obscure anchors or focus;
- decorative sidebars that push content off small screens.

## Imagery and iconography

### Art direction

Images are part of the design, not filler. Define:

- subject and crop (product, people, place, detail);
- aspect ratios per role (hero, card, thumbnail, avatar);
- treatment (natural, duotone, grain, high contrast, color grade);
- consistency across the set;
- licensing and attribution.

Use real product or context imagery when possible. Avoid generic stock scenes that could belong to any company. If you use placeholders, use stable, licensed sources and label them; do not depend on a remote placeholder service in production.

### Alt text

- Describe the purpose of the image in context, not its pixels.
- Decorative images: `alt=""` and `aria-hidden="true"` where appropriate.
- Functional images (image buttons, linked logos): describe the destination or action.
- Complex images (charts, diagrams): provide a short alt plus a longer description or data table.

### Icons

- Use one family and one visual style. Do not mix filled, outline, rounded, and sharp icons at the same hierarchy level.
- Use a consistent size grid (16, 20, 24 px) and stroke width.
- Icon-only buttons need an accessible name. Decorative icons beside visible text should be hidden from the accessibility tree.
- Do not use emoji as structural icons. Emoji render differently across platforms and cannot be themed reliably.
- Meaningful icons need 3:1 contrast against their background.
- Align icons optically with text, not just by bounding box.

### Illustration

If you use illustration, define a consistent palette, line weight, level of detail, and perspective. Mixing 3D renders, flat vectors, and hand-drawn sketches in one interface reads as indecision.

## Voice and interface copy

Words are design material. Write them with the same intentionality as spacing.

### Voice attributes

Choose three adjectives for the product's voice, for example: *plain, warm, precise* or *direct, technical, calm*. Then write to them. Tone can shift with context (error vs. celebration), but voice stays consistent.

### Principles

- Write from the user's perspective, in their vocabulary.
- Use plain language and concrete verbs.
- Prefer active voice.
- Use sentence case for labels, buttons, and headings unless the brand system says otherwise.
- Keep one name for one thing through the whole flow.
- Put the most important information first.
- Remove filler, hedging, and marketing superlatives.

### Calls to action

A CTA says exactly what happens:

| Weak | Strong |
|---|---|
| Submit | Save changes |
| Get started | Create account |
| Learn more | See how lending works |
| Continue | Choose a pickup time |

Keep the action name consistent: a button that says **Publish** should produce a confirmation that says **Published**, not **Success!**.

### Errors

An error message answers three questions:

1. What happened?
2. Why?
3. What can I do now?

```text
✗ Something went wrong.
✓ We couldn't reserve the drill because it's already booked for Saturday.
  Choose another pickup time or join the waitlist.
```

- Put the message next to the field or action that caused it.
- Use specific language, not error codes alone.
- Do not blame the user.
- Do not apologize instead of explaining.
- Preserve entered data.
- For multiple errors, provide a focusable summary and inline messages.

### Empty states

An empty screen is an invitation to act, not a dead end.

```text
No tools reserved yet.
Browse the catalog and reserve what you need for your next project.
[Browse tools]
```

Explain what would be here, why it is empty, and what to do next. Do not use a sad illustration as the only content.

### Confirmation and destructive actions

- Confirm irreversible actions, but do not confirm every action.
- Name the object and the consequence: "Delete the circular saw reservation?" not "Are you sure?"
- Offer undo for reversible destructive actions.
- Separate destructive actions visually and spatially from primary actions.
- Do not use confirmshaming ("No thanks, I like paying more").

### Numbers, dates, and names

- Use realistic, locale-aware formats.
- Use tabular figures for aligned data.
- Label synthetic data.
- Do not invent testimonials, metrics, or activity that look real.
- Avoid generic names and placeholder companies; they make the design feel generated.

## Anti-generic audit

Run this before committing to a direction.

### The five common generated-design clusters

1. Warm cream (#F4F1EA) + high-contrast serif + terracotta (#D97757).
2. Near-black + one acid-green or vermilion accent.
3. Broadsheet: hairline rules, zero radius, dense newspaper columns.
4. SaaS card kit: identical rounded cards, one shadow, gradient washes.
5. Template chrome: tracked all-caps eyebrow above every heading, middle-dot meta, `WORD — fragment` labels, `→` on every link, monospace for small labels, tinted near-black.

These can be good. The problem is using them without a subject reason. If the brief asks for one, execute it deliberately.

### Other defaults to question

- purple/indigo gradient SaaS;
- centered badge + headline + two buttons + logo marquee;
- gradient text, glassmorphism, floating blobs, decorative 3D;
- three equal feature cards;
- one border-radius for everything;
- every section fading up on scroll;
- stock "diverse team" photography;
- fake dashboards with meaningless numbers;
- AI copy clichés.

### Replacement moves

When you catch yourself reaching for a default, try a subject-specific alternative:

| Default move | Better move |
|---|---|
| Centered hero with badge, headline, two buttons | Asymmetric split, live demo, search/reserve box, product-in-context, or a single strong statement |
| Three equal feature cards | Ranked list, 2-column zigzag, comparison table, or one large example plus supporting details |
| Purple/indigo gradient | A color drawn from the subject's material, place, or process |
| All-caps eyebrow above every heading | A functional label, a folio number for a real sequence, or no label |
| One border-radius everywhere | A radius scale tied to hierarchy: inputs, buttons, cards, modals |
| Fade-up on every section | One orchestrated entrance, then motion only for feedback and state changes |
| Stock team photo | The product, the place, a real artifact, a diagram, or no image |
| Generic "Elevate your workflow" | A concrete verb and outcome: "Reserve a drill for Saturday" |
| Fake dashboard numbers | Real sample data, clearly labeled synthetic data, or no numbers |
| Glassmorphism as the whole style | Translucency only where it communicates layering or dismissal |

### The tests

1. **Remove the logo test**: without the brand name, is the interface still recognizable?
2. **Swap the subject test**: if you replaced the subject with a competitor, would the design still fit? If yes, it is generic.
3. **One-sentence test**: can you name the organizing idea in one sentence?
4. **Squint test**: does the hierarchy survive when blurred?
5. **Small-screen test**: does the idea survive at 320 px?
6. **Content stress test**: does it work with twice the text, no images, and a long word?
7. **Human defense test**: could a designer defend the choices in a critique without saying "it looks clean"?
8. **Removal test**: what happens if you remove the most decorative element? If nothing is lost, remove it.

Distinctiveness is a hypothesis, not a result. A memorable direction can still fail the job. Validate the task with real users, and treat aesthetic judgments as arguments to be tested, not facts.

## Worked example: the tool library

### Brief

```text
Subject:       A neighborhood tool-lending library
Audience:      Renters and homeowners within walking distance, often on a phone
Primary job:   Find whether a specific tool is available this weekend and reserve it
Content:       42 tools with photos, availability windows, replacement values, pickup instructions
Constraints:   Mobile-first, small budget, existing green brand, WCAG 2.2 AA
Success:       First-time reservation in under two minutes; no horizontal scroll at 320 px
```

### Three directions

| Direction | Thesis | Verdict |
|---|---|---|
| **The pegboard** | A well-kept workshop: labeled bins, hooks, safety orange, everything visible | Strong fit: lending, repair, neighborhood utility |
| **The noticeboard** | Paper, tape, handwritten notes, community warmth | Fits community, but risks crafty cliché and poor scanning |
| **Inventory OS** | Barcode labels, monospaced data, dark control room | Fits inventory, but feels cold for neighbors on a phone |

Choose **the pegboard**. It supports the job (find a tool fast) and gives the brand a specific, non-generic spine.

### Design plan

```text
Thesis: For neighbors borrowing tools, this should feel like a well-kept pegboard:
labeled bins, hooks, safety orange, and everything visible at a glance.

Palette:
  canvas    #E9E7E2  galvanized wall
  surface   #F7F6F3  label paper
  ink       #191A18  stamped ink
  muted     #5F625C  pencil note
  accent    #B23A12  safety orange
  line      #C9C7C0  pegboard grid
  success   #2F6B4F  available tag

Type:
  display   Archivo Narrow, 600, tight
  body      Public Sans, 400/500
  mono      JetBrains Mono, 500, for bin codes and pickup times

Layout:
  12-column pegboard on desktop, 4-column on mobile
  hero = search/reserve, not a marketing headline
  tool cards are labeled bins: name, bin code, availability, action
  labels are functional, not decorative eyebrows

Motion:
  one load sequence: bin tags settle into the board, 240 ms stagger
  reduced motion: static
  hover/press: 120 ms orange underline, no card lift

Checks:
  not cream + serif + terracotta
  no purple gradient
  no identical cards with the same shadow
  labels carry real bin codes
  works at 320 px with stacked bins
```

### ASCII wireframe

```text
+--------------------------------------------------+
| TOOL LIBRARY     browse   how it works   join     |
+--------------------------------------------------+
|  WHAT DO YOU NEED FIXING?                         |
|  [ search by tool or project........... ] [Find]  |
|  Popular: drill  ladder  saw  tent  sander        |
|                                                  |
|  BIN 04        BIN 07        BIN 12        BIN 19 |
|  +----------+  +----------+  +----------+  +-----+|
|  | [drill]  |  | [ladder] |  | [saw]    |  |[tent]||
|  | available|  | available|  | waitlist |  |avail.||
|  | Reserve  |  | Reserve  |  | Join     |  |Res.  ||
|  +----------+  +----------+  +----------+  +-----+|
|                                                  |
|  Pickup Sat 9–12 · 14 Oak St · Members free       |
+--------------------------------------------------+
```

### Why it works

- The pegboard spine is visible in the grid, labels, and language.
- The hero is the job (search/reserve), not a generic brand statement.
- The palette comes from the workshop, not from a SaaS gradient.
- The labels carry real information (bin codes, availability), so they are structure, not decoration.
- The motion is one moment tied to the metaphor, with a static reduced-motion fallback.
- The design can extend to tool detail, pickup, and membership screens.

## Critique prompts

Use these when reviewing your own direction:

- What is the one thing someone will remember?
- What does the interface say about the subject before the copy is read?
- Where is the hierarchy strongest? Where is it weakest?
- Which element is decorative but pretending to be structural?
- What would a skeptical senior designer attack first?
- What would you remove if you had to remove one accessory?
- Does the direction still work with real content, no images, and a 320 px screen?
- Is the boldness concentrated, or spread thin?
- Would this be better as a quieter interface with one strong detail?
- What would make this feel handmade rather than generated?

If the answer to the last question is "nothing," the direction is not finished.
