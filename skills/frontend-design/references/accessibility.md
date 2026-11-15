# Accessibility

Accessibility is a design and engineering baseline, not a compliance layer added at the end. Target **WCAG 2.2 Level AA** for every interface, and go further where the audience or legal context requires it. This reference covers issues that most often break real interfaces; it is not a substitute for testing with assistive technology.

## WCAG 2.2 AA map

The criteria most relevant to interface design:

| Criterion | Level | Requirement |
|---|---|---|
| 1.1.1 Non-text Content | A | Meaningful images have alternatives; decorative images are hidden. |
| 1.3.1 Info and Relationships | A | Structure is conveyed in markup, not only visually. |
| 1.3.2 Meaningful Sequence | A | Reading order matches visual order. |
| 1.3.4 Orientation | AA | Do not lock portrait or landscape. |
| 1.3.5 Identify Input Purpose | AA | Use correct `autocomplete` tokens. |
| 1.4.1 Use of Color | A | Color is not the only way to convey meaning. |
| 1.4.3 Contrast (Minimum) | AA | 4.5:1 normal text; 3:1 large text. |
| 1.4.4 Resize Text | AA | Text resizes to 200% without loss of content or function. |
| 1.4.10 Reflow | AA | Content reflows at 320 CSS px without two-dimensional scrolling. |
| 1.4.11 Non-text Contrast | AA | UI components and meaningful graphics have 3:1. |
| 1.4.12 Text Spacing | AA | No loss when line, word, letter, and paragraph spacing increase. |
| 1.4.13 Content on Hover or Focus | AA | Hover/focus content is dismissible, hoverable, and persistent. |
| 2.1.1 Keyboard | A | All functionality is available from a keyboard. |
| 2.1.2 No Keyboard Trap | A | Focus can always move away. |
| 2.2.2 Pause, Stop, Hide | A | Moving or auto-updating content can be paused, stopped, or hidden. |
| 2.3.1 Three Flashes | A | Nothing flashes more than three times per second. |
| 2.4.1 Bypass Blocks | A | A skip link or equivalent bypass. |
| 2.4.2 Page Titled | A | Every page has a descriptive title. |
| 2.4.3 Focus Order | A | Focus order preserves meaning and operability. |
| 2.4.4 Link Purpose | A | Link purpose is clear from text or context. |
| 2.4.5 Multiple Ways | AA | More than one way to find a page, where appropriate. |
| 2.4.6 Headings and Labels | AA | Headings and labels describe topic or purpose. |
| 2.4.7 Focus Visible | AA | Keyboard focus is visible. |
| 2.4.11 Focus Not Obscured | AA | Sticky headers, banners, and overlays do not hide the focused control. |
| 2.5.1 Pointer Gestures | A | Multi-point or path gestures have single-pointer alternatives. |
| 2.5.2 Pointer Cancellation | A | Down-event does not trigger; up-event can cancel. |
| 2.5.3 Label in Name | A | The accessible name contains the visible label text. |
| 2.5.4 Motion Actuation | A | Device-motion actions have a UI alternative and can be disabled. |
| 2.5.7 Dragging Movements | AA | Dragging has a single-pointer or keyboard alternative. |
| 2.5.8 Target Size (Minimum) | AA | 24×24 CSS px, with documented exceptions. |
| 3.1.1 Language of Page | A | Page language is declared. |
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

AAA criteria worth adopting where feasible: 1.4.6 Contrast (Enhanced) 7:1; 1.4.8 Visual Presentation; 2.3.3 Animation from Interactions; 2.4.12 Focus Not Obscured (Enhanced); 2.4.13 Focus Appearance; 2.5.5 Target Size (Enhanced) 44×44 CSS px; 3.1.5 Reading Level.

## Semantic HTML first

Native elements provide keyboard behavior, focus, roles, and states. Use them before ARIA.

