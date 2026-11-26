---
name: Orchestration
description: Use for complex, cross-cutting, or multi-step coding work when deciding whether to work directly, delegate one bounded task, or run parallel read-only investigation with native OpenCode subagents. Covers routing, briefs, file ownership, parallel work, review, and final integration without plugins, hooks, or background schedulers. Not for a small sequential edit, a single obvious file, executing an approved implementation plan, or installing an agent framework; use autonomous-execution for approved plan execution.
license: MIT
compatibility: opencode
---

# Orchestration

## What this is

Orchestration is a decision layer, not a runtime. The main session owns the conversation, plan, Git, and final judgment. It uses OpenCode's native `subagent` tool when a bounded specialist saves context or exposes independent work; otherwise it works directly.

Do not add a plugin, hook, background job service, marketplace, TUI, or model profile to use this skill. Built-in `explore` denies edits, `skill`, and `question` by default while still permitting `shell` — keep its briefs self-contained inline and explicitly forbid mutating shell commands. Built-in `general` handles implementation, testing, or read-only review when the brief says so, and denies `question` and `subagent` by default.

When a plan is already approved and the user asked to execute it, hand off to `autonomous-execution`; do not re-plan or orchestrate the same work.

## Routing matrix

| Situation | Route |
|---|---|
| One obvious file, small fix, sequential decision | Work directly. |
| Unknown area, broad search, or "where is this?" | One `explore` with a mapping brief. |
| Two or more independent read-only questions | Parallel `explore` calls, at most three, each with a disjoint question. |
| Two or more unrelated failures or independent fixes | One `general` owner per failure domain; disjoint files and no shared state; integrate and run the full suite. |
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
Plan task: <plan path#task or "read-only investigation">
Context: relevant paths, current behavior, interfaces, prior rulings, and acceptance
Ownership: files or subsystem within the repository/worktree root you may write; "read-only" if none
Constraints: no subagents, no mutating shell if read-only, no Git/publication, no secrets, project checks
Expected output: files changed and evidence, or findings with file:line (partial done + remaining if work outgrows the brief)
Verification: command(s) and expected result
Stop: what forces returning a blocker/question to the main session instead of guessing
```

A subagent does not inherit the goal, the plan, or the user's permission to change scope. Give it the minimum context it needs, not the whole session.

## Rules

- **One writer per file.** Parallel writers must have disjoint ownership explicitly bounded to the repository/worktree root (external directories may be allowed by default). Shared files and shared refactors are sequential.
- **One brief, not the whole plan.** A subagent gets the task block and cross-task decisions it needs; do not paste the entire plan or session history.
- **Async background lifecycle.** Subagents always run in the background and return a `sessionID` immediately: continue only disjoint safe work or end the turn and wait for completion notifications. Never sleep, poll, or inspect a running writer's files.
- **Continuation vs fresh context.** Reuse a child's `sessionID` for follow-ups on the same brief or delta; omit `sessionID` (fresh child) when independent context is required (such as initial or whole-branch review).
- **Read-only means read-only.** Say it explicitly in the brief, forbid mutating shell commands, and keep `explore` briefs self-contained inline (do not assume `explore` can load skills).
- **No direct user prompts from subagents.** Children return stop-condition blockers and questions to the main session; only the main session asks the user.
- **Bound by brief, not turn caps.** Size each brief for one delegate, encourage parallel independent reads per turn, and instruct the child to return a clean partial report (done + remaining) if work outgrows the brief.
- **Direct visual inspection.** Read screenshots and visual artifacts directly when your active model supports vision; delegate only when it does not or when parallel visual audit saves context.
- **Subagents do not publish.** They do not commit, push, open/merge PRs, create releases, change settings, or edit the user's global config.
- **No recursive delegation.** A child works the brief; it does not spawn more agents or invent a new plan.
- **Wait for dependencies.** Do not integrate a result from a running child. Parallelize only independent read-only work or disjoint writers.
- **Inspect the result.** Read the diff and rerun the affected checks; do not trust a report as evidence.
- **Keep the ledger.** For planned work, keep the unified ledger (`docs/plans/<plan-basename>.progress.md` or inline `## Ledger`) with plan, task, owner/session ID, BASE, status, files, commands, evidence, rulings, deferred items, and next action.
- **Do not use orchestration as a substitute for thinking.** If the next step is unclear, plan or debug first; more agents do not remove ambiguity.

## Loop

1. Restate the outcome and the acceptance checks.
2. Draw the dependency graph: what must be known, what can run in parallel, what one writer owns.
3. Choose direct, one delegate, or a bounded parallel set.
4. Dispatch with the brief template.
5. Continue only safe independent work or yield the turn for background notifications; never sleep/poll or touch a child's files.
6. Integrate results, resolve conflicts, run the full checks.
7. Send the material diff to a fresh reviewer (new child session); fix and recheck.
8. Deliver from the main session with evidence.

Use `specification` and `implementation-planning` when the request is still ambiguous. Use `systematic-debugging` before delegating a symptom. Use `test-driven-development` for implementation. Use `code-review` and `delivery` for the final gates.

## Model profiles

This skill intentionally does not choose provider models, reasoning effort, or presets. Use whatever models and agents your OpenCode configuration already exposes. If you define custom agent names, substitute them for `explore`/`general` in the briefs; do not create a plugin just to change a model.

## Independent failure dispatch

When several failures are genuinely independent — different test files, subsystems, or root causes — dispatch one owner per domain. Give each a focused scope, the exact failing evidence, disjoint write ownership, and a no-refactor constraint. Do not parallelize related failures, a shared design decision, or two writers in one file. Integrate the results, then run the full suite; never trust a child's success report without inspecting the diff.

## Stop conditions

Stop and ask only when:

- the route requires an irreversible or destructive action;
- the work needs a credential or security-sensitive change outside the approved scope;
- publication, merge, release, or a side effect outside the working copy is required;
- the plan is broken or conflicting enough that every path forward is a guess;
- integrating would depend on a child result that is still running.

A failed child is a finding, not permission to broaden its brief.

## Output

The main session reports what ran directly, what was delegated, what changed, which checks passed, what was reviewed, and what remains.
