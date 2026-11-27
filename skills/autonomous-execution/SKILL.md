---
name: autonomous-execution
description: Use to execute an approved implementation plan autonomously with small commits, test-first gates, a visible ledger, optional subagents or isolated workspaces, and clear stop conditions. Use for multi-task plans where the user asked for implementation. Not for planning, spec discovery, or debugging an unknown cause; use the corresponding skill first.
license: MIT
compatibility: agentskills
---

# Autonomous Execution

## What this is

Execution is coordination, not typing. Keep the plan, the current task, the evidence, and the next action visible; let subagents own isolated slices; and stop only for a real decision or blocker. Do not turn execution into a new planning session.

## Preflight

1. Read the plan and the relevant spec. If acceptance or dependencies are missing, return to planning instead of guessing.
2. Check the workspace using the Isolation section below; establish the baseline before editing.
3. Create or resume the ledger at `docs/plans/<plan-basename>.progress.md` (or a `## Ledger` section in the plan for a short task). Record the plan path, task ID, owner/session, BASE commit, status, files owned, commands, expected vs actual output, evidence, rulings, deferred items, and next step. Update it after every task.
4. Establish a green baseline or record the pre-existing failure. Never attribute an old failure to the new work.
5. If resuming after compaction or a restart, read the plan, ledger, and `git diff --stat`; trust those over recollection. A ledger whose plan path differs from the current plan is not yours to reuse.

## Ledger

The ledger is the recovery map, not a progress essay. Keep one row or block per task:

```text
Plan: docs/plans/2026-11-16-feature.md
Task: T2 — add validation
Owner / Session: main | <subagent id>
BASE: <commit before the task>
Status: in_progress | done | blocked
Files: <owned paths>
Commands: <command> -> <expected> -> <actual>
Evidence: <test/build output summary>
Ruling: <decision + why + cost if wrong>
Deferred: <minor/P2 items forwarded to final review>
Next: T3
```

For a short task, a `## Ledger` section in the plan is enough. For a long task,
use the separate `progress.md` file. Never hide it in a tool-owned directory.

## The task loop

1. **Read the task and its acceptance.** Restate the expected behavior in one line. Note the BASE commit before changing anything.
2. **Read the task brief.** Use the plan's task block (or the brief derived from it); do not rely on a summary from earlier context.
3. **Protect ownership.** One writer per file. Parallel tasks must touch disjoint files or use isolated workspaces; shared files are sequential.
4. **Write the failing test first.** Run it and capture the failure. Use `test-driven-development` for the red-green-refactor loop.
5. **Make the smallest coherent change.** Do not add unrelated cleanup or speculative abstractions.
6. **Run the narrow check, then the affected checks.** Add the full project check before declaring the task complete.
7. **Review the diff.** Remove dead code, debug output, generated artifacts, and secrets. When scanning diffs for secrets, report file paths or `file:line` only (for example `--name-only`) and never echo matched secret values into terminal output or transcripts. Check scope.
8. **Commit the task and append the ledger line in the same turn.** Commit only the task's files; keep the message focused.
9. **Update the ledger.** Record status, commands, evidence, and the next task. Continue without asking permission between planned tasks.

## Task briefs

A subagent gets one self-contained task brief, not the whole plan: role, goal, plan task, relevant files/interfaces, explicit write ownership bounded to the repository/worktree root (or `read-only`), workspace mode (`inherit` | `share` | `branch`), acceptance, constraints, expected output, verification command, stop condition, and any prior `Ruling:` that affects this task. Put it in the dispatch prompt or a temporary file; it is not repository state. The main session owns the plan, cross-task interfaces, user interaction, Git, publication, and final acceptance.

## Rulings and recovery

When the plan conflicts with the spec or the repository reality, decide the smallest change that satisfies the spec, record `Ruling: <finding> — <decision> — <why> — <cost if wrong>` in the ledger, and continue. Do not silently broaden the task.

Use a 3-strike protocol:

1. diagnose and apply a targeted fix;
2. change the approach, not the same action;
3. rethink the assumption and record the attempt;
4. after three failures, stop and report the blocker with evidence.

After every two broad reads or searches, write the useful findings to the ledger or plan. Long tool output goes to a file; read the tail, not the whole dump.

## Isolation

