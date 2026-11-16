---
name: Implementation Planning
description: Use after a specification or a clear multi-step request to produce an execution plan with small tasks, exact files and interfaces, tests, dependencies, risks, and verification. Use before coding when another engineer or subagent must execute without guessing. Not for a trivial one-step edit.
license: MIT
compatibility: opencode
---

# Implementation Planning

## What this is

A plan turns an accepted outcome into an ordered set of decisions. It is written for an engineer who has the codebase but not this conversation: they should know what to change, where, why, and how to prove it.

## Plan header

Every plan starts with the decisions an executor cannot recover from the code:

```text
# <feature> implementation plan
Goal: <one observable outcome>
Architecture: <2–3 sentences about the chosen shape and why>
Tech stack: <existing language/framework/tools; no new dependency unless justified>
Spec: <path to the accepted spec or one-line source>
Global constraints: <version floors, compatibility, data/security limits, naming, platform>
Review focus: <the failure modes or inputs most likely to bite; one line each>
```

Keep the header short. It is the contract that later tasks inherit; do not repeat it in every task.

## Workflow

1. **Check the input.** If the outcome, acceptance, or constraints are unclear, go back to `specification` instead of hiding uncertainty in tasks.
2. **Inspect the real seams.** Read the files, tests, build commands, and conventions that the change touches. Find existing patterns before inventing a new layer.
3. **Map the files before the tasks.** List the files or modules to create/modify and their one responsibility. Prefer focused files and existing seams; split by responsibility, not by technical layer. This is where decomposition is locked in.
4. **Choose the smallest coherent shape.** Remove duplicate work and unnecessary abstractions first. Prefer an existing seam over a new framework. State any schema, API, or compatibility decision. Prefer vertical slices that leave a working, testable path over horizontal layers that only integrate at the end.
5. **Write tasks in execution order.** Each task is the smallest unit with its own test cycle and review gate, usually 5–30 minutes. Fold setup, configuration, and documentation into the task whose deliverable needs them. Split only where a reviewer could accept one task and reject its neighbor. Put high-risk tasks early. Add a checkpoint after every 2–3 tasks.
6. **Specify each task concretely:** files (create/modify/test), public interface or signature, expected behavior, test(s), command, dependencies, and commit boundary. Use `Consumes`/`Produces` for interfaces shared with another task. Include the exact values from the spec; do not leave naming or error semantics to the implementer unless either choice is safe.
7. **Plan verification.** Name the narrow test for each task and the full check for the end. Each executable step has a command and an `Expected` result. Include a baseline check before edits and a rollback or containment path for risky changes.
8. **Self-review the plan.** Check spec coverage, step scan (does each step decide one thing?), type consistency across tasks, review focus coverage, and proportion (is the plan a transcript of the code?). Could a fresh engineer execute it without this session? Are tasks independent where claimed? Present the plan for approval when the work is large or irreversible; do not start execution on an unapproved scope.
9. **Save and hand off.** Save to `docs/plans/YYYY-MM-DD-<slug>.md` or the project's plan location. Do not create a tool-owned plan directory; use `docs/plans/`. If an unfinished plan for the same work exists, read and extend it; do not overwrite it. Hand off to `autonomous-execution`.

## Plan template

````text
# <feature> implementation plan
Goal: <one observable outcome>
Architecture: <chosen shape and why>
Tech stack: <existing tools>
Spec: <link or one-line outcome>
Global constraints: <one line each>
Review focus: <failure modes/inputs to test>
Approval: <who accepted the outcome, or "assumed for small work">

## Baseline
Current behavior, commands, and known constraints:

## File map
- Create/Modify: <path> — <one responsibility>
- Test: <path> — <what it proves>

## Tasks
### T1 — <verb + result>
Files:
- Create/Modify/Test: <exact paths>
Interfaces:
- Consumes: <earlier task signatures/data>
- Produces: <names/signatures later tasks use>
- [ ] Step 1: Write the failing test
```text
<test name and exact assertions>
```
- [ ] Step 2: Run it
Run: `<focused command>`
Expected: FAIL for the right reason
- [ ] Step 3: Implement the minimal change
...
- [ ] Step 4: Run the test
Run: `<focused command>`
Expected: PASS
- [ ] Step 5: Commit
Run: `git add <paths> && git commit -m "<message>"`

### T2 — ...
Depends on: T1
Commit: <boundary>

## Checkpoint after T1–T2
- [ ] Focused tests pass
- [ ] Full build/check passes
- [ ] No unintended files changed

## Risks and rollback
...

## Final acceptance
- [ ] <mapped to spec checks>
- [ ] Full required suite
- [ ] Documentation/changelog/tracker updates
````

## Task quality rules

- One task = one reviewable behavior or seam, not "write the backend".
- Tests come before implementation in the task description.
- Exact file paths and public names are included; internal choices may stay open only when they cannot break the contract.
- Dependencies are explicit; independent tasks are marked parallel-safe.
- No task requires the executor to invent product behavior.
- No task includes unrelated cleanup, formatting, or refactoring.
- Each task ends with an independently testable deliverable; a checkpoint follows every 2–3 tasks.
- Interfaces shared across tasks are named in both the producer and consumer tasks.
- The plan is not a code transcript: signatures and test assertions, not implementation bodies, unless exact copy is required.

## Red flags

- A task says "implement the feature" without a test or boundary.
- The plan is a prose design document with no executable order.
- Tasks depend on files that another task creates but the dependency is unstated.
- The plan assumes a framework, service, or dependency without checking the repository.
- The plan has no full-suite or end-to-end verification.
- The plan is only a list of file edits with no behavioral outcome.

## Output

A task-ordered plan with concrete seams, tests, dependencies, risks, and a final acceptance map.
