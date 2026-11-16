# Skill Suite v2 — planning, execution, review

Status: DONE
Date: 2026-11-16
Spec: user request to strengthen the suite using current skill repositories
Sources:

- https://github.com/obra/superpowers (MIT)
- https://github.com/addyosmani/agent-skills (MIT)
- https://github.com/OthmanAdi/planning-with-files (MIT)
- https://github.com/wshobson/agents (MIT)
- https://github.com/anthropics/skills (README: Apache 2.0 for many skills; verify per skill)

## Goal

Make the existing OpenCode skill suite materially better at long planning and
execution without adding a plugin, hooks, a background scheduler, a hidden
workspace, or a second overlapping suite. Plans and execution state belong to
the project in `docs/plans/`, not to a tool-owned directory.

## Architecture

Keep the current responsibilities:

- `specification` defines the problem, outcome, non-goals, options, constraints,
  acceptance, and review focus.
- `implementation-planning` turns an accepted spec into a project-local plan
  with exact files, interfaces, tests, commands, expected results, checkpoints,
  and a self-review.
- `autonomous-execution` executes the plan with a task brief, a persistent
  ledger, TDD, rulings, per-task review, and a final review.
- `orchestration` routes discovery, independent work, writers, and reviewers;
  it does not own the plan or publication.
- `code-review`, `delivery`, `clean-code`, and `skill-authoring` remain the
  quality and maintenance layer.

No new runtime. No `.superpowers/`, no hooks, no model profiles.

## Tech stack

Markdown skills, the existing Python validator and pytest suite, the existing
OpenCode native `skill`/`subagent` tools. No new runtime dependency.

## Global constraints

- Plan files: `docs/plans/YYYY-MM-DD-<slug>.md`.
- Execution ledger: `docs/plans/YYYY-MM-DD-<slug>.progress.md` for long tasks;
  short tasks may keep a ledger section in the plan file.
- Do not overwrite an incomplete plan; report the conflict.
- One writer per file; subagents never own Git, publication, or the ledger.
- Preserve existing trigger descriptions and handoffs; add content where it
  changes behavior, not as a general essay.
- Keep every loaded skill within the 32 KiB reading budget and validate links.
- Cite sources and licenses; do not copy upstream text.

## Review focus

1. A fresh executor can implement a task without the planning conversation.
2. A compaction or session restart can resume from the plan and ledger.
3. A subagent receives a self-contained brief and no unrelated plan context.
4. A failed plan assumption becomes a recorded ruling, not a silent scope change.
5. A reviewer can verify tests, behavior, and scope without trusting a report.

## Tasks

### SKL2-01 — Plan contract and project-local workspace

Files:

- `skills/specification/SKILL.md`
- `skills/implementation-planning/SKILL.md`
- `tests/test_skill_suite.py`

Interfaces:

- Consumes: accepted spec from `specification`.
- Produces: `docs/plans/YYYY-MM-DD-<slug>.md` consumed by `autonomous-execution`.

Steps:

- [x] Add an **Approaches / design note** step to specification; require 2–3
  viable approaches and a recommendation when the choice is material.
- [x] Add a **Review focus** section to the spec template: the failure modes or
  inputs the acceptance does not cover explicitly.
- [x] Add the plan header: Goal, Architecture, Tech Stack, Spec, Global
  Constraints, Review Focus.
- [x] Add a file-structure map and per-task `Files`, `Interfaces:
  Consumes/Produces`, checkbox steps, exact tests/commands, and `Expected`.
- [x] Add vertical slices, task sizes, checkpoints after 2–3 tasks, and the
  no-overwrite rule for incomplete plans.
- [x] Keep the save path `docs/plans/YYYY-MM-DD-<slug>.md`; explicitly reject
  `docs/superpowers/` and hidden plan directories.
- [x] Add contract tests for the required sections and the project-local path.

Verify:

- `python3 -m pytest -q tests/test_skill_suite.py`
- `python3 scripts/validate.py`
- `make check`

Acceptance:

- A fresh engineer can execute a plan without this session.
- Every task names files, interfaces, a test/command, expected result, and a
  dependency.
- No hidden plan state is introduced.

### SKL2-02 — Execution ledger, task briefs, and rulings

Files:

- `skills/autonomous-execution/SKILL.md`
- `skills/orchestration/SKILL.md`
- `tests/test_skill_suite.py`

Interfaces:

- Consumes: plan contract from SKL2-01.
- Produces: `docs/plans/<slug>.progress.md`; self-contained task briefs for
  subagents.

Steps:

- [x] Add the ledger shape: plan file, task ID, BASE commit, status, commands,
  expected vs actual, evidence, rulings, next step.
