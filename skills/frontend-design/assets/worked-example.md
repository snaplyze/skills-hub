# Worked example: the tool library

A complete direction from brief to critique. Use it as a model, not a template; values are illustrative and should be replaced with project tokens. The method is in `references/design-direction.md`; the brief form is in `assets/design-brief.md`.

## Brief

```text
Subject:       A neighborhood tool-lending library
Audience:      Renters and homeowners within walking distance, often on a phone
Primary job:   Find whether a specific tool is available this weekend and reserve it
Content:       42 tools with photos, availability windows, replacement values, pickup instructions
Constraints:   Mobile-first, small budget, existing forest-green library sign (paired with safety-orange action tags), WCAG 2.2 AA
Success:       First-time reservation in under two minutes; no horizontal scroll at 320 px
```

## Three directions

| Direction | Thesis | Verdict |
|---|---|---|
| **The pegboard** | A well-kept workshop: labeled bins, hooks, safety orange, everything visible | Strong fit: lending, repair, neighborhood utility |
| **The noticeboard** | Paper, tape, handwritten notes, community warmth | Fits community, but risks crafty cliché and poor scanning |
| **Inventory OS** | Barcode labels, monospaced data, dark control room | Fits inventory, but feels cold for neighbors on a phone |

Choose **the pegboard**. It supports the job (find a tool fast) and gives the brand a specific, non-generic spine.

## Design plan

```text
Thesis: For neighbors borrowing tools, this should feel like a well-kept pegboard:
labeled bins, hooks, safety orange, and everything visible at a glance.

Palette (illustrative; map to project tokens):
  canvas    galvanized wall
  surface   label paper
  ink       stamped ink
  muted     pencil note
  accent    safety orange
  line      pegboard grid
  success   available tag

Type:
  display   Archivo, 600, tight (use --font-display)
  body      Public Sans, 400/500 (use --font-body)
  mono      JetBrains Mono, 500, for bin codes and pickup times

Layout:
  12-column pegboard on desktop, 4-column on mobile
  hero = search/reserve, not a marketing headline
  tool cards are labeled bins: name, bin code, availability, action
  labels are functional, not decorative eyebrows

Motion:
  one load sequence: bin tags settle into the board
  use token durations (--duration-slow) with a --duration-instant stagger
  reduced motion: static
  hover/press: --duration-fast orange underline, no card lift

Checks:
  not cream + serif + terracotta
  no purple gradient
  no identical cards with the same shadow
  labels carry real bin codes
  works at 320 px with stacked bins
```

## ASCII wireframe

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

## Why it works

- The pegboard spine is visible in the grid, labels, and language.
- The hero is the job (search/reserve), not a generic brand statement.
- The palette comes from the workshop, not a SaaS gradient.
- Labels carry real information (bin codes, availability), so they are structure, not decoration.
- The motion is one moment tied to the metaphor, with a static reduced-motion fallback.
- The design extends to tool detail, pickup, and membership screens without a new language.

## Critique

The risk is costume: pegboard decoration without faster reservation. Test with a first-time user on a phone: can they find availability and reserve in under two minutes? Remove any bin label that does not carry real data. If the labels disappear and nothing is lost, they were decoration.
