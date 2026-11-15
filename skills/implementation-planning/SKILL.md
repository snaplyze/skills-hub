---
name: Implementation Planning
description: Use after a specification or a clear multi-step request to produce an execution plan with small tasks, exact files and interfaces, tests, dependencies, risks, and verification. Use before coding when another engineer or subagent must execute without guessing. Not for a trivial one-step edit.
license: MIT
compatibility: opencode
---

# Implementation Planning

## What this is

A plan turns an accepted outcome into an ordered set of decisions. It is written for an engineer who has the codebase but not this conversation: they should know what to change, where, why, and how to prove it.

## Workflow

1. **Check the input.** If the outcome, acceptance, or constraints are unclear, go back to `specification` instead of hiding uncertainty in tasks.
2. **Inspect the real seams.** Read the files, tests, build commands, and conventions that the change touches. Find existing patterns before inventing a new layer.
3. **Choose the smallest coherent shape.** Remove duplicate work and unnecessary abstractions first. Prefer an existing seam over a new framework. State any schema, API, or compatibility decision.
4. **Write tasks in execution order.** Each task should take roughly 5–30 minutes, change one logical thing, and leave the tree in a verifiable state. Split setup, behavior, integration, and cleanup only when each is independently useful. Split a large plan into sub-plans with a shared acceptance map rather than one unreadable document.
5. **Specify each task concretely:** files, public interface or signature, expected behavior, test(s), command, dependencies, and commit boundary. Include the exact values from the spec; do not leave naming or error semantics to the implementer unless either choice is safe.
6. **Plan verification.** Name the narrow test for each task and the full check for the end. Include a baseline check before edits and a rollback or containment path for risky changes.
7. **Self-review the plan.** Could a fresh engineer execute it without this session? Are tasks independent where claimed? Is any task a hidden design decision? Are YAGNI and DRY respected? Does every acceptance check map to a task? Mark the review focus: correctness, tests, compatibility, security, performance, or maintainability. Present the plan for approval when the work is large or irreversible; do not start execution on an unapproved scope.
8. **Save and hand off.** Save to `docs/plans/YYYY-MM-DD-<slug>.md` or the project's plan location. Hand off to `autonomous-execution`.

## Plan template

```text
# <feature> implementation plan
Spec: <link or one-line outcome>
Approval: <who accepted the outcome, or "assumed for small work">

## Baseline
Current behavior, commands, and known constraints:

## Tasks
### T1 — <verb + result>
Files:
Interfaces: consumes -> produces (names, signatures, schemas)
Change:
Test:
Run:
Expected:
Verify:
Depends on:
Commit:

### T2 — ...

## Risks and rollback
...

## Final acceptance
- <mapped to spec checks>
```

## Task quality rules

- One task = one reviewable behavior or seam, not "write the backend".
- Tests come before implementation in the task description.
- Exact file paths and public names are included; internal choices may stay open only when they cannot break the contract.
- Dependencies are explicit; independent tasks are marked parallel-safe.
- No task requires the executor to invent product behavior.
- No task includes unrelated cleanup, formatting, or refactoring.

## Red flags

- A task says "implement the feature" without a test or boundary.
- The plan is a prose design document with no executable order.
- Tasks depend on files that another task creates but the dependency is unstated.
- The plan assumes a framework, service, or dependency without checking the repository.
- The plan has no full-suite or end-to-end verification.
- The plan is only a list of file edits with no behavioral outcome.

## Output

A task-ordered plan with concrete seams, tests, dependencies, risks, and a final acceptance map.
