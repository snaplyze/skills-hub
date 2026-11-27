---
name: code-review
description: Use before merging or after completing a task to request a fresh-context review and to evaluate review feedback rigorously. Covers correctness, edge cases, security, tests, compatibility, performance, and scope, with P0/P1/P2 findings and evidence. Not for UI/visual design audits (use frontend-design), performative agreement, or reviewing your own work as an independent approval.
license: MIT
compatibility: agentskills
---

# Code Review

## Two modes

**Requesting:** give a fresh reviewer the spec, the exact diff, the test evidence, the risks, and the questions that matter. The reviewer reads; it does not edit or take over the branch.

**Receiving:** verify every point against the code and a command before implementing it. Separate technical correctness from tone. Accept with evidence, or push back with evidence. Do not agree just to be agreeable.

## Request brief

```text
Goal:
Spec / acceptance:
Base and head:
Files and intentional scope:
Tests run and outputs:
Known risks / not tested:
Specific questions:
```

If the harness has subagents, dispatch a fresh read-only reviewer (new child subagent via `invoke_subagent` using `define_subagent` with `EnableWriteTools: false`, `research`, or a dedicated read-only reviewer agent) with this brief, the exact diff range, and explicit changed file paths (or diff excerpt when the reviewer has no shell tools); do not let it edit or take over the branch. If no separate reviewer is available, do a structured self-review using the same checklist and state that it is not independent. After fixes, send the fix delta (or the new diff) for a scoped re-review (continuing the reviewer via `send_message` or starting a fresh reviewer) before merge. Where available, users can also inspect diffs inline with the Review pane or `/diff`.

## Review order

1. **Tests first.** Read the test diff before the implementation: names, assertions, edge cases, and whether the tests would fail on the old behavior.
2. **Then the implementation.** Walk the five axes below with the spec and diff in front of you.
3. **Then the evidence.** When shell tools are available, verify the tree is clean (`git status --short` empty) and `HEAD` matches the reviewed commit before running probes or tests, citing that SHA in the review, and re-run the narrow test and affected suite instead of trusting a pasted result. When running in a no-shell read-only reviewer (`EnableWriteTools: false`), inspect the changed files and test assertions statically, mark command execution as `NOT_TESTED`, and have the parent (or a separate isolated test runner) execute clean-tree and test verification.
4. **Then scope.** Check for unrelated refactors, generated files, secrets, and behavior changes not in the spec.

## Five axes

- **Correctness:** matches acceptance, failure/empty paths, boundaries, concurrency, retries, state.
- **Readability:** domain names, one level of abstraction, explicit side effects, comments for why.
- **Architecture:** boundaries, dependency direction, duplication of knowledge, fit with existing seams.
- **Security:** input validation, authorization, secrets, injection, path traversal, unsafe data.
- **Performance:** N+1, unbounded work, repeated I/O, memory, missing limits, hot paths.

## Review checklist

Use these as detailed prompts under the five axes; they are not a second verdict.

- **Correctness:** the change does what the spec says, including failure and empty paths.
- **Edge cases:** null/empty, long input, concurrency, retries, partial failure, permissions, time zones, locale, and version boundaries.
- **Security and trust:** input validation, authorization, secret handling, injection, path traversal, unsafe deserialization, dependency/supply-chain changes.
- **Data:** schema, migration, compatibility, idempotency, rollback, and loss.
- **Tests:** behavior-level coverage, deterministic assertions, regression test for a bug, no weakened or skipped checks.
- **Compatibility:** public API, CLI, config, storage, and platform behavior.
- **Performance:** obvious N+1, unbounded memory, repeated I/O, blocking work, or missing limits.
- **Maintainability:** names, boundaries, duplication, dead code, and fit with repository conventions.
- **Scope:** no unrelated refactors, generated files, secrets, or accidental behavior changes.
- **Docs:** commands, links, and claims match the change.

## Mutation check

For a changed condition, invert or remove it in a scratch copy and run the test that should protect it. If the test stays green, the test does not prove the behavior: report the missing case. Restore the file immediately. Do not run mutation experiments on the working tree without a restore path. When running in a no-shell read-only reviewer (`EnableWriteTools: false`), perform mental/static mutation analysis against the test assertions and flag suspected gaps for the parent to verify in a scratch run.

## Findings

Use P0/P1/P2 and mark optional feedback separately:

- **P0 — blocker:** security, data loss, unusable behavior, or a broken contract. Do not ship.
- **P1 — major:** likely user-visible defect, missing critical test, or material maintainability risk. Fix before merge.
- **P2 — minor:** polish, clarity, or a small edge case. Fix when reasonable. Mark optional suggestions as `optional:` rather than P2.
- **Nit:** formatting or preference with no functional impact; never block on it.

Calibrate by impact and likelihood: external security/data loss is P0/P1; missing tests for a critical path is at least P2; style is a nit. Verify every candidate finding against callers, guards, and tests before reporting, and drop claims ruled out by the codebase. Separate pre-existing base defects from regressions introduced by the diff. Zero findings is a valid result — never pad the list with generic advice. Every finding needs `path:line`, evidence, impact, and a concrete fix. Mark uncertainty as a question, not a finding.

## Structural remedies

When a finding is structural, propose the move: replace a conditional chain with a typed model or dispatcher; collapse duplicate branches; separate orchestration from business logic; move feature logic out of a shared module; reuse the canonical helper; make a type boundary explicit; delete a pass-through wrapper; extract a focused helper. Prefer deleting a layer to polishing it.

## Change size

- around 100 changed lines: easy to review;
- around 300: acceptable for one logical change;
- around 1000: split it.

Separate refactoring from behavior changes. A large mechanical rename or file deletion may be one change; a feature plus a refactor is two.

## Receiving feedback

1. Restate the claim and find the relevant code.
2. If any item is unclear, stop and ask for the missing context before implementing any of it.
3. Reproduce the problem or inspect the test that proves it.
4. Classify: blocking defect, valid improvement, question, YAGNI/scope concern, or incorrect assumption. Grade by real user impact — do not dismiss a real user-facing bug just because a reviewer labeled it Minor where the spec was silent.
5. Implement valid blocking changes; reply to questions; explain a reasoned rejection. Treat feedback from a human, an external reviewer, and a bot by the same technical standard, not by authority.
6. Rerun the affected checks, reply in the review thread with evidence, and request a re-review of the delta.
7. Do not silently dismiss feedback, and do not rewrite unrelated code to satisfy a local comment.

## Red flags

- "LGTM" without reading the diff.
- Approving your own PR as independent review.
- Implementing every suggestion without verification.
- Defending code instead of testing the claim.
- A review that lists style preferences but misses failure paths.
- Findings without a location or reproduction.

## Handoff

After feedback is resolved and checks are green, hand off to `delivery`.
