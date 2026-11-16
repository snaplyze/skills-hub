---
name: Specification
description: Use before non-trivial feature work, redesigns, or ambiguous requests to turn the request into a short, testable specification. Covers users, outcomes, non-goals, constraints, acceptance criteria, assumptions, and open questions. Not for tiny, obvious fixes where the requirement is already concrete.
license: MIT
compatibility: opencode
---

# Specification

## What this is

A specification is a small agreement about the problem, not a design document and not code. It exists so implementation decisions can be made against a shared target instead of guesswork.

## When to use it

Use it when the request is multi-step, affects other people, changes existing behavior, or leaves a material decision open. For a one-line fix with an obvious expected result, state the intent and proceed.

## Workflow

1. **Read before asking.** Inspect the relevant code, docs, tests, and project conventions. Do not ask questions the repository already answers.
2. **Ask only decision-changing questions.** Batch the smallest set of questions whose answers change scope, behavior, data, compatibility, or acceptance. If an answer is unavailable, state an assumption and its consequence.
3. **Write the spec in seven parts:** problem, users and job, observable outcome, non-goals, constraints, acceptance checks, and review focus. Add risks, assumptions, and open questions only when they are real.
4. **Make acceptance observable.** Each check should name a command, behavior, screen, API response, or measurable result. Avoid "works well", "clean", and "fast" without a target.
5. **Size and options.** If the work is large, split it into outcomes instead of one giant spec. If the solution space is open, list two or three viable approaches with tradeoffs and a recommendation; do not pretend the first idea is the only option. Keep a short design note in the spec when the choice is material; do not create a hidden design file.
6. **Name the review focus.** List the failure modes or inputs the acceptance does not explicitly cover: empty/large data, retries, permissions, compatibility, migration, and the most likely misuse. Each item should get a test in the plan.
7. **Play it back.** Give a five-line summary: problem, outcome, non-goals, main constraint, and acceptance. Ask for confirmation when a wrong decision would be expensive. For small work, a one-line intent is enough.
8. **Persist it for multi-step work.** Save to `docs/specs/YYYY-MM-DD-<slug>.md` or the project's existing spec location. Do not create a spec file for a trivial change.
9. **Hand off.** Use the `implementation-planning` skill when the spec is accepted. Use `systematic-debugging` instead when the task is a defect with unknown cause.

## Spec template

```text
# <feature>
Problem:      the concrete pain or opportunity
Users / job:  who needs what, in what situation
Outcome:      the observable change
Non-goals:    what this deliberately does not change
Constraints:  compatibility, data, security, performance, design, time
Approaches:   2–3 viable options, tradeoffs, recommendation (when material)
Acceptance:   checkable conditions, including failure and edge behavior
Review focus: failure modes/inputs not covered explicitly by acceptance
Assumptions:  inferred facts and what happens if they are wrong
Open questions: only questions that still change the design
```

## Hard rules

- Do not invent requirements, users, metrics, or constraints. Mark assumptions as assumptions.
- Do not jump to architecture or code before the problem and outcome are clear.
- Preserve existing behavior unless the spec explicitly changes it.
- Keep one outcome per spec; split unrelated outcomes instead of hiding them in one request.
- Do not turn the spec into a task list. Sequencing belongs in `implementation-planning`.
- Do not start planning a material approach choice until the recommendation is accepted or explicitly assumed.

## Red flags

- The acceptance section contains no observable check.
- A question can be answered by reading the repository.
- The spec lists a solution but not the problem.
- Non-goals are empty on a change that can affect existing users.
- The request is large but the spec has one vague sentence.

## Output

A short spec, assumptions made explicit, and a clear handoff to planning or debugging.
