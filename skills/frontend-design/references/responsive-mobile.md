# Responsive and Mobile Design

Mobile is not a smaller desktop. The constraints are different: one thumb, intermittent attention, unreliable networks, browser chrome that moves, and a screen that may be 320 px wide. Design the reflow and the interaction, not just the breakpoint.

## Contents

- [Mobile-first principles](#mobile-first-principles)
- [Breakpoints and fluid layout](#breakpoints-and-fluid-layout)
- [Touch and thumb zones](#touch-and-thumb-zones)
- [Safe areas and browser chrome](#safe-areas-and-browser-chrome)
- [Responsive patterns](#responsive-patterns)
- [Mobile forms](#mobile-forms)
- [Navigation on mobile](#navigation-on-mobile)
- [Images and media](#images-and-media)
- [Mobile performance](#mobile-performance)
- [Testing matrix](#testing-matrix)
- [Common responsive bugs](#common-responsive-bugs)

## Mobile-first principles

1. **Start with the smallest useful screen.** Decide what must survive at 320 px before adding desktop richness.
2. **Prioritize the primary job.** Secondary navigation, decorative media, and optional fields can move, collapse, or wait.
3. **Design the content order.** When columns stack, the reading order must still make sense.
4. **Do not hide essential content behind hover.** Touch has no hover.
5. **Make targets comfortable.** 44×44 px is the practical default; WCAG 2.2 AA is 24×24 with exceptions.
6. **Respect the keyboard and browser chrome.** Inputs, sticky bars, and full-height sections must survive the on-screen keyboard and address bar.
7. **Assume a slow network.** Reserve space, lazy-load below the fold, and show meaningful loading states.
8. **Test on a real device.** Emulators miss touch, performance, and browser quirks.

## Breakpoints and fluid layout

### Breakpoints by content

Use breakpoints where the layout breaks, not where a device happens to be. A common starting set:

| Name | Width | Typical change |
|---|---|---|
| xs | 0–479 px | Single column, bottom nav, stacked forms |
| sm | 480–767 px | Larger phone, two-column cards |
| md | 768–1023 px | Tablet, sidebar appears, two-column content |
| lg | 1024–1279 px | Desktop, full nav, multi-column |
| xl | 1280–1535 px | Wide desktop, larger gutters |
| 2xl | 1536 px+ | Max-width container, more whitespace |

These are not sacred. A dashboard may break at 640 and 1280; a reading site may only need 768. Document the set.

### Fluid type and space

Use the fluid `--text-*`, `--gutter`, and `--section-space` tokens in `assets/tokens.css`; do not define a second `--step-*` scale. Fluid values reduce font-size breakpoints, but test the extremes because `clamp()` can produce awkward intermediate sizes. Check 320, 375, 768, 1024, and 1440 px.

### Containers

```css
.container {
  inline-size: min(100% - 2 * var(--gutter), var(--container-xl));
  margin-inline: auto;
}
```

- Use `min()` so the container never overflows.
- Use `max-inline-size` with `ch` for reading content.
- Full-bleed sections can break out, but their inner content should align to the container.

### Grid

```css
.auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
  gap: var(--space-4);
}
```

- `auto-fit` collapses empty tracks; `auto-fill` keeps them.
- `min(100%, 18rem)` prevents overflow when the container is narrower than the minimum.
- Use explicit columns for editorial layouts; use auto grids for collections.
- Use container queries when a component's layout depends on its container, not the viewport.

```css
.card-list {
  container-type: inline-size;
}
@container (min-width: 40rem) {
  .card { display: grid; grid-template-columns: 12rem 1fr; }
}
```

## Touch and thumb zones

### Target size and spacing

- Practical target: 44×44 px minimum; 48×48 dp for Android-style interfaces.
- WCAG 2.2 AA: 24×24 CSS px with exceptions; do not use the exception as a design target.
- Keep at least 8 px between adjacent targets.
- Expand the hit area with padding or a pseudo-element when the icon is small.

```css
.icon-button {
  position: relative;
  inline-size: 40px;
  block-size: 40px;
}
.icon-button::after {
  content: "";
  position: absolute;
  inset: -4px;
}
```

### Thumb zones

On a phone held one-handed:

- the bottom-center and bottom-right are easy to reach;
- the top corners are hard;
- the middle is comfortable for reading, not for frequent controls.

Put primary actions near the bottom on mobile, but do not cover content with a fixed bar. Move destructive actions away from the primary thumb path.

### Touch feedback

- Provide visual feedback within ~100 ms: color shift, opacity, slight scale.
- Do not move surrounding layout on press.
- Avoid 300 ms tap delay: use `touch-action: manipulation` on interactive elements.
- Do not rely on hover for state.
- Use `@media (hover: hover) and (pointer: fine)` for hover-only enhancements.

```css
@media (hover: hover) and (pointer: fine) {
  .card:hover { border-color: var(--color-border-strong); }
}
```

### Gestures

- Use standard gestures: vertical scroll, horizontal swipe for carousels, pinch to zoom.
- Do not block pinch zoom.
- Do not put horizontal swipe on the main content if it conflicts with browser back.
- Provide visible controls for any gesture-only action.
- Dragging needs a single-pointer and keyboard alternative.

## Safe areas and browser chrome

### Viewport meta

```html
<meta name="viewport" content="width=device-width, initial-scale=1" />
```

Do not add `user-scalable=no` or `maximum-scale=1`. Do not use a fixed viewport width.

### Dynamic viewport units

Use `dvh` for full-height sections, with `svh`/`lvh` where appropriate:

```css
.hero {
  min-block-size: 100svh; /* stable smallest viewport */
}
.app-shell {
  min-block-size: 100dvh; /* tracks dynamic browser chrome */
}
```

Test the address bar collapse and the on-screen keyboard. `100vh` often causes content to be hidden behind browser chrome on mobile.

### Safe-area insets

```css
.bottom-bar {
  padding-block-end: max(var(--space-4), env(safe-area-inset-bottom));
}
```

Use `env(safe-area-inset-top/right/bottom/left)` for fixed headers, bottom bars, and full-screen layouts on notched devices. Provide fallbacks with `max()`/`var()`.

### Sticky elements

- Add `scroll-padding-top` equal to the sticky header height.
- Add bottom padding so content is not hidden behind a fixed bottom bar.
- Avoid stacking multiple sticky bars on small screens.
- Do not let a sticky header obscure focused controls (WCAG 2.4.11).

```css
html {
  scroll-padding-top: calc(var(--header-height) + 1rem);
}
```

## Responsive patterns

### Navigation on mobile

| Screen | Pattern |
|---|---|
| Mobile | Bottom nav (3–5 top-level items) or top bar + menu |
| Tablet | Top bar + collapsible sidebar, or rail |
| Desktop | Persistent sidebar or top nav with full labels |

- Do not hide primary navigation behind a hamburger on desktop without a reason.
- Use a drawer for secondary navigation, not primary actions.
- Keep labels visible; icon-only navigation harms discoverability.
- Make the current location clear with more than color.
- Preserve scroll and filters when navigating back.

### Tables

Options, in order of preference:

1. **Reflow into stacked records** with field labels, preserving all data.
2. **Priority columns**: keep the most important 2–3 columns, reveal the rest on demand.
3. **Scroll region** with a visible affordance and sticky first column.
4. **Card list** for small screens if the data is not comparison-heavy.

Do not remove header associations or hide essential data. Do not use horizontal page scroll; contain the scroll within the table region.

### Cards and lists

- Stack cards in one column on mobile.
- Avoid identical card grids when the content has hierarchy.
- Let long text wrap; do not clamp essential content.
- Use `min-width: 0` on flex/grid children to allow shrinking.
- Use `overflow-wrap: anywhere` for long URLs/IDs, not `word-break: break-all` for prose.

### Modals and sheets

- On mobile, prefer a full-screen sheet or a bottom sheet for complex tasks.
- Keep the close control reachable.
- Trap focus and restore it.
- Do not cover the on-screen keyboard with the primary action.
- Confirm before discarding unsaved changes.

### Forms

- One column on mobile; do not use side-by-side fields unless they are naturally paired (e.g., expiry date).
- Labels above inputs.
- Inputs at least 16 px to avoid iOS zoom.
- Use the right `inputmode` and `autocomplete`.
- Keep the submit action visible or reachable after the last field.
- Do not use a fixed footer that covers the keyboard.

### Media

- Use `aspect-ratio` or width/height attributes to reserve space.
- Use `object-fit: cover` for art-directed crops, with a focal point.
- Do not autoplay video with sound.
- Provide captions and transcripts.

## Mobile forms

```html
<label for="email">Email</label>
<input
  id="email"
  name="email"
  type="email"
  autocomplete="email"
  inputmode="email"
  enterkeyhint="next"
/>
```

- `type` selects the keyboard; `inputmode` refines it; `autocomplete` enables autofill.
- Do not block paste.
- Use `enterkeyhint` to label the keyboard action.
- Keep the submit button enabled and validate on submit; if disabled, explain why.
- Show errors inline and preserve values.
- For long forms, autosave drafts and show when saved.
- Avoid `position: fixed` footers that collide with the keyboard.

### iOS specifics

- Inputs below 16 px trigger zoom on focus.
- `-webkit-appearance: none` can remove native affordances; use carefully.
- Test safe-area insets and the home indicator.
- Date/time inputs vary; provide a text fallback if needed.

### Android specifics

- Respect the system back gesture; do not trap it.
- Use Material touch targets and ripple/state layers where appropriate.
- Test predictive back behavior if the app targets Android 14+.

## Images and media

```html
<img
  src="tool-640.avif"
  srcset="tool-320.avif 320w, tool-640.avif 640w, tool-1280.avif 1280w"
  sizes="(min-width: 64rem) 33vw, 100vw"
  width="640"
  height="480"
  alt="A cordless drill in a labeled tool-library bin"
  loading="lazy"
  decoding="async"
/>
```

- Use AVIF/WebP with fallbacks.
- Provide `srcset`/`sizes` for responsive images.
- Always set dimensions or `aspect-ratio` to prevent CLS.
- Lazy-load below the fold; do not lazy-load the LCP image.
- Use `fetchpriority="high"` on the LCP image only.
- Use modern formats and compress.
- Use a CDN image resizer if available.

### Fonts

- Subset to the scripts you need.
- Preload at most one critical font.
- Use `font-display: swap` or `optional`.
- Avoid loading five weights; use variable fonts where possible.
- Match fallback metrics with `size-adjust`, `ascent-override`, and `descent-override` to reduce layout shift.

## Mobile performance

Mobile performance is design. A page that looks calm but janks on scroll does not feel calm.

### Targets

- LCP < 2.5 s at p75 on mobile.
- INP < 200 ms at p75.
- CLS < 0.1 at p75.
- Initial JS budget: use the profile table in `implementation.md`; do not restate it here. Dashboards can be larger but should be route-split.
- Keep the main thread free; long tasks < 50 ms.

### Techniques

- Server-render or statically generate content where possible.
- Split code by route and interaction.
- Hydrate only interactive islands.
- Virtualize long lists.
- Debounce/throttle scroll, resize, and input handlers.
- Move heavy computation to a worker.
- Avoid layout thrash: batch reads and writes.
- Use `content-visibility: auto` for long off-screen sections, with care for accessibility and find-in-page.
- Compress and cache assets.
- Use a performance budget in CI.

### Perceived performance

- Show skeletons that match the layout.
- Use optimistic UI for low-risk actions.
- Keep navigation instant with prefetching where appropriate.
- Avoid blocking the first render on non-critical fonts or scripts.
- Show progress for long operations; do not leave the UI frozen.

## Testing matrix

At minimum:

| Width | What to check |
|---|---|
| 320 px | Reflow, no horizontal scroll, text wrapping, target sizes |
| 360–390 px | Real phone, bottom nav, keyboard, safe areas |
| 768 px | Tablet, sidebar/columns, touch targets |
| 1024 px | Desktop, full nav, density |
| 1440 px | Wide desktop, max-width, line length |
| Landscape phone | Height-constrained layout, sticky bars, modals |
| 200% text | No clipping, no overlap |
| 400% zoom | Reflow, no two-dimensional scroll |
| Slow 3G | Loading states, image strategy, font swap |
| Reduced motion | No essential motion; final state visible |

Test on at least one real iOS device and one real Android device if the product targets mobile web. Emulators are useful but not sufficient.

## Common responsive bugs

| Bug | Cause | Fix |
|---|---|---|
| Horizontal page scroll | Fixed widths, negative margins, long words, grid blowout | `max-width: 100%`, `min-width: 0`, `overflow-wrap`, audit with DevTools |
| Content hidden behind sticky header | No scroll padding | `scroll-padding-top` and header height token |
| Content hidden behind bottom bar | No bottom padding | Add padding equal to bar height + safe area |
| Text clipped at 200% zoom | Fixed height/overflow hidden | Use `min-height`, allow wrapping |
| Flex child won't shrink | Default `min-width: auto` | Set `min-width: 0` |
| Grid child overflows | `minmax()` min too large | `minmax(min(100%, 18rem), 1fr)` |
| Full-height hero jumps | `100vh` and browser chrome | Use `svh`/`dvh` and test |
| Input zooms on iOS | Font size < 16 px | Set input font-size to 16 px |
| Table forces page scroll | Wide table | Wrap in a scroll region or reflow |
| Modal under keyboard | Fixed positioning + no visual viewport handling | Use a sheet, scroll into view, test |
| Images cause layout shift | No dimensions | `width`/`height` or `aspect-ratio` |
| Hover state sticks on touch | Hover-only styles | Guard with `@media (hover: hover)` |
| Tap target too small | Icon-only control | Expand hit area to 44×44 px |
| Drawer traps focus | Custom implementation | Use a tested dialog/drawer primitive |
| Safe area ignored | Fixed bottom bar | `env(safe-area-inset-bottom)` |

## Mobile checklist

- [ ] The primary job works at 320 px.
- [ ] No horizontal page scroll.
- [ ] Body text ≥16 px; inputs ≥16 px.
- [ ] Touch targets ≥44×44 px.
- [ ] Bottom nav has ≤5 items with labels.
- [ ] Sticky bars do not obscure content or focus.
- [ ] Safe-area insets respected.
- [ ] `100dvh`/`100svh` used instead of `100vh` for full-height layouts.
- [ ] Forms use correct input types, autocomplete, and inputmode.
- [ ] Images have dimensions and responsive sources.
- [ ] Loading, empty, error, and offline states work on a slow network.
- [ ] Reduced motion respected.
- [ ] Tested on a real phone, one-handed, with the keyboard open.
