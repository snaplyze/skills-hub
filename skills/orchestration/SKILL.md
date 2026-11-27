---
name: orchestration
description: Use for complex, cross-cutting, or multi-step coding work when deciding whether to work directly, delegate bounded subagents, run a dynamic workflow, or recommend a built-in Antigravity orchestrator. Covers routing, briefs, workspace isolation, file ownership, parallel work, review, and final integration without plugins, hooks, or custom schedulers. Not for a small sequential edit, a single obvious file, executing an approved implementation plan, or installing an agent framework; use autonomous-execution for approved plan execution.
license: MIT
compatibility: agentskills
---

# Orchestration

## What this is

Orchestration is a decision layer, not a runtime. The main conversation owns the goal, plan, Git, user interaction, and final judgment. It uses Antigravity's native delegation tools (`invoke_subagent`, `define_subagent`, `send_message`, `manage_subagents`, and `run_workflow`) when isolated context, parallel research, or scripted fan-out improves outcomes; otherwise it works directly.

Do not install plugins, hooks, custom agent files, or model-profile frameworks to use this skill. Built-in subagents cover most needs out of the box:

- **`research`**: read-only sandbox (no writes, no network) for codebase exploration, search, and structural mapping.
- **`browser`**: live UI verification, screenshots, DOM, console, and network inspection (built-in browser in Antigravity App; Chrome via `/browser` in CLI/IDE).
- **`self`**: full clone of the parent agent for bounded implementation, testing, or scoped tasks.
- **Transient read-only subagents (`define_subagent` with `EnableWriteTools: false`)**: hard read-only enforcement for independent code review or audits without creating project files.

When a plan is already approved and the user asked to execute it, hand off to `autonomous-execution`; do not re-plan or orchestrate the same work.

## Routing matrix

| Situation | Route |
|---|---|
| One obvious file, small fix, sequential decision | Work directly. |
| Unknown area, broad search, or "where is this?" | One `research` subagent (`workspace: "inherit"`) with a mapping brief. |
| Two or more independent read-only questions | Parallel `research` calls, at most three, each with a disjoint question. |
| Live UI, layout, console, or interaction verification | `browser` subagent (or recommend `/browser` if user setup is needed). |
| Two or more unrelated failures or independent fixes | One `self` owner per failure domain with disjoint files (`workspace: "share"` or `"branch"` if builds/edits overlap); integrate and run the full suite. |
| Independent implementation in disjoint files | One `self` writer per ownership boundary (`workspace: "share"` for concurrent edits/builds); serialize shared files. |
| Many uniform items (per-file audits, staged pipelines, structured JSON aggregation) | Dynamic workflow via `run_workflow` (`parallel()` / `pipeline()` with explicit JSON `schema`). |
| Verification of a risky change | Main session plus a fresh read-only tester/reviewer subagent (`define_subagent` with `EnableWriteTools: false`). |
| Material change before merge | Fresh read-only reviewer subagent with spec, diff, tests, and open questions. |
| Broad multi-worker coordination with peer chat, hard deep-reasoning bugs, or multi-day campaigns | Recommend Antigravity's built-in user-invoked orchestrators: `/swarm` (broad parallel work + `@verifier`, all plans), `/boost` (hard bugs/races/algorithms, paid plans), or `/teamwork` (multi-milestone teams, paid plans). Never invoke `/swarm` unprompted. |
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
Workspace: inherit | share | branch
Constraints: no recursive subagents, no writes if read-only, no Git/publication, no secrets, project checks
Expected output: files changed and evidence, or findings with file:line (partial done + remaining if work outgrows the brief)
Verification: command(s) and expected result
Stop: what forces returning a blocker/question to the main session instead of guessing
```

A subagent starts with a clean context and does not inherit the parent's conversation history, plan, or authority to widen scope. Give it the minimum context it needs, not the whole session.

## Rules

- **One writer per file.** Parallel writers must have disjoint ownership bounded to the repository/worktree root. Use `workspace: "share"` (shared-repo working copy) or `"branch"` (isolated clone) when parallel writers edit or run builds/tests simultaneously. Shared files and shared refactors are sequential.
- **Land work before killing isolated workspaces.** Killing a subagent via `manage_subagents` permanently deletes its `share`/`branch` workspace. Integrate or merge its changes into the target branch before terminating it.
- **One brief, not the whole plan.** A subagent gets the task block and cross-task decisions it needs; do not paste the entire plan or session history.
- **Async background lifecycle and reactive wakeup.** `invoke_subagent` and `run_workflow` run asynchronously and return a `conversationId` or task immediately. Continue only disjoint safe work or end the turn and wait for reactive wakeup notifications. Never poll in a loop, never use shell `sleep`, and never touch a running writer's files.
- **Continuation vs fresh context.** Continue an idle subagent's retained context with `send_message(Recipient=conversationId, ...)` for follow-ups on the same brief or delta; launch a fresh `invoke_subagent` when independent context is required (such as initial or whole-branch review).
- **Read-only means read-only.** Use built-in `research`, `define_subagent` with `EnableWriteTools: false`, or a read-only custom agent; state read-only explicitly in the brief and forbid mutating commands.
- **No direct user prompts from subagents.** Children return stop-condition blockers and questions to the parent conversation; only the main session coordinates scope decisions with the user (tool approval prompts bubble cleanly to the UI).
- **Bound by brief, not turn caps.** Size each brief for one delegate, encourage parallel independent reads per turn, and instruct the child to return a clean partial report (`done + remaining`) if work outgrows the brief.
- **Direct visual inspection.** Read screenshots and visual artifacts directly when your active model supports vision; delegate live page interaction, screenshots, and console/network checks to `browser`.
- **Subagents do not publish.** They do not commit, push, open/merge PRs, create releases, change repository settings, or edit user-global Antigravity configuration.
- **Keep delegation flat.** Although Antigravity enforces a hard nesting depth cap of 10, delegated leaf workers execute their brief without spawning nested subagents unless explicitly assigned an orchestration workflow.
- **Never start `/swarm` unprompted.** Recommend `/swarm`, `/boost`, or `/teamwork` when warranted, and invoke `swarm` only when the user explicitly started `/swarm` or an active swarm is already running.
- **Wait for dependencies and inspect results.** Do not integrate output from a running child. Read the actual diff and rerun affected checks; never trust a child's report as verification evidence.
- **Keep the ledger.** For planned work, keep the unified ledger (`docs/plans/<plan-basename>.progress.md` or inline `## Ledger`) with plan, task, owner/`conversationId`, BASE, status, files, commands, evidence, rulings, deferred items, and next action.
- **Do not use orchestration as a substitute for thinking.** If the next step is unclear, plan or debug first; more agents do not remove ambiguity.

