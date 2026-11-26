# UX Patterns

Use this reference for flows, navigation, forms, feedback, states, UX copy, and research-lite decisions. The goal is not to apply a pattern because it is familiar. It is to reduce the effort between a person's intent and the outcome they need.

## Start with the job

Describe the user's job, not the feature:

> When **[situation]**, I want to **[motivation]**, so I can **[outcome]**.

Examples:

- "When I need a drill for one shelf, I want to know whether a neighbor has one available this weekend, so I can finish the job without buying a tool I'll use once."
- "When a payment fails, I want to know why and what to try next, so I don't lose the order."

Then map the flow:

```text
Entry -> Step 1 -> Decision -> Step 2 -> Failure path -> Recovery -> Success -> Exit
```

For each step, define:

- what the person sees;
- what they must decide or do;
- what can go wrong;
- how they recover;
- what confirms success;
- what happens if they leave and come back.

If a flow has no failure path, it is not designed yet.

## Flows and information architecture

### Navigation model

Choose one primary model and keep it consistent: top bar (marketing, small apps), sidebar (dashboards, admin), bottom nav (3–5 mobile areas), tabs (peer views), breadcrumbs (deep hierarchies), or search-first (large catalogs). Watch mobile fit, too many items, nested navigation, and search without empty/no-result states.

Rules: primary navigation stays in the same place; current location is more than color; do not mix tabs, sidebar, and bottom nav at one level; deep-link key screens and shareable filters/tabs/pagination; preserve scroll, filters, and form state on back; never break the back button; keep the logo linked home.

### Hierarchy and labels

- Group navigation by the user's mental model, not the org chart.
- Use familiar labels; do not invent clever names for standard destinations.
- Keep labels short, specific, and parallel in grammar.
- Avoid more than 7 ± 2 top-level items where possible.
- Put secondary and destructive actions out of the primary path.
- Use breadcrumbs for three or more levels of hierarchy.

### Search and filtering

- Make search easy to find; placeholder text is not a label.
- Show recent and suggested queries when useful.
- Support empty, no-results, and error states.
- Show active filters as removable chips; provide a clear "clear all".
- Keep filters in the URL when the state should be shareable.
- Announce result counts to screen readers with a polite status.
- Do not reset filters unexpectedly when the user changes sort or page.

### Onboarding

- Show value before asking for work.
- Ask only for information needed now; defer the rest.
- Use progressive disclosure, not a wall of setup.
- Allow skip and return.
- Show progress for multi-step onboarding.
- Confirm what was set up and what happens next.

### Authentication

Allow paste and password managers. Use correct `autocomplete` tokens (`username`, `current-password`, `new-password`, `one-time-code`), offer passkeys or OAuth, and provide a non-cognitive alternative for memory tests (WCAG 3.3.8). Show requirements before submission, provide recovery, and avoid account enumeration unless intentional.

### Checkout and payments

Show total cost, taxes, and fees before the final step; no surprise charges. Support guest checkout, preserve entered data on error, and show an order summary and confirmation. Make cancellation and refund paths findable. Do not use fake urgency or countdowns.

## Page and screen patterns

### Landing page

A landing page has one job: help a specific audience take the next step. The hero should answer:

- What is this?
- Who is it for?
- What can I do now?
- Why should I trust it?

Avoid the default centered badge + headline + two buttons + logo marquee. Choose a composition that fits the subject: a live demo, a product image, a search box, a map, a specimen, a story, a calculator, a comparison.

Sections should follow the user's questions, not a template:

```text
Hook -> Problem/context -> How it works -> Proof -> Objections -> Next step
```

Proof can be a demo, a case study, a transparent metric, a sample, a guarantee, or a real testimonial. Do not invent proof.

### Dashboard

Lead with the decision the dashboard supports, not the widget count. Put the most important metric and trend first; use consistent scales, units, and ranges; show comparisons and context. Filters and time ranges persist in the URL. Design empty, loading, partial, and error states for every widget. Prefer tables for precise values and charts for patterns; make numbers tabular and aligned. Do not use pie charts for many categories or 3D charts. Label synthetic data.

### Data display

Choose the chart from the question, not from the chart library:

