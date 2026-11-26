---
name: Systematic Debugging
description: Use when a bug, test failure, crash, regression, or unexpected behavior needs a root-cause fix. Requires reproducing the failure, isolating the cause, testing a falsifiable hypothesis, and adding a regression test before the fix. Not for feature work or for guessing at symptoms without evidence.
license: MIT
compatibility: opencode
---

# Systematic Debugging

## The rule

Do not fix a symptom you cannot explain. The first useful output is a reproducible failure and a likely cause, not a patch.

## Phase 1 — Reproduce

- Capture the exact command, input, environment, version, and observed output.
- Make the reproduction as small and deterministic as possible. Remove unrelated steps one at a time.
- Find the first bad state, not the last error message.
- If the failure is intermittent, measure the conditions and rate; do not call it random.
- This workflow also applies to pasted stack traces, diffs, or snippets without a local checkout: isolate what the snippet proves and explicitly list the missing runtime/environment evidence.

## Phase 2 — Localize

- Read the failing path and its tests before changing it.
- Trace backward through callers from the failure site to the earliest point where invalid state originated (**root-cause tracing**).
- Compare a working case with the failing case: input, configuration, data, ordering, and version.
- Use logs, assertions, a debugger, tracing, or `git bisect` to narrow the boundary. Add temporary instrumentation only where it answers a question; remove it afterward.
- Check recent changes and the assumptions at every boundary: caller, parser, storage, network, clock, locale, permissions.

## Phase 3 — Hypothesize and test

State one falsifiable sentence: "If X causes the failure, then Y should change Z." Predict the result before running the test. If the prediction fails, discard the hypothesis and gather new evidence. Do not accumulate speculative fixes.

## Phase 4 — Fix and prove

1. Write a regression test that fails for the reproduced cause. For flaky async tests, use **condition-based waiting** (predicate polling with a bounded timeout) instead of fixed sleeps; reserve fixed delays only when testing explicit timing behavior such as debounce.
2. Apply the smallest fix at the cause, not at every downstream symptom. For invalid-data bugs, pair the root fix with **defense-in-depth** validation at entry, domain, and environment boundaries where appropriate.
3. Run the regression test, the affected tests, and the full required suite.
4. Remove temporary instrumentation and confirm the diff contains only the fix and its test.
5. Explain why the fix prevents recurrence.

## If no root cause is found

Do not guess. Keep the reproduction, add the smallest safe diagnostic that will distinguish hypotheses, and report what is still unknown. A documented investigation with a next experiment is better than a random patch.

## Red flags

- Editing several unrelated places to see what sticks.
- Disabling, skipping, or loosening a test.
- A sleep, retry, catch-all, or timeout added without understanding the race or failure.
- "It works on my machine" without environment evidence.
- A fix with no failing test or no before/after output.
- Treating a symptom (null, 500, flicker) as the cause.

## Handoff

Use `test-driven-development` for the regression test and `clean-code` for the final shape. Hand off to `code-review` with the reproduction, root cause, fix, and evidence.
