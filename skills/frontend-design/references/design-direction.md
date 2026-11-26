# Design Direction

Use for new pages, redesigns, and visual identity work. The goal is a direction that could only belong to this subject, not a style applied from outside. See `references/visual-craft.md` for craft, `assets/design-brief.md` for the brief and plan, and the optional `assets/worked-example.md` for a complete example.

## The brief

A brief states subject, audience, job, content, constraints, and success. If the user gives only a feature list, infer the rest and say so.

| Field | Bad | Good |
|---|---|---|
| Subject | "A platform" | "A neighborhood tool-lending library" |
| Audience | "Users" | "Renters and homeowners nearby, often on a phone" |
| Primary job | "Browse" | "Find and reserve an available tool for this weekend in under two minutes" |
| Content | "Some cards" | "42 tools with photos, availability, replacement values, pickup instructions" |
| Constraints | "Make it modern" | "Mobile-first, existing green brand, no photo budget, WCAG 2.2 AA" |
| Success | "Looks better" | "A first-time user reserves a drill without help; no horizontal scroll at 320 px" |

Write the brief before choosing colors. If you cannot state the primary job in one sentence, the design has nothing to organize around.

## Direction method

### 1. Write a thesis

Complete this sentence:

> For **[audience]** who need **[job]**, this interface should feel like **[concrete metaphor or material]**, expressed through **[three visual devices]**.

Examples: "For neighbors borrowing tools, this should feel like a well-kept pegboard: labeled bins, hooks, safety orange, and everything visible at a glance." "For a research archive, this should feel like a reading room: warm paper, precise rules, quiet typography, and no decorative noise."

The metaphor is a source of decisions, not a costume. If it fights the job, change the metaphor.

### 2. Build a visual vocabulary

Collect concrete material from the subject's world: objects (tools, labels, tickets, ledgers, instruments), places (workshop, library, market, station, field), materials (paper, canvas, cork, steel, glass, clay, ink), language (words the domain uses), rituals (how work gets done, checked, signed), and references (print, signage, industrial design, film, architecture, music).

Translate it into design axes:

| Axis | Low end | High end |
|---|---|---|
| Density | Airy, gallery-like | Packed, cockpit-like |
| Temperature | Cool, clinical | Warm, organic |
| Contrast | Soft, tonal | Stark, graphic |
| Geometry | Rounded, organic | Rigid, orthogonal |
| Era | Historical, analog | Futuristic, technical |
| Energy | Calm, still | Kinetic, loud |
| Finish | Utilitarian, raw | Refined, luxurious |
| Familiarity | Conventional | Experimental |

Choose a position on each axis. A direction is positions, not a mood board.

### 3. Find the spine

The spine is the one organizing idea that shapes layout, type, color, and motion: a pegboard, a newspaper front page, a lab notebook, a departure board, a seed catalog, a control room, or a reading room. It should be visible in the wireframe before CSS. If you cannot draw it, it is not a direction yet.

Use archetypes as reference points after the thesis, not as a menu. Two projects in one archetype should still look different because subjects, content, and audiences differ.

| Archetype | Spine | Best for | Main risk |
|---|---|---|---|
| **Reading room** | Measured column, margins, footnotes | Publishing, research, docs | Beige and forgettable |
| **Workshop** | Pegboard, bins, labels, visible tools | Tools, repair, making | Costume without utility |
| **Institutional** | Strict grid, rules, numbered sections | Government, finance, healthcare | Cold and bureaucratic |
| **Field guide** | Plates, captions, specimen labels | Nature, wellness, education | Generic "organic" |
| **Control room** | Dense panels, gauges, status rows | Dashboards, ops, monitoring | Unreadable density |
| **Atelier** | Generous space, one dramatic object | Luxury, fashion, architecture | Style over substance |
| **Toybox** | Chunky modules, playful geometry | Kids, games, creative tools | Clutter, low credibility |
| **Archive** | Index cards, catalog numbers, tabs | Culture, music, collections | Nostalgia without navigation |
| **Terminal** | Monospaced grid, command surface | Developer tools, security, data | Novelty hurts readability |
| **Market stall** | Handbills, price tags, stacked goods | Retail, food, local commerce | Chaos without hierarchy |

