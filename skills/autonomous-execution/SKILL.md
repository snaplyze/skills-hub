---
name: Autonomous Execution
description: Use to execute an approved implementation plan autonomously with small commits, test-first gates, a visible ledger, optional subagents or worktrees, and clear stop conditions. Use for multi-task plans where the user asked for implementation, not for planning or debugging unknowns. Handles parallel independent tasks without sharing files.
license: MIT
compatibility: opencode
---

# Autonomous Execution

## What this is

Execution is coordination, not typing. Keep the plan, the current task, the evidence, and the next action visible; let subagents own isolated slices; and stop only for a real decision or blocker. Do not turn execution into a new planning session.

## Preflight

1. Read the plan and the relevant spec. If acceptance or dependencies are missing, return to planning instead of guessing.
2. Check the workspace: current branch, dirty files, baseline test command, and whether an isolated workspace already exists. Use the current workspace by default; create a worktree only when isolation is needed and the user/project permits it.
3. Define the ledger: plan path, task ID, status, files owned, commands run, evidence, and blockers. Update it after every task.
4. Establish a green baseline or record the pre-existing failure. Never attribute an old failure to the new work.

## The task loop

1. **Read the task and its acceptance.** Restate the expected behavior in one line.
2. **Protect ownership.** One writer per file. Parallel tasks must touch disjoint files or use isolated workspaces; shared files are sequential.
3. **Write the failing test first.** Run it and capture the failure. Use `test-driven-development` for the red-green-refactor loop.
4. **Make the smallest coherent change.** Do not add unrelated cleanup or speculative abstractions.
5. **Run the narrow check, then the affected checks.** Add the full project check before declaring the task complete.
6. **Review the diff.** Remove dead code, debug output, generated artifacts, and secrets. Check scope.
7. **Commit the task.** Commit only the task's files; keep the message focused.
8. **Update the ledger.** Record status, commands, evidence, and the next task. Continue without asking permission between planned tasks.

## Isolation

Check whether the workspace is already isolated before creating anything. Use the current checkout by default; create a worktree or equivalent only when the task needs a clean branch alongside other work and the project/user permits it. If you create one, verify it points at the intended base commit, install/setup as the project requires, and run the baseline checks there. Remove only your own clean worktree at the end; do not delete another agent's workspace or uncommitted work.

## Subagents and parallelism

Give each subagent a self-contained brief: goal, context and paths, write ownership, constraints, expected result, verification, and stop condition. Subagents do not own the goal, Git/publication, or the ledger. Do not let two agents write the same file. When results return, inspect the diff and rerun the relevant checks rather than trusting the report.

Use parallelism only for independent work: separate files, separate investigations, separate test failures. Do not parallelize a design decision, a shared refactor, or a sequence with a hidden dependency.

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
- Report PASS/FAIL/NOT_TESTED with exact commands and outputs.
- Hand off to `code-review` and then `delivery`; do not merge on your own authority.

## Never

- Skip or weaken a failing test to keep moving.
- Claim a check passed without running it.
- Force-push, bypass a review, or commit secrets.
- Rewrite unrelated files because they are convenient.
- Leave the ledger claiming work that was not verified.