| Need | Use | Not |
|---|---|---|
| Action | `<button type="button">` | `<div onclick>` |
| Navigation | `<a href>` | `<span onclick>` |
| Structure | `<header>`, `<nav>`, `<main>`, `<footer>`, `<aside>` | Nested `<div>` soup |
| Heading | `<h1>`–`<h6>` | Styled `<div>` |
| List | `<ul>`, `<ol>`, `<dl>` | Stacked `<div>`s |
| Form | `<form>`, `<label>`, `<input>`, `<select>`, `<textarea>`, `<fieldset>`, `<legend>` | Divs without roles |
| Table | `<table>`, `<caption>`, `<th scope>`, `<td>` | Grid pretending to be a table |
| Emphasis | `<strong>`, `<em>` | Color or weight alone |
| Progress | `<progress>` or a status message | A div with color change |

- One `<main>` per page. Label multiple navs with `aria-label`. Use `header`/`footer` for page or section chrome.
- One `<h1>` is a good default; do not skip levels. Headings describe the content that follows, not visual size. Connect regions with `aria-labelledby` when needed.
- Set `lang` on the page and on passages in another language. Set `dir="rtl"` for RTL pages and use logical CSS.

## Keyboard access

- Tab reaches every interactive element in logical order; Shift+Tab moves backward predictably.
- Enter activates links and buttons; Space activates buttons. Arrow keys work in menus, tabs, radio groups, sliders, and composite widgets. Escape closes dialogs, menus, and popovers.
- Focus does not jump unexpectedly; no keyboard trap. Custom shortcuts do not override browser or assistive-technology shortcuts. Drag-and-drop has a keyboard alternative.
- DOM order matches visual order. Do not use `tabindex` greater than zero; `tabindex="-1"` is for programmatic focus. CSS `order`, absolute positioning, and grid placement can desync visual and DOM order; test it. When content is inserted or removed, decide where focus goes.
- Provide a skip link to main content.
- For menus, tabs, comboboxes, grids, and trees, follow the WAI-ARIA Authoring Practices or use a tested headless primitive (Radix, React Aria, Ark, Headless UI). Do not invent keyboard behavior.

## Focus

```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```

- Do not use `outline: none` without a visible replacement. Use `:focus-visible` for keyboard focus.
- Aim for a 2–3 px indicator with at least 3:1 contrast against adjacent colors. Test on dark, light, image, and accent backgrounds. `outline` survives forced-colors better than `box-shadow`.
- Sticky headers, cookie banners, chat widgets, and fixed footers can hide focus. Use `scroll-padding-top` equal to the sticky height, dismiss or move overlays, and test with keyboard navigation.
- On modal open, move focus to the dialog or first meaningful control; trap focus; remove background from the tab order with native modal semantics or `inert`; close on Escape; restore focus; prevent background scroll; keep the close control visible; work at 200% zoom and on small screens.
- On close, return focus to the trigger. On delete, move focus to a neighbor or list heading. On form errors, focus the summary or first invalid field. On SPA route change, focus the new heading or announce it. Do not move focus on every keystroke or blur.
- Use `<dialog>` with `showModal()` or a tested primitive.

## Screen readers and ARIA

Do not use ARIA if a native element already provides the semantics; incorrect ARIA is worse than none.

- Every interactive element needs a name. Prefer visible text; `aria-label` should contain the visible label text (2.5.3). Do not put essential information only in a tooltip.
- Decorative icons: `aria-hidden="true"` and `focusable="false"` for SVG. Meaningful images: `alt` describes purpose; decorative: `alt=""`. Linked images: alt describes the destination.
- Live regions: `polite` for non-urgent updates, `assertive` only for urgent errors. Keep the region in the DOM before updating text. For forms, inline `aria-describedby` plus a focusable summary is usually better than a live region alone. Do not move focus to announce status.
- Use `aria-expanded` for disclosure/menu triggers; `aria-selected` for tabs/options; `aria-pressed` for toggle buttons; `aria-checked` for custom checkboxes/switches (prefer native); `aria-current="page"` for current navigation; `aria-invalid` + `aria-describedby` for form errors; `aria-busy` for loading regions.
- Use `aria-hidden` only for content hidden from everyone; never on focusable content.
- Tables: use a real `<table>`, `<caption>` or associated heading, and `scope="col"`/`scope="row"`. Do not use tables for layout. For sortable columns, use a button and `aria-sort`. For responsive tables, keep header associations via stacked labels or a scroll region with an affordance.

## Forms

