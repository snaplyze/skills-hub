# Accessibility

Accessibility is a design and engineering baseline, not a compliance layer added at the end. Target **WCAG 2.2 Level AA** for every interface, and go further where the product's audience or legal context requires it.

This reference covers the issues that most often break real interfaces. It is not a substitute for testing with assistive technology.

## Contents

- [WCAG 2.2 AA map](#wcag-22-aa-map)
- [Semantic HTML first](#semantic-html-first)
- [Keyboard access](#keyboard-access)
- [Focus](#focus)
- [Screen readers and ARIA](#screen-readers-and-aria)
- [Forms](#forms)
- [Visual accessibility](#visual-accessibility)
- [Motion and animation](#motion-and-animation)
- [Touch, pointer, and dragging](#touch-pointer-and-dragging)
- [Media](#media)
- [Testing protocol](#testing-protocol)
- [Common failures and fixes](#common-failures-and-fixes)

## WCAG 2.2 AA map

The criteria most relevant to interface design:

| Criterion | Level | What it means in practice |
|---|---|---|
| 1.1.1 Non-text Content | A | Meaningful images have alternatives; decorative images are hidden. |
| 1.3.1 Info and Relationships | A | Structure is conveyed in markup, not only visually. |
| 1.3.2 Meaningful Sequence | A | Reading order matches the visual order. |
| 1.3.4 Orientation | AA | Do not lock the interface to portrait or landscape. |
| 1.3.5 Identify Input Purpose | AA | Use correct `autocomplete` tokens. |
| 1.4.1 Use of Color | A | Color is not the only way to convey meaning. |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 normal text; 3:1 large text. |
| 1.4.4 Resize Text | AA | Text can resize to 200% without loss of content or function. |
| 1.4.10 Reflow | AA | Content reflows at 320 CSS px without two-dimensional scrolling. |
| 1.4.11 Non-text Contrast | AA | UI components and meaningful graphics have 3:1 contrast. |
| 1.4.12 Text Spacing | AA | No loss of content when users increase line, word, letter, and paragraph spacing. |
| 1.4.13 Content on Hover or Focus | AA | Hover/focus content is dismissible, hoverable, and persistent. |
| 2.1.1 Keyboard | A | All functionality is available from a keyboard. |
| 2.1.2 No Keyboard Trap | A | Focus can always move away. |
| 2.2.2 Pause, Stop, Hide | A | Moving or auto-updating content can be paused, stopped, or hidden. |
| 2.3.1 Three Flashes | A | Nothing flashes more than three times per second. |
| 2.4.1 Bypass Blocks | A | A skip link or equivalent bypass. |
| 2.4.2 Page Titled | A | Every page has a descriptive title. |
| 2.4.3 Focus Order | A | Focus order preserves meaning and operability. |
| 2.4.4 Link Purpose | A | Link purpose is clear from the link text or context. |
| 2.4.5 Multiple Ways | AA | More than one way to find a page, where appropriate. |
| 2.4.6 Headings and Labels | AA | Headings and labels describe the topic or purpose. |
| 2.4.7 Focus Visible | AA | Keyboard focus is visible. |
| 2.4.11 Focus Not Obscured | AA | Sticky headers, banners, and overlays do not hide the focused control. |
| 2.5.1 Pointer Gestures | A | Multi-point or path gestures have single-pointer alternatives. |
| 2.5.2 Pointer Cancellation | A | Down-event does not trigger the action; up-event can cancel. |
| 2.5.3 Label in Name | A | The accessible name contains the visible label text. |
| 2.5.4 Motion Actuation | A | Device-motion actions have a UI alternative and can be disabled. |
| 2.5.7 Dragging Movements | AA | Dragging has a single-pointer or keyboard alternative. |
| 2.5.8 Target Size (Minimum) | AA | 24×24 CSS px, with documented exceptions. |
| 3.1.1 Language of Page | A | The page language is declared. |
| 3.2.1 On Focus | A | Focus does not trigger an unexpected change of context. |
| 3.2.2 On Input | A | Input does not trigger an unexpected change of context. |
| 3.2.3 Consistent Navigation | AA | Navigation is in the same relative order across pages. |
| 3.2.4 Consistent Identification | AA | Components with the same function are identified consistently. |
| 3.2.6 Consistent Help | A | Help mechanisms appear in the same relative order. |
| 3.3.1 Error Identification | A | Errors are identified in text. |
| 3.3.2 Labels or Instructions | A | Labels or instructions are provided for input. |
| 3.3.3 Error Suggestion | AA | Suggest a correction when known. |
| 3.3.4 Error Prevention | AA | Confirm, review, or reverse legal/financial/data submissions. |
| 3.3.7 Redundant Entry | A | Do not ask for the same information twice in a process. |
| 3.3.8 Accessible Authentication | AA | No cognitive function test without an alternative or assistance. |
| 4.1.2 Name, Role, Value | A | Custom controls expose name, role, state, and value. |
| 4.1.3 Status Messages | AA | Status messages are announced without moving focus. |

AAA criteria worth adopting where feasible:

- 1.4.6 Contrast (Enhanced): 7:1 normal text, 4.5:1 large text.
- 1.4.8 Visual Presentation: user-selectable colors, line width, spacing.
- 2.3.3 Animation from Interactions: motion can be disabled.
- 2.4.12 Focus Not Obscured (Enhanced): the entire focused component is visible.
- 2.4.13 Focus Appearance: a strong, high-contrast focus indicator.
- 2.5.5 Target Size (Enhanced): 44×44 CSS px.
- 3.1.5 Reading Level: plain language where possible.

## Semantic HTML first

Native elements give you keyboard behavior, focus, roles, and states for free. Use them before reaching for ARIA.

| Need | Use | Not |
|---|---|---|
| Action | `<button type="button">` | `<div onclick>` |
| Navigation | `<a href>` | `<span onclick>` |
| Page structure | `<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>` | Nested `<div>` soup |
| Section heading | `<h1>`–`<h6>` | Styled `<div>` |
| List | `<ul>`, `<ol>`, `<dl>` | A stack of `<div>`s |
| Form | `<form>`, `<label>`, `<input>`, `<select>`, `<textarea>`, `<fieldset>`, `<legend>` | Custom divs without roles |
| Table | `<table>`, `<caption>`, `<th scope>`, `<td>` | CSS grid pretending to be a table |
| Emphasis | `<strong>`, `<em>` | Color or font weight alone |
| Progress | `<progress>` or a status message | A div with a color change |

### Landmarks and headings

- One `<main>` per page.
- Use `<nav>` for navigation regions; label multiple navs with `aria-label`.
- Use `<header>` and `<footer>` for page or section chrome.
- One `<h1>` per page is a good default; do not skip heading levels.
- Headings describe the content that follows, not the visual size.
- Use `aria-labelledby` to connect a region to its heading when needed.

### Language

```html
<html lang="en">
  <body>
    <p>Этот текст на русском.</p>
    <p lang="ru">Этот текст на русском.</p>
  </body>
</html>
```

Set `lang` on the page and on passages in another language. Set `dir="rtl"` for RTL pages and use logical CSS properties.

## Keyboard access

Every action must be operable with a keyboard alone.

### Checklist

- [ ] Tab reaches every interactive element in a logical order.
- [ ] Shift+Tab moves backward predictably.
- [ ] Enter activates links and buttons (buttons also respond to Space).
- [ ] Arrow keys work in menus, tabs, radio groups, sliders, and composite widgets.
- [ ] Escape closes dialogs, menus, and popovers.
- [ ] Focus does not jump unexpectedly.
- [ ] No keyboard trap; focus can leave every component.
- [ ] Custom shortcuts do not override browser or assistive-technology shortcuts.
- [ ] Drag-and-drop has a keyboard alternative.

### Focus order

- DOM order should match visual order.
- Do not use `tabindex` greater than zero. Use DOM order instead.
- `tabindex="-1"` is for programmatic focus (e.g., a dialog container, an error summary).
- CSS `order`, absolute positioning, and grid placement can create a mismatch between visual and DOM order; test it.
- When content is inserted, decide where focus should go; do not leave it on a removed element.

### Skip link

```html
<a class="skip-link" href="#main">Skip to main content</a>
...
<main id="main" tabindex="-1">...</main>
```

```css
.skip-link {
  position: absolute;
  inset-block-start: -100%;
  inset-inline-start: 1rem;
  z-index: var(--z-tooltip);
  padding: 0.75rem 1rem;
  background: var(--color-surface);
  color: var(--color-text);
  border: 2px solid var(--color-focus);
  border-radius: var(--radius-sm);
}
.skip-link:focus {
  inset-block-start: 1rem;
}
```

### Composite widgets

For menus, tabs, comboboxes, grids, and trees, follow the WAI-ARIA Authoring Practices. Do not invent keyboard behavior:

- Menu: Arrow Down/Up, Home/End, Escape; Enter/Space activates.
- Tabs: Arrow Left/Right (or Up/Down for vertical), Home/End; only the active tab is in the tab order.
- Combobox: Arrow Down opens, Arrow Up/Down moves, Enter selects, Escape closes.
- Radio group: arrow keys move selection; only one radio is in the tab order.
- Slider: Arrow keys adjust, Home/End jump to min/max, Page Up/Down for larger steps.

Use a tested headless library (Radix, React Aria, Ark, Headless UI) when possible. Re-implementing these is a common source of bugs.

## Focus

### Visible focus

```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```

- Do not use `outline: none` without a visible replacement.
- Use `:focus-visible` for keyboard focus; do not hide focus for mouse users at the cost of keyboard users.
- Aim for a 2–3 px indicator with at least 3:1 contrast against adjacent colors.
- Test on dark, light, image, and accent backgrounds.
- `outline` is better than `box-shadow` for forced-colors mode.

### Focus not obscured

Sticky headers, cookie banners, chat widgets, and fixed footers can hide the focused element. Use:

```css
html {
  scroll-padding-top: calc(var(--header-height) + 1rem);
}
```

Also dismiss or move overlays when they cover focus, and test with keyboard navigation from top to bottom.

### Focus management

- On opening a modal: move focus to the dialog or its first meaningful control.
- On closing: return focus to the trigger.
- On deleting an item: move focus to a sensible neighbor or the list heading.
- On submitting a form with errors: focus the error summary or the first invalid field.
- On route change in a SPA: move focus to the new page heading or announce the change.
- Do not move focus on every keystroke or blur.

### Modal focus trap

Use `<dialog>` with `showModal()` or a tested primitive. A correct modal:

- has an accessible name;
- traps focus inside while open;
- removes background content from the tab order with native modal semantics or `inert`;
- closes on Escape;
- restores focus to the trigger;
- prevents background scroll;
- does not hide the close control;
- works at 200% zoom and on small screens.

## Screen readers and ARIA

### The first rule of ARIA

Do not use ARIA if a native element already provides the semantics. Incorrect ARIA is worse than no ARIA.

### Accessible names

Every interactive element needs a name:

```html
<button type="button" aria-label="Close dialog">
  <svg aria-hidden="true" focusable="false">...</svg>
</button>
```

- Prefer visible text; `aria-label` should contain the visible label text (2.5.3).
- Do not put essential information only in a tooltip.
- Decorative icons: `aria-hidden="true"` and `focusable="false"` for SVG.
- Meaningful images: `alt` describes purpose; decorative images: `alt=""`.
- Linked images: alt describes the destination.

### Live regions

Use live regions for status messages that appear without a page reload:

```html
<div role="status" aria-live="polite" aria-atomic="true">
  3 results found
</div>
```

- `polite` for non-urgent updates; `assertive` only for urgent errors.
- Do not announce every keystroke or every badge change.
- Keep the live region in the DOM before updating its text.
- For form errors, inline `aria-describedby` plus a focusable summary is usually better than a live region alone.
- Do not move focus to announce a status message.

### State and properties

- `aria-expanded` for disclosure/menu triggers.
- `aria-selected` for tabs/options.
- `aria-pressed` for toggle buttons.
- `aria-checked` for custom checkboxes/switches (prefer native).
- `aria-current="page"` for the current navigation item.
- `aria-invalid` and `aria-describedby` for form errors.
- `aria-busy` for loading regions.
- `aria-hidden` only for content that is truly hidden from everyone; never on focusable content.

### Tables

```html
<table>
  <caption>Reservations for this week</caption>
  <thead>
    <tr>
      <th scope="col">Tool</th>
      <th scope="col">Pickup</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>...</tbody>
</table>
```

- Use `<caption>` or an associated heading.
- Use `scope="col"` and `scope="row"`.
- Do not use tables for layout.
- For sortable columns, use a button in the header and `aria-sort`.
- For responsive tables, do not remove header associations; use a stacked pattern with labels or a scroll region with an affordance.

## Forms

### Labels

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" autocomplete="email" />
```

- Every input has a visible label.
- Placeholder is not a label.
- Use `fieldset`/`legend` for groups.
- Mark required fields and explain the mark.
- Use `aria-describedby` for help text and errors.

### Errors

```html
<label for="date">Pickup date</label>
<input
  id="date"
  name="date"
  type="date"
  aria-invalid="true"
  aria-describedby="date-help date-error"
/>
<p id="date-help">Available Saturday and Sunday.</p>
<p id="date-error">Choose a date within the next 14 days.</p>
```

- Identify the field and the problem in text.
- Suggest a correction when possible.
- Keep the error next to the field.
- For multiple errors, provide a focusable summary at the top; link each item to its field.
- Do not use color alone.
- Preserve entered values.

### Accessible authentication

- Allow paste and password managers.
- Do not block autofill.
- Offer passkeys or OAuth.
- If using OTP, allow paste and provide a non-cognitive alternative.
- Do not require memorizing or transcribing a code without an alternative.

### Redundant entry

Do not ask for the same information twice in a process. Prefill or let the user select previously entered values.

## Visual accessibility

### Contrast

- Normal text: 4.5:1.
- Large text (≥24 px regular or ≥18.66 px bold): 3:1.
- UI components, icons, focus indicators, and meaningful graphics: 3:1.
- Disabled controls are exempt but should remain recognizable.
- Text over images needs a reliable backing surface or overlay; measure the worst-case area.
- Placeholder text is text; if it carries information, it needs contrast.

Use `scripts/contrast.py` to check pairs, including alpha compositing.

### Color is not the only indicator

- Add text, icons, patterns, or position.
- For errors, use an icon and message.
- For charts, use labels, patterns, or direct annotations.
- For links in body text, use underline or another non-color cue.
- For status, use text labels, not just red/green dots.

### Reflow and zoom

- Content must work at 320 CSS px wide without horizontal scrolling (except for content that requires two-dimensional layout, such as a data table or map).
- At 400% zoom, content reflows and remains operable.
- Do not use fixed widths that clip.
- Do not disable zoom: `<meta name="viewport" content="width=device-width, initial-scale=1">`; never add `user-scalable=no` or `maximum-scale=1`.
- Use `min-height` instead of fixed heights for text containers.
- Test with browser zoom and with increased default font size.

### Text spacing

Test with:

```css
* {
  line-height: 1.5 !important;
  letter-spacing: 0.12em !important;
  word-spacing: 0.16em !important;
}
p {
  margin-block-end: 2em !important;
}
```

Content must not be clipped or overlap. Avoid fixed-height text boxes and `overflow: hidden` on text.

### Forced colors and high contrast

Test Windows High Contrast / `forced-colors: active`. Use system colors where appropriate, keep borders and focus indicators visible, and do not rely on background images for meaning.

### Images of text

Avoid images of text. Use real text for localization, zoom, and screen readers. If an image of text is essential (e.g., a logo), provide alt text.

## Motion and animation

- Respect `prefers-reduced-motion: reduce`.
- Do not auto-play motion that lasts more than five seconds without a pause/stop control.
- Do not flash more than three times per second.
- Do not use scroll-jacking or parallax as a required path.
- Provide a static final state when motion is reduced.
- For carousels, provide previous/next and pause; stop on focus/hover.
- For animated charts, provide a static view or a table alternative.
- Motion-sensitive users can experience nausea, dizziness, and migraine; "reduce" is not cosmetic.

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

Prefer targeted removal over the global sledgehammer, but ensure the final state is still visible.

## Touch, pointer, and dragging

### Target size

- WCAG 2.2 AA: 24×24 CSS px, with exceptions for inline links, essential presentation, and spacing.
- Practical design target: 44×44 px (Apple HIG) or 48×48 dp (Material).
- Add padding or a pseudo-element to expand the hit area without changing the visual size.
- Keep at least 8 px between adjacent targets.

```css
.icon-button {
  min-inline-size: 44px;
  min-block-size: 44px;
  display: inline-grid;
  place-items: center;
}
```

### Pointer cancellation

- Trigger actions on `click`/`pointerup`, not `pointerdown`, so users can cancel by moving away.
- Do not require precision for small controls.
- Provide a visible pressed state.

### Dragging

- Provide buttons, menus, or keyboard controls for reordering, resizing, and selecting.
- Dragging must not be the only way to complete a task.
- Support touch, mouse, and keyboard.
- Provide clear affordances and feedback.

### Hover-only content

- Hover content must also appear on focus.
- It must be dismissible (Escape), hoverable (the pointer can move into it), and persistent until dismissed.
- Do not put essential information only in a hover tooltip.

## Media

### Images

- Meaningful images: describe the purpose in context.
- Decorative images: `alt=""`.
- Complex images: provide a longer description or data table.
- Do not use images of text.
- Provide captions for video and transcripts for audio.
- Do not autoplay audio.

### Video and audio

- Captions for prerecorded video.
- Transcript for audio.
- Audio description for visual information not conveyed in the main audio.
- Keyboard-operable controls with visible focus.
- Pause/stop for auto-playing media.

## Testing protocol

Automated tools catch only a subset. Combine:

### Automated

- axe DevTools or `@axe-core/playwright`.
- Lighthouse accessibility audit.
- HTML validator.
- Contrast script.
- ESLint jsx-a11y rules where applicable.

### Manual

- **Keyboard only**: unplug the mouse; complete the primary task.
- **Screen reader**: NVDA + Firefox/Chrome on Windows, or VoiceOver + Safari on macOS/iOS. Check names, roles, states, reading order, and announcements.
- **Zoom**: 200% text, 400% page zoom, and a 320 px viewport.
- **Reduced motion**: enable the OS setting; verify no essential content disappears.
- **Forced colors**: Windows High Contrast mode.
- **Touch**: test on a real phone, one-handed, with the keyboard open.
- **Slow network**: throttle to 3G; check loading and error states.
- **Content stress**: long text, long words, no images, translated strings.

### Severity

| Severity | Definition | Action |
|---|---|---|
| Critical | Blocks a task for a group of users; legal risk | Fix before release |
| Major | Significant difficulty or workaround required | Fix before release |
| Minor | Causes hesitation or inefficiency | Fix when possible |
| Cosmetic | Noticeable but not functionally harmful | Low priority |

Report the criterion, the element, the evidence, and the fix. Do not claim "WCAG compliant" based on an automated scan.

## Common failures and fixes

| Failure | Why it matters | Fix |
|---|---|---|
| `<div onclick>` as a button | Not focusable, no role, no keyboard | Use `<button>` |
| `outline: none` | Keyboard users lose their place | Add `:focus-visible` outline |
| Placeholder-only label | Disappears on input; inaccessible name | Add a visible `<label>` |
| Icon-only button without a name | Screen reader says "button" | Add `aria-label` |
| Color-only error | Colorblind users miss it | Add icon + text |
| Low-contrast gray text | Unreadable in sunlight/low vision | Increase contrast to 4.5:1 |
| `tabindex="1"` | Breaks natural order | Use DOM order |
| Modal without focus trap | Keyboard escapes behind the dialog | Use `<dialog>` or a primitive |
| Sticky header covers focus | Focused control is invisible | `scroll-padding-top` + overlay handling |
| Auto-rotating carousel | Cannot be paused; motion sensitivity | Add pause/stop; stop on focus |
| Drag-only reorder | Impossible by keyboard | Add move up/down buttons |
| Tiny icon targets | Hard to tap | Expand to 44×44 px |
| `user-scalable=no` | Prevents zoom | Remove it |
| Fixed-height text box | Clips at 200% zoom | Use `min-height` and wrapping |
| `aria-hidden` on focusable content | Screen reader cannot reach it | Remove or hide properly |
| Redundant ARIA on native elements | Conflicting semantics | Use native semantics |
| Missing `lang` | Wrong pronunciation | Set `<html lang>` |
| Fake links/buttons in a table | Keyboard and screen reader issues | Use real controls |
| Toast-only errors | Easy to miss; not announced | Inline error + live region |
| No skip link | Keyboard users traverse nav on every page | Add a skip link |

## Definition of done

- [ ] Semantic landmarks and heading hierarchy.
- [ ] All actions keyboard operable; no traps.
- [ ] Visible focus everywhere; focus not obscured.
- [ ] Contrast checked in both themes.
- [ ] Forms have labels, instructions, and linked errors.
- [ ] Images have appropriate alternatives; decorative images hidden.
- [ ] Custom widgets follow APG patterns or use a tested primitive.
- [ ] Live regions announce status without moving focus.
- [ ] Target sizes meet 24×24 AA and preferably 44×44.
- [ ] Reflow at 320 px, 200% text, 400% zoom.
- [ ] Reduced motion and pause controls.
- [ ] Tested with keyboard and at least one screen reader.
