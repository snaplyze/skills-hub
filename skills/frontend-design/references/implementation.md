# Implementation

A design is only as good as the code that carries it. This reference covers modern CSS, component architecture, framework-specific pitfalls, performance budgets, and the verification that keeps a polished design from breaking in production.

Use the project's existing conventions first. The patterns below are defaults for new work, not a mandate to rewrite a working codebase.

## Contents

- [Architecture](#architecture)
- [Modern CSS](#modern-css)
- [Component patterns](#component-patterns)
- [React and Next.js](#react-and-nextjs)
- [Tailwind CSS](#tailwind-css)
- [shadcn/ui and headless primitives](#shadcnui-and-headless-primitives)
- [Vue, Svelte, and Astro](#vue-svelte-and-astro)
- [Performance](#performance)
- [Testing](#testing)
- [Common bugs](#common-bugs)
- [Code review](#code-review)

## Architecture

### Start from the existing system

Before adding a library or a new pattern:

- inspect `package.json`, lockfiles, and config files;
- find the CSS entry point, tokens, and theme;
- find existing components and variants;
- check the routing and data-fetching model;
- check the test and lint setup;
- check browser and device support.

Do not add a second component library, a second styling system, or a second state manager to solve a local problem. Never assume a dependency exists: check `package.json` and the lockfile before importing it. If a new dependency is justified, state why and include the install command.

### Suggested structure

Adapt to the framework, but keep concerns separate:

```text
src/
  app/ or pages/          routes and screens
  components/
    ui/                   primitives: button, input, dialog
    patterns/             composed patterns: search, empty state
    feature/              feature-specific components
  styles/
    tokens.css            primitives + semantic tokens
    base.css              reset, typography, global styles
    utilities.css         small utilities
  lib/                    helpers, formatting, API client
  hooks/                  shared behavior
  tests/                  unit, integration, e2e
```

Colocate component tests, stories, and types with the component when the project does that. Do not create a global folder for everything.

### CSS layers

Use `@layer` to control specificity:

```css
@layer reset, tokens, base, components, utilities;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
}

@layer base {
  body { margin: 0; font-family: var(--font-body); }
}

@layer components {
  .button { /* ... */ }
}

@layer utilities {
  .visually-hidden { /* ... */ }
}
```

Layers prevent a utility from being defeated by a component selector, and make overrides predictable. If the project uses Tailwind, use its layer system instead.

### Naming

- Components: `PascalCase` in React/Vue/Svelte; `kebab-case` in HTML/CSS.
- CSS classes: follow the project (BEM, utility, CSS Modules). Do not mix conventions.
- Tokens: semantic, lowercase, hyphenated.
- Files: one component per file where practical.
- Tests: `Component.test.tsx` or the project's convention.

## Modern CSS

### Custom properties

```css
:root {
  --color-accent: oklch(0.62 0.16 55);
  --space-4: 1rem;
}
.button {
  background: var(--color-accent);
  padding: var(--space-2) var(--space-4);
}
```

Use fallbacks for critical values when supporting older browsers:

```css
background: #b4451f;
background: var(--color-accent, #b4451f);
```

### `clamp()`, `min()`, `max()`

```css
.title {
  font-size: clamp(2rem, 1.4rem + 3vw, 4.5rem);
}
.container {
  inline-size: min(100% - 2rem, 80rem);
  margin-inline: auto;
}
.sidebar {
  inline-size: max(14rem, 25%);
}
```

### Logical properties

Use logical properties for RTL support:

```css
.card {
  padding-inline: var(--space-4);
  padding-block: var(--space-3);
  margin-inline-start: var(--space-2);
  border-inline-start: 2px solid var(--color-accent);
  inset-inline: 0;
}
```

### Container queries

```css
.card-list {
  container-type: inline-size;
}
@container (min-width: 36rem) {
  .card {
    grid-template-columns: 10rem 1fr;
  }
}
```

Container queries make components portable across sidebars, modals, and grids. Use them when the component's layout depends on its container, not the viewport.

### `:has()`

```css
.field:has(input:invalid) {
  --field-border: var(--color-danger);
}
.card:has(img) {
  padding-block-start: 0;
}
```

`:`has()` is widely supported in modern browsers. Provide a sensible fallback for critical behavior.

### `color-mix()`

```css
.button:hover {
  background: color-mix(in oklch, var(--color-accent) 88%, black);
}
```

Use it for tints, hover states, and overlays. Test contrast after mixing.

### `text-wrap`

```css
h1, h2, h3 {
  text-wrap: balance;
}
p {
  text-wrap: pretty;
}
```

Use `balance` for short headings, `pretty` for body text. Both are progressive enhancements.

### `accent-color`

```css
input[type="checkbox"],
input[type="radio"],
input[type="range"] {
  accent-color: var(--color-accent);
}
```

This gives native controls a brand color without rebuilding them.

### `scrollbar-gutter`

```css
html {
  scrollbar-gutter: stable;
}
```

Prevents layout shift when a modal locks scroll or content grows.

### `dvh` / `svh` / `lvh`

```css
.hero {
  min-block-size: 100svh;
}
.app {
  min-block-size: 100dvh;
}
```

`svh` is the smallest viewport (browser chrome visible); `dvh` tracks dynamic chrome. Test keyboard and address-bar changes.

### `@starting-style`

```css
dialog[open] {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 200ms, transform 200ms;
}
@starting-style {
  dialog[open] {
    opacity: 0;
    transform: translateY(8px);
  }
}
```

Progressive enhancement for entry animations without JS.

### `prefers-*` and `forced-colors`

```css
@media (prefers-reduced-motion: reduce) { /* ... */ }
@media (prefers-contrast: more) { /* ... */ }
@media (forced-colors: active) {
  .button { border: 1px solid ButtonText; }
}
```

Test all three.

### CSS anti-patterns

- `!important` as a layout strategy;
- `transition: all`;
- `outline: none` without a replacement;
- fixed heights on text containers;
- `overflow: hidden` on the body to "fix" layout;
- `position: absolute` for normal flow;
- deeply nested selectors;
- styling by element type when a class is clearer;
- hardcoded colors in components;
- z-index values outside the scale.

## Component patterns

### Composition over configuration

```tsx
<Card>
  <Card.Header>
    <Card.Title>Reservations</Card.Title>
  </Card.Header>
  <Card.Body>
    <ReservationList items={items} />
  </Card.Body>
</Card>
```

Avoid a single component with 20 boolean props. Compose parts.

### Controlled and uncontrolled

- Support `value`/`defaultValue` and `onChange` where the component is reusable.
- Keep the state in the parent when it affects the flow.
- Use uncontrolled state for local UI details.
- Do not sync props to state with `useEffect` unless you are deliberately resetting.

### Variants

Use a variant helper (`cva`, `tailwind-variants`, or a small map) instead of nested ternaries:

```tsx
const button = cva("button", {
  variants: {
    intent: {
      primary: "button--primary",
      secondary: "button--secondary",
      danger: "button--danger",
    },
    size: {
      sm: "button--sm",
      md: "button--md",
      lg: "button--lg",
    },
  },
  defaultVariants: { intent: "primary", size: "md" },
});
```

### Accessibility is part of the API

- A `Button` must render a `<button>` by default.
- A `Link` must render an `<a href>`.
- A `Dialog` must handle focus, Escape, and scroll lock.
- An `IconButton` must require an accessible label.
- A `Field` must connect label, help, and error.

If a primitive cannot be used accessibly, fix the primitive, not every call site.

## React and Next.js

### Server and client components

- In Next.js App Router, components are server components by default.
- Add `"use client"` only to the interactive leaf, not the whole page.
- Keep data fetching on the server where possible.
- Pass serializable props across the boundary.
- Do not use browser APIs in server components.
- Wrap providers in a client component.

### State

| Need | Use |
|---|---|
| Local UI state | `useState` / `useReducer` |
| Shared by 2–3 siblings | Lift state |
| Theme, auth, locale | Context |
| Filters, pagination, tabs | URL/search params |
| Remote data | Server components, React Query, SWR |
| Complex global client state | Zustand/Redux only if justified |

Avoid prop drilling deeper than three levels. Avoid global state for local UI.

### Effects

- Do not use `useEffect` for derived state; compute during render.
- Use effects for external synchronization (subscriptions, DOM APIs, analytics).
- Clean up subscriptions, timers, observers, and animations.
- Do not use effects to fetch data in modern Next.js; fetch on the server or use a data library.
- Guard against race conditions with an abort controller or a cancelled flag.

### Rendering

- Use stable, unique keys; do not use array index for reorderable lists.
- Memoize only after measuring; unnecessary `memo`/`useMemo` adds complexity.
- Use `Suspense` and error boundaries for loading and failure.
- Avoid hydration mismatches: do not render `Date.now()`, `Math.random()`, or browser-only values on the server.
- Use `suppressHydrationWarning` only for genuinely unavoidable cases.

### Images and fonts

- Use `next/image` or the framework's image component.
- Provide `width`/`height` or `fill` with a sized container.
- Use `priority`/`fetchpriority` only for the LCP image.
- Use `next/font` or self-hosted fonts with `font-display`.
- Subset and preload only what is needed.

### Bundle budgets

| Profile | Initial JS |
|---|---|
| Marketing / content | < 100–150 KB gzip |
| SaaS app | < 200 KB gzip initial, route-split |
| Dashboard | Route-split; defer charts and heavy editors |
| Docs / blog | < 50–80 KB gzip |

Measure with the framework's bundle analyzer. Import only the icons and utilities used.

### React anti-patterns

- `useEffect` for derived state;
- `useState` for values that can be computed;
- index keys on reorderable lists;
- context for high-frequency state;
- memoizing everything;
- huge client components;
- fetching in effects when server rendering is available;
- `dangerouslySetInnerHTML` with unsanitized content;
- inline object/array props causing re-renders;
- `window` access during render.

## Tailwind CSS

### Map tokens

Tailwind v4 uses CSS-first config:

```css
@import "tailwindcss";

@theme {
  --color-canvas: oklch(0.97 0.01 80);
  --color-ink: oklch(0.22 0.02 80);
  --color-accent: oklch(0.62 0.16 55);
  --font-display: "Archivo Narrow", sans-serif;
  --font-body: "Public Sans", sans-serif;
  --radius-card: 0.75rem;
}
```

Tailwind v3 uses `tailwind.config.js`. Check the installed version before using v4 syntax.

### Use tokens, not arbitrary values

```html
<!-- Good -->
<div class="bg-surface text-ink p-4 rounded-card">

<!-- Avoid -->
<div class="bg-[#f7f6f3] text-[#191a18] p-[17px] rounded-[11px]">
```

Arbitrary values are acceptable for one-off layout constraints, not for the design system.

### Variants

Use `cva` or `tailwind-variants` for component APIs. Use `cn`/`clsx` + `tailwind-merge` to compose classes safely.

### Dark mode

Choose one strategy:

- `class`/`data-theme` for explicit control;
- `media` for system-only.

Do not mix strategies. Define semantic color tokens and use them in both themes.

### Responsive

- Mobile-first: base styles are the smallest screen; `md:` and `lg:` add complexity.
- Use container queries (`@container`) for components.
- Do not use `max-lg:` to undo desktop styles if mobile-first would be simpler.

### Tailwind anti-patterns

- a wall of arbitrary values;
- duplicating the same 12-class string across components;
- using `!important` modifiers to fight specificity;
- styling child elements with arbitrary selectors instead of component APIs;
- hiding focus with `outline-none` and no `focus-visible` ring.

## shadcn/ui and headless primitives

- Use Radix, React Aria, Ark, or Headless UI for behavior and accessibility.
- Style the primitives with the project's tokens; do not ship the default shadcn look unchanged.
- Keep the primitive's focus management, keyboard behavior, and ARIA intact.
- Customize radius, color, shadow, and density to match the design direction.
- Do not wrap a primitive in a div that breaks its semantics.
- Test with keyboard and a screen reader; headless libraries are a starting point, not a guarantee.

## Vue, Svelte, and Astro

### Vue

- Use `<script setup>` and typed props.
- Scoped styles are fine; shared tokens live in a global stylesheet.
- Use `v-model` for two-way bindings; emit events for actions.
- Use `Teleport` for modals; manage focus.
- Use `defineAsyncComponent` for heavy widgets.

### Svelte

- Use runes (`$state`, `$derived`, `$effect`) in Svelte 5; check the project's version.
- Use `bind:` for form controls, but keep validation explicit.
- Use transitions sparingly and respect reduced motion.
- Use `{@html}` only with sanitized content.

### Astro

- Prefer static rendering; hydrate only interactive islands.
- Use `client:visible`/`client:idle` for below-the-fold widgets.
- Keep global CSS small; scope component styles.
- Use the framework's image component for optimization.

## Performance

### Core Web Vitals

| Metric | Good | Needs improvement | Poor |
|---|---|---|---|
| LCP | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s |
| INP | ≤ 200 ms | 200–500 ms | > 500 ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |

Measure at p75 on mobile, not only on a fast desktop. Use field data when available; lab data for diagnosis.

### Images

- AVIF/WebP with fallbacks.
- `srcset`/`sizes`.
- width/height or `aspect-ratio`.
- lazy-load below the fold; do not lazy-load the LCP image.
- compress and resize; do not serve a 4000 px image in a 400 px slot.
- use a CDN image service if available.

### Fonts

- subset;
- variable fonts where possible;
- `font-display: swap` or `optional`;
- preload at most one critical font;
- self-host or use a reliable font CDN;
- match fallback metrics to reduce shift.

### 3D, canvas, and WebGL

- Treat 3D as an enhancement, not the only path to content. Provide a static image or HTML fallback.
- Do not block LCP on a 3D scene; lazy-load it after the main content.
- Pause rendering when offscreen or when the tab is hidden; dispose geometries, textures, and listeners.
- Respect reduced motion; do not autoplay camera movement or parallax.
- Test on a mid-range phone; reduce resolution, effects, and frame rate before dropping the feature.
- Provide a non-WebGL path for older devices and locked-down browsers.
- Do not make 3D navigation the only way to reach content.

### JavaScript

- route-split;
- defer non-critical scripts;
- avoid large date/utility libraries for one function;
- import only the icons used;
- virtualize long lists;
- debounce/throttle high-frequency handlers;
- move heavy work to a worker;
- remove unused dependencies.

### CSS

- keep critical CSS small;
- avoid huge utility frameworks if the project does not use them;
- use `content-visibility` carefully;
- avoid expensive selectors and filters on scroll;
- test with CPU throttling.

### Runtime

- avoid layout thrash;
- use `requestAnimationFrame`;
- batch DOM reads/writes;
- use `ResizeObserver`/`IntersectionObserver` instead of scroll polling;
- clean up listeners;
- avoid memory leaks in SPA routes.

## Testing

### Unit and component

- Test behavior, not implementation details.
- Test keyboard interaction and accessible names.
- Use Testing Library queries by role/label, not test IDs.
- Test loading, empty, error, and success states.
- Snapshot tests are not a substitute for behavior tests.

### E2E

- Use Playwright or Cypress.
- Test the primary flow, not every click.
- Run at a mobile viewport and a desktop viewport.
- Include keyboard-only and reduced-motion runs.
- Check for horizontal scroll at 320 px.
- Check console errors.

### Visual regression

- Screenshot key screens at 360, 768, and 1440 px.
- Capture light and dark themes.
- Capture empty, loading, and error states.
- Review diffs; do not auto-approve.

### Accessibility

- `@axe-core/playwright` or axe DevTools.
- Keyboard-only pass.
- Screen reader spot check.
- Zoom and reflow check.
- Contrast script.
- Automated tools catch only a subset; manual checks are required.

### Performance

- Lighthouse CI or the framework's analyzer.
- Bundle size budget.
- Core Web Vitals in the field.
- Test on a mid-range mobile device.

## Common bugs

| Bug | Cause | Fix |
|---|---|---|
| Horizontal scroll | Fixed width, long word, negative margin, grid blowout | `max-width: 100%`, `min-width: 0`, `overflow-wrap`, audit |
| Flex child won't shrink | `min-width: auto` | `min-width: 0` |
| Grid child overflows | Min track too wide | `minmax(min(100%, 18rem), 1fr)` |
| Content hidden behind sticky header | No scroll padding | `scroll-padding-top` |
| Modal background scrolls | No scroll lock | Lock body scroll; use `scrollbar-gutter: stable` |
| Focus lost after modal close | No focus restore | Return focus to trigger |
| Input zooms on iOS | < 16 px font | 16 px minimum |
| 100vh jumps | Browser chrome | `svh`/`dvh` |
| Images cause CLS | No dimensions | width/height or aspect-ratio |
| Font flash/FOIT | No `font-display` | `swap`/`optional` + preload |
| Z-index war | Arbitrary values | Layer scale |
| Hover state sticks on touch | Hover-only CSS | `@media (hover: hover)` |
| Animation jank | Animating layout properties | `transform`/`opacity` |
| Memory leak | Uncleaned listeners/observers | Cleanup in effect/unmount |
| Hydration mismatch | Browser-only values in SSR | Render after mount or compute on server |
| Double submit | No pending state | Disable + busy state + idempotency |
| Stale data after mutation | No cache invalidation | Invalidate/refetch or optimistic update with rollback |
| Long text overflow | No wrapping strategy | `overflow-wrap: anywhere` for tokens; wrap prose |
| Table breaks mobile | Wide table | Scroll region or stacked records |
| Dropdown clipped | `overflow: hidden` ancestor | Portal or adjust stacking/overflow |
| Tooltip inaccessible | Hover-only | Focus + Escape + `aria-describedby` |
| Toast missed | No live region | `role="status"` / `aria-live` |

## Code review

- [ ] The change follows the existing design system and conventions.
- [ ] Semantic HTML and accessible names are present.
- [ ] Keyboard, focus, and screen reader behavior are correct.
- [ ] Contrast and target sizes pass.
- [ ] Responsive behavior works at 320 px and on mobile.
- [ ] Loading, empty, error, and success states exist.
- [ ] No raw hex values or arbitrary spacing in components.
- [ ] No `transition: all`, `outline: none`, or `z-index: 9999`.
- [ ] Images have dimensions; fonts are optimized.
- [ ] No new heavy dependency without justification.
- [ ] Tests cover the new behavior.
- [ ] No console errors, dead links, or broken images.
- [ ] Motion respects reduced motion.
- [ ] The code is readable and the component API is clear.
