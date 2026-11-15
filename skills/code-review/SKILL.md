---
name: Code Review
description: Use before merging or after completing a task to request a fresh-context review and to evaluate review feedback rigorously. Covers correctness, edge cases, security, tests, compatibility, performance, and scope, with P0/P1/P2 findings and evidence. Not for performative agreement or for reviewing your own work as an independent approval.
license: MIT
compatibility: opencode
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

If the harness has subagents, dispatch a read-only reviewer with this brief and the exact diff range; do not let it edit or take over the branch. If no separate reviewer is available, do a structured self-review using the same checklist and state that it is not independent. After fixes, send the delta (or the new diff) for a re-review before merge.

## Review checklist

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

## Findings

Use P0/P1/P2:

- **P0 — blocker:** security, data loss, unusable behavior, or a broken contract. Do not ship.
- **P1 — major:** likely user-visible defect, missing critical test, or material maintainability risk. Fix before merge.
- **P2 — minor:** polish, clarity, or a small edge case. Fix when reasonable.

Every finding needs `path:line`, evidence, impact, and a concrete fix. Do not pad the list with generic advice. Mark uncertainty as a question, not a finding.

## Receiving feedback

1. Restate the claim and find the relevant code.
2. If any item is unclear, stop and ask for the missing context before implementing any of it.
3. Reproduce the problem or inspect the test that proves it.
4. Classify: blocking defect, valid improvement, question, YAGNI/scope concern, or incorrect assumption.
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
