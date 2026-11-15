# Motion

Motion is a communication layer. It should explain where something came from, what changed, what is now possible, or what needs attention. If it does none of those, it is decoration — and decoration has a performance and accessibility cost.

## Contents

- [Principles](#principles)
- [Tokens](#tokens)
- [Patterns](#patterns)
- [Performance](#performance)
- [Accessibility](#accessibility)
- [Implementation notes](#implementation-notes)
- [Motion audit](#motion-audit)

## Principles

1. **Purpose before effect.** Name what the motion communicates. If you cannot, remove it.
2. **One orchestrated moment.** A single page-load sequence or one meaningful transition lands better than scattered effects.
3. **Motion follows action.** Feedback for a click, opening, expanding, confirming, or dragging is welcome. Ambient motion is not.
4. **Spatial continuity.** Elements should enter from and exit toward a plausible origin. A dialog scales from its trigger; a sheet slides from the edge; a list item collapses into its source.
5. **Fast enough to feel responsive.** UI feedback should be perceptible but not a wait. Exits are faster than entrances.
6. **Interruptible.** User input cancels or redirects motion immediately. Never block the interface during an animation.
7. **Respect the user.** Reduced motion, vestibular disorders, and low-power devices are design constraints, not edge cases.
8. **Restraint.** If the static interface is unclear, motion will not fix it. Establish hierarchy first.

## Tokens

`assets/tokens.css` defines the canonical `--duration-*` and `--ease-*` values. Use those tokens, not one-off durations; a component at 137 ms next to one at 250 ms feels broken.

| Interaction | Duration | Easing |
|---|---|---|
| Hover/press feedback | `--duration-instant`–`--duration-fast` | `--ease-out` |
| Tooltip/popover | `--duration-fast` | `--ease-out` |
| Dropdown/menu | `--duration-fast`–`--duration-normal` | `--ease-out` |
| Dialog/sheet | `--duration-normal`–`--duration-slow` | `--ease-out` |
| Expand/collapse | `--duration-normal`–`--duration-slow` | `--ease-in-out` |
| Page transition | `--duration-slow`–`--duration-slower` | `--ease-in-out` |
| Exit | 60–70% of enter | `--ease-in` |
| Large cinematic moment | `--duration-slower` or custom, sparingly | custom |

### Easing character

- **ease-out**: arriving; fast start, gentle stop. Default for entrances.
- **ease-in**: leaving; gentle start, fast exit. Default for exits.
- **ease-in-out**: moving between two states; good for expand/collapse.
- **spring**: direct manipulation, playful brands, physical objects. Use with restraint; overshoot can feel toy-like in enterprise UI.
- **linear**: progress bars, spinners, constant-rate loops. Not for spatial movement.

## Patterns

### Page load

- One orchestrated sequence: the hero's type, image, and primary action settle into place.
- Stagger by `--duration-instant` or a fraction of the entrance duration, not 200 ms.
- Keep the total under ~700 ms; do not make users wait for the show.
- Respect reduced motion: show the final state immediately.

### Hover and press

- Hover: subtle color, border, or elevation change; no layout shift.
- Press: 0.97–0.99 scale or 1 px translate; return on release.
- Do not animate every card on hover; it creates noise and costs performance.
- Hover is an enhancement, not the only affordance; use `--duration-fast` and `--ease-out`.

### Expand and collapse

- Animate height only when necessary; prefer `grid-template-rows: 0fr -> 1fr` or a measured height.
- Use `overflow: clip` and `min-height: 0` for grid children.
- Keep focus inside the expanded content visible.
- Do not use `display: none` if you need an exit animation; use `hidden`/`inert` after the transition.
- Use `--duration-normal`–`--duration-slow` with `--ease-in-out`.

### Dialog and sheet

- Enter: fade + scale from 0.96 to 1, or slide from the edge for a sheet.
- Exit: faster fade/scale down.
- Use a scrim that isolates the foreground.
- Move focus in; restore focus out.
- Do not animate the backdrop blur if it causes jank on low-end devices.

```css
dialog {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  transition: opacity var(--duration-normal) var(--ease-out),
              transform var(--duration-normal) var(--ease-out),
              overlay var(--duration-normal) allow-discrete,
              display var(--duration-normal) allow-discrete;
}
dialog[open] {
  opacity: 1;
  transform: translateY(0) scale(1);
}
@starting-style {
  dialog[open] {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
}
```

`@starting-style` is progressive enhancement; ensure the final state is visible without it.

### List reorder

- Use `transform` for movement, not `top`/`left`.
- FLIP (First, Last, Invert, Play) is the standard technique.
- Keep item identity stable with keys.
- Cancel prior transitions when a new reorder starts.
- Provide a non-motion path for reduced motion.

### Shared element transition

- Use the View Transitions API for same-document and cross-document transitions where supported.
- Provide a fallback without the transition.
- Keep the shared element's shape and position plausible.
- Do not animate between unrelated elements.

```js
if (document.startViewTransition) {
  document.startViewTransition(() => updateDom());
} else {
  updateDom();
}
```

### Loading

- Under ~100 ms: no indicator.
- 100 ms–1 s: subtle inline busy state.
- Over 1 s: skeleton or progress.
- Over 10 s: background task with a way to leave and return.
- Use a skeleton that matches the final layout.
- Do not use a spinner for content that has a known shape.
- Announce busy state without moving focus.

### Success and error

- Success: brief check, color shift, or toast; do not celebrate with confetti for routine actions.
- Error: shake is a cliché and can be alarming; use a clear inline message and focus.
- For destructive actions, a short confirm transition is enough; do not dramatize.
- Use `aria-live` for announcements; do not rely on motion.

### Scroll-driven motion

- Use CSS scroll-driven animations or IntersectionObserver; avoid `window.addEventListener('scroll')` for animation.
- Use one reveal, not a fade-up on every section.
- Do not hijack scroll or pin sections for essential content.
- Respect reduced motion; show the final state.
- Keep the unanimated default visible. Never set `opacity: 0` on the base state; unsupported browsers would hide the content.
- Test on low-end mobile.

```css
@media (prefers-reduced-motion: no-preference) {
  .reveal {
    animation: reveal linear both;
    animation-timeline: view();
    animation-range: entry 10% cover 30%;
  }
}
@keyframes reveal {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Auto-rotating content

- Provide previous/next and play/pause controls.
- Stop on focus and hover.
- Stop when reduced motion is requested.
- Do not auto-advance so fast that people cannot read.
- Announce slide changes politely; do not move focus.

## Performance

### Animate the compositor-friendly properties

Prefer:

- `transform`
- `opacity`
- `filter` (with caution)
- `clip-path` (with caution)

Avoid animating:

- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `box-shadow` (can be expensive; animate a pseudo-element's opacity instead)
- `background-position` on large images
- `backdrop-filter` on large areas

### Avoid layout thrash

- Batch DOM reads and writes.
- Use `requestAnimationFrame` for visual updates.
- Do not read `offsetHeight` inside a scroll handler that also writes styles.
- Use `will-change: transform` sparingly and remove it after the animation.
- Use `contain: layout paint` for isolated animated regions where safe.

### Keep the main thread free

- Use CSS transitions/animations for simple state changes.
- Use the Web Animations API for JS-driven animation.
- Use a spring library only when physics is needed.
- Move heavy computation to a worker.
- Do not mount a large animation tree for a small effect.
- Virtualize long lists before animating them.

### Measure

- Use Chrome DevTools Performance panel; look for long tasks and dropped frames.
- Test on a mid-range Android device, not only a desktop.
- Check CPU throttling 4× and network throttling.
- Measure INP; animation that blocks input is a failure.
- Use `prefers-reduced-motion` and low-power mode.

## Accessibility

- `prefers-reduced-motion: reduce` must remove or substantially reduce non-essential motion.
- Do not merely shorten durations; remove parallax, scroll-jacking, and large movement.
- Keep the final state visible; do not leave content at `opacity: 0`.
- Provide pause/stop for auto-rotating or auto-updating content (WCAG 2.2.2).
- Do not flash more than three times per second (WCAG 2.3.1).
- Provide a static alternative for animated charts or complex transitions.
- Motion must not be the only way to understand a change; pair it with text or state.
- Do not block input during animation.
- Ensure focus remains visible during and after transitions.
- Test with reduced motion, zoom, and a screen reader.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Prefer targeted rules:

```css
@media (prefers-reduced-motion: reduce) {
  .hero-media,
  .parallax,
  .auto-rotate {
    animation: none !important;
    transition: none !important;
  }
  .reveal {
    opacity: 1;
    transform: none;
  }
}
```

## Implementation notes

### CSS-first

Use CSS transitions for hover, focus, press, expand, and simple entrance. Use `@starting-style` for entry animations where supported. Use `transition-behavior: allow-discrete` for `display`/`overlay` transitions.

### JavaScript

Use the Web Animations API for imperative animations with token durations/easings. Cancel in-flight animations on state change and clean up when finished.

### React and Next.js

- Prefer CSS for simple interactions; avoid a motion library for a hover state.
- Use a client component only for the animated leaf, not the whole page.
- Clean up animations and observers in `useEffect`.
- Do not use `useState` for continuous pointer motion; use motion values or refs.
- Use `layout`/`layoutId` for shared element transitions when the library is already present.
- Respect `useReducedMotion()`.

### GSAP / ScrollTrigger

Use for complex, isolated scroll storytelling, not routine UI. Register plugins once, clean up on unmount, use `gsap.matchMedia()` for reduced motion, avoid scroll hijacking, and do not mix GSAP with a React motion library in one component tree.

### View Transitions

Use for route changes and shared elements when supported, with a fallback that updates the DOM immediately. Keep transitions short (`--duration-slow`–`--duration-slower`), avoid unrelated layouts, and respect reduced motion.

## Motion audit

- [ ] Every animation has a named purpose.
- [ ] There is one orchestrated moment, not effects on every section.
- [ ] Durations and easings come from tokens.
- [ ] Entrances use ease-out; exits use ease-in and are faster.
- [ ] Only `transform`/`opacity` are animated for movement.
- [ ] No layout shift or CLS from animation.
- [ ] Input is never blocked.
- [ ] Rapid state changes cancel prior animations.
- [ ] `prefers-reduced-motion` removes non-essential motion and keeps the final state.
- [ ] Auto-rotating content has pause/stop and stops on focus.
- [ ] No flashing above three times per second.
- [ ] Focus remains visible during and after transitions.
- [ ] Tested on a mid-range mobile device with CPU throttling.
- [ ] Animation libraries are isolated and cleaned up.
- [ ] The interface is understandable with motion disabled.