| Question | Better default |
|---|---|
| How did a value change over time? | Line or area chart |
| How do categories compare? | Horizontal bar chart |
| What is the distribution? | Histogram, dot plot, or box plot |
| What is the composition? | Stacked bar; pie only for 2–5 clear parts |
| Is there a relationship? | Scatter plot |
| Where is it? | Map with a clear scale and accessible fallback |
| What is the exact value? | Table or a labeled number, not a chart |

Rules:

- Label axes, units, and time ranges. Start bar charts at zero.
- Use direct labels; avoid legends that require color matching. Use one accent for the focus series and mute the rest.
- Do not rely on color alone; use patterns, labels, or annotation, and test a colorblind-safe palette in grayscale.
- Use tabular figures and consistent precision. Show comparisons (previous period, target, benchmark) where they change the decision.
- Design empty, loading, partial, and error states for every chart.
- Provide a data table or text summary for screen readers and exact values.
- Do not use 3D charts or decorative gradients that distort perception; do not animate bars racing from zero on every load.
- Label synthetic or sample data and state the source and freshness when trust matters.

### List and detail

List prioritizes scanning and shows the fields that distinguish items. Detail answers what this is, what I can do, and what happens next. Use one clear primary action. Preserve filters, scroll, and selection on return. Support bulk actions with clear selection and undo. Design "no items" and "no results" differently.

### Settings

Group by mental model, show current values, and make save behavior explicit (autosave or save). Confirm destructive changes and provide reset or recovery. Distinguish read-only from disabled. Do not hide critical settings behind search only.

### Pricing

Show the unit, billing period, inclusions, and taxes or fees. Make the recommended plan clear without dark patterns. Show plan differences, not just feature lists. Offer a human path for complex plans. Do not use fake countdowns or false scarcity.

### Empty and first-run screens

Explain what would be here and why it is empty. Give one primary action to populate it and offer a sample or template when useful. Do not use a sad face as the whole experience or hide the way back.

## Forms

Forms are where users lose patience. Design the whole conversation, not just the fields.

### Field anatomy

```text
Label (visible, associated)
Optional help text (persistent)
[ input ]
Error text (specific, adjacent, linked)
```

- Label above the input for most forms; beside for compact, simple settings.
- Mark required fields; do not mark every field with an asterisk if all are required.
- Use placeholder for an example, not as a label.
- Use helper text for format, constraints, or why the information is needed.
- Keep error text next to the field; do not rely on a toast.
- Use `aria-describedby` to connect help and error text.
- Use `aria-invalid="true"` on invalid fields.
- Preserve values after an error.

### Validation

- Validate on blur for most fields, not on every keystroke.
- Validate on submit for the whole form.
- Error lifecycle invariants: never display an error before the user has interacted or submitted, and clear the error immediately once the underlying cause is fixed.
- Do not clear the form on error.
- Do not disable submit silently; if disabled, explain what is missing.
- For multiple errors, provide a focusable summary at the top and inline messages; move focus to the summary or first invalid field after submit.
- Use specific messages: "Enter a date after today" not "Invalid date".
- Success should be as clear as failure.

### Input types and autofill

```html
<label for="email">Email</label>
<input id="email" name="email" type="email" autocomplete="email" inputmode="email" />

<label for="phone">Phone</label>
<input id="phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" />

<label for="password">Password</label>
<input id="password" name="password" type="password" autocomplete="current-password" />
```

Use `enterkeyhint` on mobile (`next`, `done`, `search`, `send`). Use `inputmode` for numeric or decimal keyboards. Do not block paste.

### Grouping and multi-step forms

- Group related fields with `fieldset`/`legend` or a clear heading.
- Use progressive disclosure for advanced options.
- Show progress for multi-step flows: "Step 2 of 4" plus a label.
- Allow back navigation without losing data.
- Save drafts for long forms; tell the user when saved.
- Confirm before leaving with unsaved changes.
- Do not ask for the same information twice (WCAG 3.3.7).

### Destructive actions

- Confirm irreversible actions with the object, consequence, and explicit action/cancel button verbs (for example `Delete report` / `Keep report`, never generic `Are you sure?` / `OK`).
- Use safe synthetic contact and identity placeholders in examples and mockups (`.example` domains, non-real phone/VAT/street numbers).
- Offer undo for reversible actions.
- Separate destructive actions from primary actions.
- Do not use a confirm dialog for every click; it trains people to dismiss them.
- For bulk destructive actions, show the count and scope.

### Form checklist

