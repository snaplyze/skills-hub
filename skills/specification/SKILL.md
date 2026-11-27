---
name: specification
description: Use before non-trivial feature work, redesigns, or ambiguous requests to turn the request into a short, testable specification. Covers users, outcomes, non-goals, constraints, acceptance criteria, assumptions, and open questions. Not for tiny, obvious fixes where the requirement is already concrete.
license: MIT
compatibility: agentskills
---

# Specification

## What this is

A specification is a small agreement about the problem, not a design document and not code. It exists so implementation decisions can be made against a shared target instead of guesswork.

## When to use it

Use it when the request is multi-step, affects other people, changes existing behavior, or leaves a material decision open. For a one-line fix with an obvious expected result, state the intent and proceed.

## Workflow

1. **Read before asking.** Inspect the relevant code, docs, tests, and project conventions. Do not ask questions the repository already answers.
2. **Ask only decision-changing questions.** Ask open "why" questions first when intent is unclear; once options are concrete, present named tradeoffs plus a recommendation. State non-material defaults as proposals to correct, and never ask permission for routine process steps (reading files or choosing standard paths). Batch remaining user-only questions; if an answer is unavailable, state an assumption and its consequence.
3. **Write the spec cleanly:** problem, users and job, observable outcome, non-goals and anti-goals (what would make it a failure even if it technically works), constraints, approaches (when material), acceptance checks, review focus, risks, assumptions, deferred (`V2+`) items, and open questions (include only sections that carry real signal).
4. **Make acceptance observable.** Each check should name a command, behavior, screen, API response, or measurable result. Avoid "works well", "clean", and "fast" without a target.
5. **Size and options.** If the work is large, split it into outcomes instead of one giant spec. If the solution space is open, list two or three viable approaches with tradeoffs and a recommendation; do not pretend the first idea is the only option. Keep a short design note in the spec when the choice is material; do not create a hidden design file.
6. **Name the review focus.** List the failure modes or inputs the acceptance does not explicitly cover: empty/large data, retries, permissions, compatibility, migration, and the most likely misuse. Each item should get a test in the plan.
7. **Builder check and playback.** For large or multi-step specs, run a fresh read-only builder check (subagent or self-pass) reporting only ambiguities where a wrong guess would change the plan, and fold them into one consolidated round. Then play back a five-line summary (problem, outcome, non-goals, main constraint, acceptance) and confirm before expensive decisions.
8. **Persist it for multi-step work.** Save to `docs/specs/YYYY-MM-DD-<slug>.md` or the project's existing spec location. Do not create a spec file for a trivial change. If the active agent cannot edit project files (for example in read-only or plan mode), present the complete spec with target path `docs/specs/YYYY-MM-DD-<slug>.md`, do not bypass edit restrictions via shell writes, and hand off to a writable agent to save it. For post-ship changes to an existing spec, write a focused delta spec (`docs/specs/YYYY-MM-DD-<slug>-delta.md`) covering current behavior, new behavior, unchanged invariants, and boundary deltas instead of rewriting the shipped spec.
9. **Hand off.** Use the `implementation-planning` skill when the spec is accepted. Use `systematic-debugging` instead when the task is a defect with unknown cause.

## Spec template

```text
# <feature>
Problem:      the concrete pain or opportunity
Users / job:  who needs what, in what situation
Outcome:      the observable change
Non-goals:    what this deliberately does not change (plus anti-goals)
Deferred:     out-of-scope V2+ backlog items (optional)
Constraints:  compatibility, data, security, performance, design, time
Approaches:   2–3 viable options, tradeoffs, recommendation (when material)
Acceptance:   checkable conditions, including failure and edge behavior
Review focus: failure modes/inputs not covered explicitly by acceptance
Risks:        concrete failure or migration risks (when real)
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