Pick an archetype, then push it through the subject's vocabulary. "Workshop" is not a direction; "a pegboard for a neighborhood tool library, with bin codes and safety-orange availability tags" is.

### 4. Define the devices

A direction becomes executable when it specifies grid (columns, gutters, breaks), type (families, roles, scale, measure), color (4–6 named values with roles), surface (borders, radii, shadows), imagery (crop, ratio, treatment), icons (family, stroke, size), and motion (one entrance, feedback, easing).

### 5. Test the thesis against the job

Ask: does it make the primary job easier or merely more interesting? Does it survive the densest screen, longest content, smallest viewport, dark mode, 200% zoom, and reduced motion? Can a new team member extend it without guessing? Does it require effects or assets the project cannot afford? A direction that only works on a desktop hero is a poster, not a product.

## Three directions, one choice

For a new page or deliberate redesign, generate three directions with different risk profiles. Do not generate three variations of one idea.

| Direction | What it is | When to use |
|---|---|---|
| **Grounded** | Category conventions, made specific with one strong device | Product UI, dashboards, forms, B2B |
| **Adjacent** | A visual system borrowed from a neighboring domain | Differentiation without confusion |
| **Wildcard** | A high-concept direction with a strong organizing metaphor | Portfolios, campaigns, launches, culture |

For each, write name, thesis, spine, palette, type, layout, motion, risk, and fit. Choose with explicit tradeoffs; a wildcard that slows scanning is wrong for a B2B dashboard.

## Anti-generic audit

Run this before committing to a direction.

### Five common generated-design clusters

1. Warm cream (#F4F1EA) + high-contrast serif + terracotta (#D97757).
2. Near-black + one acid-green or vermilion accent.
3. Broadsheet: hairline rules, zero radius, dense newspaper columns.
4. SaaS card kit: identical rounded cards, one shadow, gradient washes.
5. Template chrome: tracked all-caps eyebrow above every heading, middle-dot meta, `WORD — fragment` labels, `→` on every link, monospace for small labels, tinted near-black.

These are fine when the subject justifies them; without a reason, they are defaults.

### Replacement moves

| Default move | Better move |
|---|---|
| Centered hero with badge, headline, two buttons | Asymmetric split, live demo, search/reserve box, or one statement |
| Three equal feature cards | Ranked list, zigzag, comparison table, or one large example |
| Purple/indigo gradient | A color from the subject's material, place, or process |
| All-caps eyebrow above every heading | A functional label, a folio number for a real sequence, or no label |
| One border-radius everywhere | A radius scale tied to hierarchy: inputs, buttons, cards, modals |
| Fade-up on every section | One entrance, then motion only for feedback and state changes |
| Stock team photo | The product, the place, a real artifact, a diagram, or no image |
| Generic "Elevate your workflow" | A concrete verb and outcome: "Reserve a drill for Saturday" |
| Fake dashboard numbers | Real sample data, labeled synthetic data, or no numbers |
| Glassmorphism as the whole style | Translucency only where it communicates layering or dismissal |

### The tests

1. **Remove the logo:** without the brand, is it still recognizable?
2. **Swap the subject:** would the design still fit a competitor? If yes, it is generic.
3. **One sentence:** can you name the organizing idea in one sentence?
4. **Squint:** does hierarchy survive when blurred?
5. **Small screen:** does the idea survive at 320 px?
6. **Content stress:** does it work with twice the text, no images, and a long word?
7. **Human defense:** could a designer defend the choices without saying "it looks clean"?
8. **Removal:** remove the most decorative element; if nothing is lost, remove it.

Distinctiveness is a hypothesis: a memorable direction can still fail the job. Validate with real users.

## Critique prompts

Use these when reviewing your own direction:

- What is the one thing someone will remember?
- What does the interface say about the subject before the copy is read?
- Which element is decorative but pretending to be structural?
- What would you remove if you had to remove one accessory?
- Does the direction still work with real content, no images, and a 320 px screen?
- Is boldness concentrated or spread thin?
- What would make this feel handmade rather than generated?

If the answer to the last question is "nothing," the direction is not finished.
