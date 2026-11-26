---
name: Delivery
description: Use when implementation and review are complete to prove the result with fresh checks and deliver it through a PR, merge, and cleanup. Covers evidence gates, diff review, PR content, required checks, no-bypass merge rules, release handoff, and truthful completion reports. Not for starting implementation or merging unverified work.
license: MIT
compatibility: opencode
---

# Delivery

## Evidence before claims

A completion claim needs fresh evidence from the current tree:

- the exact command that was run;
- the result and relevant output;
- the scope it covers;
- what was not tested and why.

Use PASS, FAIL, or NOT_TESTED. A local check does not replace a required CI check. If a check cannot run, say so and use the best available substitute rather than inventing a result.

| Claim | Evidence required | Not sufficient |
|---|---|---|
| Tests pass | command + exit code + failure count | "should pass" or an earlier run |
| Build passes | build command + exit 0 | linter only |
| Bug fixed | original symptom now passes + regression test | code changed |
| Requirements met | acceptance checklist, item by item | tests alone |
| Agent finished | diff inspected + checks rerun | agent report |

## Before the PR

1. Re-read the spec and acceptance checks.
2. Run the full required local suite on the final tree.
3. Review the complete diff against the base, not only your last edit.
4. Check for secrets, generated files, debug output, unrelated changes, and broken links. When scanning diffs for secrets, report file paths or `file:line` only (`--name-only`) — never echo matched secret values into terminal output or transcripts.
5. Confirm every issue/acceptance item is represented in the change.
6. Update documentation, changelog, and plan/tracker status as required.

## PR content

Include: goal, issue link, what changed, why, tests and evidence, risks, compatibility, rollback, and anything intentionally not done. Keep the PR focused. Do not mix unrelated refactors. Use the repository's template when present.

## Integration choice

Before merging, confirm the base branch and present the integration choice:

1. Merge locally into the base and verify the merged result.
2. Push the branch and open a PR; keep the branch for review.
3. Keep the branch/worktree as-is.

Discard is allowed only after an explicit request and confirmation. Do not choose a destructive discard or force-push on your own. When working on a detached `HEAD`, offer only pushing to a new branch (`git push origin HEAD:refs/heads/<branch>`) + PR or keeping as-is. If the change came from a worktree, capture the worktree path, verify the base and test the merged result, `cd` to the main repository root before removing the worktree (using the harness's native remove operation when created natively), and never `--force` remove a dirty worktree without explicit confirmation.

## Merge gate

- The head commit is the one tested.
- The diff is reviewed and conflicts are resolved.
- Required checks, reviews, and conversations are satisfied.
- No admin bypass, force push, or self-approval is used to get around a protection.
- Merge method matches the repository policy.
- After merge, verify the actual main commit and the expected files/content.
- If a push or merge is rejected, inspect the actual remote state; do not retry with force.

An auto-merge queue is not a merge; confirm the final commit. If checks fail, fix the cause and rerun the affected checks; do not edit the test to hide a regression.

## Post-merge verification

After merge, fetch the base branch, confirm the merge/squash commit, and inspect the actual content on the base branch: the expected files, tests, docs, and tracker state. Run the affected checks on that commit or confirm the required CI run for that exact commit. A local branch or a merge queue entry is not delivery.

## Change summary

Report: files changed; what was intentionally not touched; commands and results; reviewed-by (or self-review); risks; NOT_TESTED items; PR and merge commit; tracker items closed. Keep it concise and evidence-based.

## Cleanup

Delete your branch after its changes are in main and no dependent branch needs it. Do not delete other people's branches or untracked work. Report the PR, merge commit, checks, and any residual.

## Release handoff

Publishing a release, tag, deployment, or production change is a separate authority unless the task explicitly includes it. Follow the repository's release process and verify the actual artifact, checksum, and published state.

## Red flags

- "Should work" or "tests pass" without a command and output.
- Merging with a red, missing, or unreported required check.
- Closing an issue without acceptance evidence.
- Force-pushing over review history.
- Treating a drafted PR, an auto-merge queue entry, or a local commit as delivery.
- Deleting a branch before confirming the merge commit.

## Output

A delivered, verified change with the PR/merge commit and a completion report that separates what passed, what failed, what was not tested, and what remains.