Every field has a visible label and clear required/optional status; help text persists; errors are specific, inline, linked, and summarized focusably; values persist after failure; autofill works; input types trigger the right mobile keyboard; submit has loading, success, and error states; double submission is prevented without losing input; the form works keyboard-only at 200% zoom.

## Feedback and states

Every asynchronous or data-driven surface needs a state plan.

| State | What the user needs | Pattern |
|---|---|---|
| Idle | Clarity about what to do | Clear primary action |
| Loading | Confidence that something is happening | Skeleton, progress, or busy label |
| Partial | What is available now | Show partial data with a clear note |
| Empty | Why it is empty and what to do | Explanation + action |
| No results | How to broaden the search | Clear filters, suggest alternatives |
| Error | What happened, why, how to recover | Inline message + retry |
| Offline | What still works | Cached data + reconnect guidance |
| Success | What changed and what's next | Confirmation + next step or undo |
| Disabled | Why it is unavailable | Reduced emphasis + explanation |

### Loading thresholds

- Under ~100 ms: no indicator; it would flash.
- ~100 ms–1 s: subtle inline feedback, such as a button busy state.
- Over ~1 s: skeleton or progress indicator.
- Over ~10 s: background task with a way to leave and return.
- Preserve layout; do not replace the whole page with a spinner for a local update.
- Announce busy state with `aria-busy` or a status message where appropriate.

### Skeletons

- Match the final layout's dimensions.
- Do not animate aggressively; a subtle pulse is enough.
- Do not use a skeleton for an action that takes 200 ms.
- Provide a text alternative or status for screen readers.
- Avoid endless skeletons; show an error after a reasonable timeout.

### Optimistic updates

- Update the UI immediately for low-risk actions.
- Provide a rollback and a clear error if the server fails.
- Do not use optimistic UI for payments, irreversible actions, or anything with legal consequences unless the product is designed for it.
- Keep the pending state visible enough that the user knows the change is not confirmed.

### Toasts and notifications

- Use toasts for transient confirmation, not for critical errors.
- Do not steal focus.
- Use `aria-live="polite"` or `role="status"`.
- Auto-dismiss simple messages in 3–5 seconds; pause on hover/focus.
- Provide a dismiss control.
- Do not stack more than a few toasts; group or queue them.
- For errors, use inline messages first; a toast can supplement, not replace.

## Content design and microcopy

### Voice and tone

Choose three voice attributes. Keep the voice stable; let tone shift with context.

| Context | Tone |
|---|---|
| Success | Brief, specific, not smug |
| Error | Calm, factual, helpful |
| Empty | Inviting, not cute |
| Destructive | Serious, clear, not dramatic |
| Onboarding | Encouraging, not patronizing |
| Legal/security | Precise, plain, not alarmist |

### Microcopy rules

- Use plain language and concrete verbs.
- Prefer sentence case.
- Use "you" and "we" only if the brand voice supports it.
- Keep one name for one thing.
- Put the important information first.
- Remove filler: "Please note that", "In order to", "Simply", "Just".
- Avoid jargon unless the audience uses it.
- Avoid exclamation marks in errors and confirmations.
- Do not use humor to soften a serious failure.
- Do not blame the user.

### Buttons and links

- Button labels describe the action: "Save changes", "Reserve drill", "Send invite".
- Link text describes the destination: "See pickup hours", not "Click here".
- Keep the same action name through the flow.
- Use destructive verbs explicitly: "Delete project", not "Remove".
- Do not use "OK" as the only label in a consequential dialog.

### Errors

```text
What happened: We couldn't save your changes.
Why: The connection dropped before the server confirmed the update.
What now: Try again. Your text is still here.
[Try again]
```

- Be specific.
- Put the error where the action happened.
- Preserve the user's work.
- Provide a recovery path.
- Use an error code only as secondary information.
- Do not expose stack traces or internal identifiers.

### Empty states

```text
No reservations yet.
When you reserve a tool, it will appear here with pickup details.
[Browse tools]
```

- Explain what would be here.
- Explain why it is empty.
- Give one action.
- Keep it brief.
- Do not use a decorative illustration as the only content.

### Confirmation

- Confirm what changed: "Reservation confirmed for Saturday, 9–12."
- Include the next step: "Pick up at 14 Oak St. Bring your member card."
- Offer undo for reversible actions.
- Do not use "Success!" alone.

## Research-lite