- [x] Add the task-brief rule: a subagent reads one task brief, not the whole
  plan; the main session owns cross-task interfaces and decisions.
- [x] Add `Ruling:` for plan/spec conflicts; carry rulings to later tasks.
- [x] Add the 3-strike error protocol and a bounded retry/stop rule.
- [x] Add per-task review and final whole-branch review; the reviewer gets the
  spec, diff range, tests, and open questions.
- [x] Add orchestration routing for independent failure domains, writer
  ownership, and the four stop conditions.
- [x] Test the required headings, ledger path, and no hidden workspace.

Verify:

- `python3 -m pytest -q tests/test_skill_suite.py`
- `python3 scripts/validate.py`
- `make check`

Acceptance:

- A resumed session can recover from the plan and ledger.
- Subagents get only a bounded brief and cannot publish or edit the ledger.
- Independent failures can run in parallel; shared files cannot.

### SKL2-03 — Review and delivery quality bars

Files:

- `skills/code-review/SKILL.md`
- `skills/delivery/SKILL.md`
- `skills/clean-code/SKILL.md`
- `tests/test_skill_suite.py`

Interfaces:

- Consumes: implementation and evidence from SKL2-02.
- Produces: reviewed, merge-ready change with a truthful completion report.

Steps:

- [x] Add tests-first review, a mutation check, five review axes, severity
  calibration, structural remedies, and change-size guidance to code review.
- [x] Add the integration choice, post-merge verification, change summary, and
  explicit NOT_TESTED handling to delivery.
- [x] Add scope discipline and a simplicity check to clean code; do not mix
  cleanup with behavior changes.
- [x] Preserve P0/P1/P2 compatibility while adding the new labels/axes.
- [x] Add contract tests for the new review/delivery sections.

Verify:

- `python3 -m pytest -q tests/test_skill_suite.py`
- `python3 scripts/validate.py`
- `make check`

Acceptance:

- Review findings are evidence-based and calibrated.
- Delivery verifies the actual merged commit, not just a local branch.
- Clean-code changes remain behavior-preserving and scoped.

### SKL2-04 — Skill evals, trigger quality, attribution

Files:

- `skills/skill-authoring/SKILL.md`
- `THIRD_PARTY_NOTICES.md`
- `CHANGELOG.md`
- `README.md`
- `tests/test_skill_suite.py`

Interfaces:

- Consumes: improved planning/execution/review skills.
- Produces: documented source attribution and a repeatable skill evaluation
  workflow.

Steps:

- [x] Add trigger mining, baseline-vs-skill eval, pressure variants, versioning,
  and license checks to skill authoring.
- [x] Add source entries for superpowers, addyosmani/agent-skills,
  planning-with-files, wshobson/agents, and anthropics/skills; state the license
  and what idea was used.
- [x] Add an Unreleased changelog entry for the v2 suite.
- [x] Update README/AGENTS only where the skill list or workflow changed.
- [x] Add contract tests for the eval/authoring sections.

Verify:

- `python3 -m pytest -q tests/test_skill_suite.py`
- `python3 scripts/validate.py`
- `make check`

Acceptance:

- A new skill has a baseline, trigger test, pressure variants, and a source
  license before it is merged.
- Attribution is present and does not claim copied text.
- The suite remains within the reading budget.

## Acceptance map

| Spec outcome | Task | Evidence |
|---|---|---|
| Project-local plan contract | SKL2-01 | plan file and contract tests |
| Resumable execution | SKL2-02 | ledger tests and sample paths |
| Independent review/delivery | SKL2-03 | review/delivery contract tests |
| Measured, attributed skills | SKL2-04 | eval/authoring tests and notices |

## Risks and rollback

- Risk: more instructions increase context cost. Mitigation: add only sections
  that change decisions; keep references inline only where needed.
- Risk: two plans diverge. Mitigation: one plan file, one ledger path, one
  owner; no hidden workspace.
- Risk: borrowed text/license ambiguity. Mitigation: synthesize, cite, and
  verify per-skill licenses; no wholesale copying.
- Rollback: revert the individual skill task; no runtime or configuration
  coupling.

## Final acceptance

- All four IDs are implemented in one scoped PR or a dependency-ordered set.
- `make check` passes with the expanded contract tests.
- Plan/ledger paths are project-local and documented.
- Tracker issues close only after the merge and evidence check.

## Evidence

- `make check` — PASS, 201 tests, 11 skills, markdownlint, Ruff, ShellCheck, dry-run installer, CSS, workflow policy.
- `python3 scripts/validate.py` — PASS.
- `git diff --check` — PASS.
- Tracker: #58, #59, #60, #61; milestone #8.