## Loop

1. Restate the outcome and the acceptance checks.
2. Draw the dependency graph: what must be known, what can run in parallel, what one writer owns.
3. Choose direct work, focused subagent(s), `run_workflow`, or a recommendation for `/swarm` / `/boost` / `/teamwork`.
4. Dispatch with the brief template (and `workspace: "share"`/`"branch"` for concurrent writers).
5. Continue only safe independent work or end the turn for reactive wakeup; never poll, shell-sleep, or touch a running writer's files.
6. Integrate results (before terminating isolated workspaces), resolve conflicts, and run full checks.
7. Send the material diff to a fresh read-only reviewer subagent; fix and recheck.
8. Deliver from the main session with evidence.

Use `specification` and `implementation-planning` when the request is still ambiguous. Use `systematic-debugging` before delegating a symptom. Use `test-driven-development` for implementation. Use `code-review` and `delivery` for the final gates.

## Model tiers

This skill intentionally does not hardcode provider models, reasoning effort, or presets. Leave `Model` at `"inherit"` by default; optionally pick Antigravity's built-in tiers (`"flash_lite"` / `"flash"` for fast, high-fan-out scans; `"pro"` for deeper analysis) when helpful. If the user's configuration (`~/.gemini/config/agents/` or `.agents/agents/`) already defines custom agents, pass their name to `TypeName`; do not create plugins or project agent files just to change a model.

## Independent failure dispatch

When several failures are genuinely independent — different test files, subsystems, or root causes — dispatch one owner per domain (`self` with disjoint write ownership, using `workspace: "share"` if builds/tests contend). Give each a focused scope, the exact failing evidence, explicit ownership, and a no-refactor constraint. Do not parallelize related failures, a shared design decision, or two writers in one file. Integrate the results, then run the full suite; never trust a child's success report without inspecting the diff.

## Stop conditions

Stop and ask only when:

- the route requires an irreversible or destructive action;
- the work needs a credential or security-sensitive change outside the approved scope;
- publication, merge, release, or a side effect outside the working copy is required;
- the plan is broken or conflicting enough that every path forward is a guess;
- integrating would depend on a child result that is still running.

A failed child is a finding, not permission to broaden its brief.

## Output

The main session reports what ran directly, what was delegated (subagents or workflows), what changed, which checks passed, what was reviewed, and what remains.