This skill does not replace a dedicated research practice. But design decisions should be labeled as evidence, assumption, or hypothesis.

### Evidence levels

| Level | What it is | How to use |
|---|---|---|
| Evidence | Observed behavior, analytics, interviews, tests | Can justify a decision |
| Assumption | A belief about users or context | State it; test it cheaply |
| Hypothesis | A proposed cause-effect | Design an experiment |

If you have no research, say so. Do not invent personas or statistics.

### Cheap validation

- **Five-user usability test**: find the top 3–5 problems in a flow.
- **Task-based test**: give a realistic scenario, not instructions.
- **First-click test**: can users find the right starting point?
- **Hallway test**: ask a colleague to complete one task while thinking aloud.
- **Analytics review**: funnel drop-off, rage clicks, search terms, support tickets.
- **Content review**: read the copy aloud; if it sounds like a brochure, rewrite it.

### Usability test basics

- 5–8 participants per round is enough for directional findings.
- Write tasks as scenarios with a goal, not steps.
- Ask participants to think aloud.
- Do not lead with "Would you like...?"; observe behavior.
- Record completion, time, errors, and confidence.
- Rate severity with P0/P1/P2 from `quality-gates.md`.
- Report evidence and recommendation, not just opinions.

### Journey map

For a key flow, map:

```text
Stage -> Action -> Touchpoint -> Thought/feeling -> Pain -> Opportunity
```

Use real data where possible. Prioritize opportunities by frequency × severity × solvability, and state the assumptions behind the scores.

### Personas

Create personas only when they are grounded in data. A useful persona includes:

- context and goal;
- current behavior and workarounds;
- pain points with frequency;
- decision criteria;
- what the product should do differently.

Avoid demographic decoration that does not change design decisions.

## Internationalization and RTL

- Allow at least 30% text expansion for translated strings.
- Do not bake text into images.
- Use locale-aware number, date, currency, and address formats.
- Avoid idioms, puns, and culture-specific references in critical UI.
- Support RTL with logical CSS properties: `margin-inline`, `padding-inline`, `inset-inline`, `border-inline`.
- Mirror directional icons (arrows, chevrons) but not universal symbols (play, check, logos).
- Test layouts with long German compounds and short CJK strings.
- Use `lang` and `dir` attributes correctly.
- Do not use flags for languages.

## Trust, privacy, and dark patterns

### Trust

- Show who is behind the product: contact, address, policies.
- Explain what happens with user data before asking for it.
- Use clear pricing and cancellation terms.
- Show security-relevant states honestly.
- Label AI-generated content and synthetic media.
- Do not fabricate testimonials, ratings, or activity.

### Dark patterns to avoid

- fake urgency or countdowns;
- confirmshaming;
- pre-checked consent;
- hidden fees;
- difficult cancellation;
- roach motel (easy sign-up, hard delete);
- disguised ads;
- false scarcity;
- nagging;
- confusing toggle logic;
- "accept all" as the only prominent cookie choice.

### Consent

- Make reject as easy as accept.
- Explain categories in plain language.
- Do not block content behind a wall when consent is not required.
- Remember the choice.
- Provide a way to change it later.

## Heuristic review

Use Nielsen's ten heuristics as a quick lens, not a checklist to recite:

1. Visibility of system status.
2. Match between system and the real world.
3. User control and freedom.
4. Consistency and standards.
5. Error prevention.
6. Recognition rather than recall.
7. Flexibility and efficiency of use.
8. Aesthetic and minimalist design.
9. Help users recognize, diagnose, and recover from errors.
10. Help and documentation.

For each finding, state:

- the heuristic;
- the screen and element;
- the user impact;
- the evidence;
- the fix;
- the severity from `quality-gates.md`.

## UX checklist

- [ ] The primary job is stated in one sentence.
- [ ] The flow has entry, decision, failure, recovery, success, and exit states.
- [ ] Navigation is consistent and the current location is clear.
- [ ] Every form field has a visible label and a clear error path.
- [ ] Loading, empty, error, success, and offline states are designed.
- [ ] Destructive actions are confirmed and reversible where possible.
- [ ] Content is specific, plain, and consistent through the flow.
- [ ] The interface works with keyboard, screen reader, zoom, and reduced motion.
- [ ] The layout survives long content, translation, and 320 px width.
- [ ] No dark pattern or fabricated proof is present.