Check whether the workspace is already isolated before creating anything. Use the current checkout by default; create an isolated workspace or worktree only when the task needs a clean branch alongside other work and the project/user permits it. Prefer Antigravity's native workspace isolation (`workspace: "branch"` for an isolated branched/cloned workspace or `"share"` for a new working copy sharing underlying repository storage on `invoke_subagent` or `run_workflow`)—or the active harness's native equivalents. Always land or merge changes from a `branch`/`share` workspace before terminating the subagent (`manage_subagents` permanently deletes isolated workspaces when killing a subagent). If using manual `git worktree`, verify the branch/base, do not copy ignored directories such as `node_modules` or caches, check ignore rules before adding files, `cd` to the main repository root before removing, and remove only your own clean worktree at the end without forcing removal of uncommitted work.

## Review gate

After each task, if a fresh reviewer subagent is available, dispatch `code-review` via a fresh read-only subagent (`research`, `define_subagent` with `EnableWriteTools: false`, or a dedicated read-only reviewer agent — never reusing an implementer's `conversationId`) with the task spec, BASE..HEAD diff, tests, and open questions. If independent review is unavailable, perform the same checklist yourself, record that it is a self-review, and do not claim independent approval. Do not accumulate unreviewed tasks until the end.

Keep the review-fix loop bounded:

1. **Triage:** P0/P1 findings block the next task. Keep P2/minor findings out of the per-task fix loop; log them under `Deferred:` in the ledger and pass that list to the final whole-branch review.
2. **Fix rounds (max 3–5):** continue the original implementer via `send_message` first; if stalled after 2–3 rounds, launch a fresh implementer (`invoke_subagent`) with the diff and evidence. At the cap, adjudicate explicitly in the ledger (`parked` or a load-bearing `Ruling:`) rather than looping or dropping silently.
3. **Scoped re-review:** send the fix delta (`FIX_BASE..HEAD`) for re-review (continuing the reviewer via `send_message` or starting a fresh reviewer): verdict each prior finding `ADDRESSED` or `NOT ADDRESSED`, and flag only new breakage introduced by the fix.

Before delivery, send the whole BASE..HEAD diff, plan acceptance map, deferred minor list, and final evidence to a fresh read-only reviewer subagent for a whole-branch review. Dispatch **one** batched fix pass for final-review findings (never one fixer per finding), followed by one scoped re-review.

## Subagents and parallelism

Use the Task briefs schema above for every subagent dispatch. Subagents (`invoke_subagent`) and dynamic workflows (`run_workflow`)—or the active harness's native equivalents—run asynchronously in the background and return immediately: continue only disjoint safe work or end the turn and wait for reactive wakeup notifications — never poll in a loop, shell-sleep, or touch a running child's files. Subagents cannot negotiate scope directly with the user; instruct them to stop and return blockers to the main session. Continue an idle child's retained context with `send_message(Recipient=conversationId, ...)` for follow-ups on the same brief or delta; launch a fresh `invoke_subagent` when independent context is needed. For large uniform fan-outs or staged pipelines with structured JSON outputs, prefer `run_workflow`. Subagents do not own the goal, Git/publication, or the ledger. Do not let two agents write the same file. When results return, inspect the diff and rerun the relevant checks rather than trusting the report.

Use parallelism only for independent work: separate files, separate investigations, separate test failures. Do not parallelize a design decision, a shared refactor, or a sequence with a hidden dependency. Between long milestones, suggest `/compact` if context pressure grows — recover cleanly from the plan file and ledger.

For parallel branches or worktrees, designate one integration branch and one merge owner. Merge task branches in dependency order, resolve conflicts at the integration branch, and run the full suite on the merged result. Never let two agents resolve the same conflict. Land changes before killing `share`/`branch` subagents, and remove only clean manual worktrees created for the task; keep unmerged work.

## Stop conditions

Stop and ask when:

- the plan conflicts with the spec or repository reality and the fix changes scope;
- a required credential, permission, service, or destructive action is needed outside the approved scope;
- the same failure repeats without a new hypothesis;
- tests cannot run and the available substitute would not prove the claim;
- a new dependency, migration, release, or public API change is required.

A blocker does not stop unrelated safe work. Record it and continue independent tasks.

## Final gate

- Run the full required checks fresh.
- Review the complete diff against the base.
- Confirm every acceptance check and every planned task is accounted for.
- Include an exhaustive **Rulings made** rollup copied from the ledger with each ruling's cost if wrong (no ruling should die quietly in the ledger).
- Report PASS/FAIL/NOT_TESTED with exact commands and outputs.
- Hand off to `code-review` and then `delivery`; do not merge on your own authority.

## Never

- Skip or weaken a failing test to keep moving.
- Claim a check passed without running it.
- Force-push, bypass a review, or commit secrets.
- Rewrite unrelated files because they are convenient.
- Leave the ledger claiming work that was not verified.