- Every input has a visible label; a placeholder is not a label. Use `<label for>`; group related fields with `fieldset`/`legend`. Mark required fields and explain the mark. Connect help and errors with `aria-describedby`.
- Errors identify the field and problem in text, suggest a correction, stay next to the field, and preserve entered values. Use `aria-invalid="true"`. For multiple errors, provide a focusable summary at the top and link each item to its field. Do not use color alone.
- Allow paste and password managers; do not block autofill. Offer passkeys or OAuth. If using OTP, allow paste and provide a non-cognitive alternative.
- Do not ask for the same information twice in a process; prefill or let the user select previous values.

## Visual accessibility

- Normal text 4.5:1; large text (≥24 px regular or ≥18.66 px bold) 3:1; UI components, icons, focus indicators, and meaningful graphics 3:1. Disabled controls are exempt but should remain recognizable. Text over images needs a reliable backing surface; measure the worst-case area. Placeholder text is text.
- Use `scripts/contrast.py` to check pairs, including alpha compositing.
- Color is not the only indicator: add text, icons, patterns, or position. Errors use icon + message; charts use labels/patterns/annotations; links in body text use underline or another non-color cue; status uses text labels, not red/green dots.
- Reflow at 320 CSS px without horizontal scrolling (except content that requires two-dimensional layout, such as a data table or map). At 400% zoom, content reflows and remains operable. Do not use fixed widths that clip; use `min-height` instead of fixed heights. Do not disable zoom; never add `user-scalable=no` or `maximum-scale=1`.
- Text spacing: test with line-height 1.5, letter-spacing 0.12em, word-spacing 0.16em, and paragraph spacing 2em. Content must not clip or overlap. Avoid fixed-height text boxes and `overflow: hidden` on text.
- Test Windows High Contrast / `forced-colors: active`; keep borders and focus indicators visible and do not rely on background images for meaning.
- Avoid images of text; use real text for localization, zoom, and screen readers. If an image of text is essential (a logo), provide alt text.

## Motion and animation

- Respect `prefers-reduced-motion: reduce`; provide the final state. Do not auto-play motion over five seconds without pause/stop. Do not flash more than three times per second. Do not use scroll-jacking or parallax as a required path.
- Carousels: previous/next and pause; stop on focus/hover. Animated charts: static view or table alternative. Motion-sensitive users can experience nausea, dizziness, and migraine. See `motion.md`.

## Touch, pointer, and dragging

- WCAG 2.2 AA target size: 24×24 CSS px with exceptions for inline links, essential presentation, and spacing. The practical web default is 44×44 CSS px; Apple recommends 44×44 pt and Material 48×48 dp. Do not treat a platform unit as a web conformance rule.
- Add padding or a pseudo-element to expand the hit area without changing visual size. Keep at least 8 px between adjacent targets.
- Trigger actions on `click`/`pointerup`, not `pointerdown`, so users can cancel by moving away. Do not require precision. Provide a visible pressed state.
- Dragging needs buttons, menus, or keyboard controls; support touch, mouse, and keyboard; provide clear affordances and feedback.
- Hover content must also appear on focus, be dismissible with Escape, hoverable, and persistent until dismissed. Do not put essential information only in a hover tooltip.

## Media

- Meaningful images: describe purpose in context. Decorative: `alt=""`. Complex images: longer description or data table. Do not use images of text.
- Captions for prerecorded video; transcripts for audio; audio description for visual information not in the main audio. Keyboard-operable controls with visible focus. Pause/stop for auto-playing media. Do not autoplay audio.

## Testing protocol

Automated tools catch only a subset. Combine:

- **Automated:** axe DevTools or `@axe-core/playwright`; Lighthouse accessibility; HTML validator; `scripts/contrast.py`; ESLint jsx-a11y.
- **Manual:** keyboard only (unplug the mouse, complete the primary task); screen reader (NVDA + Firefox/Chrome or VoiceOver + Safari) for names, roles, states, order, announcements; 200% text, 400% page zoom, and 320 px; reduced motion; forced colors; touch on a real phone one-handed with the keyboard open; slow network; long text, long words, no images, translated strings.
- Report the criterion, element, evidence, and fix. Do not claim "WCAG compliant" from an automated scan. Use the P0/P1/P2 severity in `quality-gates.md`.
