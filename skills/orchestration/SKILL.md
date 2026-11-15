---
name: Orchestration
description: Use for complex, cross-cutting, or multi-step coding work when deciding whether to work directly, delegate one bounded task, or run parallel read-only investigation with native OpenCode subagents. Covers routing, briefs, file ownership, parallel work, review, and final integration without plugins, hooks, or background schedulers. Not for a small sequential edit, a single obvious file, or installing an agent framework.
license: MIT
compatibility: opencode
---

# Orchestration

## What this is

Orchestration is a decision layer, not a runtime. The main session owns the conversation, plan, Git, and final judgment. It uses OpenCode's native `subagent` tool when a bounded specialist saves context or exposes independent work; otherwise it works directly.

Do not add a plugin, hook, background job service, marketplace, TUI, or model profile to use this skill. `explore` is the read-only mapper; `general` is the writer/reviewer/tester when the brief says so.

## Routing matrix

| Situation | Route |
|---|---|
| One obvious file, small fix, sequential decision | Work directly. |
| Unknown area, broad search, or "where is this?" | One `explore` with a mapping brief. |
| Two or more independent read-only questions | Parallel `explore` calls, at most three, each with a disjoint question. |
| Independent implementation in disjoint files | One `general` writer per workstream; serialize shared files. |
| Verification of a risky change | Main session plus a `general` tester with a read-only brief. |
| Material change before merge | Fresh `general` reviewer with spec, diff, tests, and open questions. |
| Delivery, merge, release | Main session only. Never delegate publication or Git authority. |

When the work is mostly discovery, prefer several small read-only briefs over one giant research prompt. When the work is mostly implementation, one writer per ownership boundary is safer than many eager agents.

## Brief template

Every delegated task is self-contained:

```text
Role: observer | implementer | tester | reviewer
Goal: one observable outcome
Context: relevant paths, current behavior, and the spec/acceptance
Ownership: files or subsystem you may write; "read-only" if none
Constraints: no subagents, no Git/publication, no secrets, project checks
Expected output: files changed and evidence, or findings with file:line
Verification: command(s) and expected result
Stop: what forces a question instead of a guess
```

A subagent does not inherit the goal, the plan, or the user's permission to change scope. Give it the minimum context it needs, not the whole session.

## Rules

- **One writer per file.** Parallel writers must have disjoint ownership. Shared files and shared refactors are sequential.
- **Read-only means read-only.** Say it explicitly in the brief and do not ask an `explore` agent to implement.
- **Subagents do not publish.** They do not commit, push, open/merge PRs, create releases, change settings, or edit the user's global config.
- **No recursive delegation.** A child works the brief; it does not spawn more agents or invent a new plan.
- **Wait for dependencies.** Do not integrate a result from a running child. Parallelize only independent read-only work or disjoint writers.
- **Inspect the result.** Read the diff and rerun the affected checks; do not trust a report as evidence.
- **Keep the ledger.** Record the task, owner, session ID, status, commands, evidence, and next action.
- **Do not use orchestration as a substitute for thinking.** If the next step is unclear, plan or debug first; more agents do not remove ambiguity.

## Loop

1. Restate the outcome and the acceptance checks.
2. Draw the dependency graph: what must be known, what can run in parallel, what one writer owns.
3. Choose direct, one delegate, or a bounded parallel set.
4. Dispatch with the brief template.
5. Continue only safe independent work; do not touch a child's files.
6. Integrate results, resolve conflicts, run the full checks.
7. Send the material diff to a fresh reviewer; fix and recheck.
8. Deliver from the main session with evidence.

Use `specification` and `implementation-planning` when the request is still ambiguous. Use `systematic-debugging` before delegating a symptom. Use `test-driven-development` for implementation. Use `code-review` and `delivery` for the final gates.

## Model profiles

This skill intentionally does not choose provider models, reasoning effort, or presets. Use whatever models and agents your OpenCode configuration already exposes. If you define custom agent names, substitute them for `explore`/`general` in the briefs; do not create a plugin just to change a model.

## Stop conditions

Stop and ask when the route would change scope, require a credential or destructive action, publish something, or depend on a child result that is still running. A failed child is a finding, not permission to broaden its brief.

## Output

The main session reports what ran directly, what was delegated, what changed, which checks passed, what was reviewed, and what remains.
