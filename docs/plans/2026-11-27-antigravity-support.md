# Antigravity Support — Stage 10 Implementation Plan

Goal: Add first-class Google Antigravity support (App, CLI `agy`, IDE, and IDE extensions) alongside existing OpenCode support, unifying all 11 skills under the Agent Skills open standard (`agentskills.io`) with zero OpenCode-specific descriptions inside `skills/` and full alignment with Antigravity's native orchestration.

Architecture: Keep OpenCode support intact (`install/opencode.sh`, `docs/opencode-orchestration.md`, OpenCode V2 validator compatibility) while adding Antigravity as a co-equal Ready harness (`install/antigravity.sh`, `docs/antigravity-orchestration.md`, Antigravity discovery and reload guidance). Skill frontmatter adopts strict Agent Skills / Antigravity naming (`name` matching folder ID, exposed as `/<name>`), unified `compatibility: agentskills`, and optional standard fields (`disable-model-invocation`, `metadata`, `allowed-tools`). Inside `skills/`, remove all OpenCode-only runtime wording and express orchestration natively for Antigravity (`invoke_subagent`, `define_subagent`, `send_message`, `manage_subagents`, built-in `research`/`browser`/`self`, `workspace: inherit/share/branch`, `run_workflow`, and user-invoked `/swarm`/`/boost`/`/teamwork`) while staying clear and portable for OpenCode.

Tech stack: Markdown skills, Python 3.12 (`scripts/validate.py`, `pytest`), Bash (`install/antigravity.sh`, `install/opencode.sh`, `shellcheck`), Node.js 22 (`markdownlint-cli2`, `csstree-validator`), GitHub Actions (`make check`). No new runtime dependencies, plugins, or hooks.

Spec: User requests (2026-11-27: add Antigravity support alongside OpenCode; remove OpenCode descriptions from skills and make them unified for Antigravity; use native Antigravity orchestration; organize via plan, issues, and milestone) + official Google Antigravity docs (`antigravity.google/docs/*`) + Agent Skills open standard (`agentskills.io/specification`).

Global constraints:

- Preserve full OpenCode support (`install/opencode.sh`, `docs/opencode-orchestration.md`, `metadata.opencode/autoinvoke` validator support).
- Zero OpenCode-specific runtime wording (`opencode`, `sessionID`, `session.move`, `worktree_remove`, `opencode.json`, `opencode/autoinvoke`) inside `skills/`.
- No project-local plugins, hooks, custom agent definitions, or installed skills committed to this repository (`.agents/`, `.gemini/`, `.opencode/` remain ignored).
- Every skill `SKILL.md` and `frontend-design` reading set stays ≤ 32,768 B.
- All 11 skills pass `scripts/validate.py` and empirical `agy plugin validate` checks with zero skill errors or warnings.
- Historical records (`CHANGELOG.md` v1.0.0–v1.3.0, completed Stage 01–09 plans, upstream attribution URLs) are not rewritten retroactively.
- Releases and `v*` tags remain owner-gated; changes go under `## [Unreleased]` in `CHANGELOG.md`.
- `main` branch protection is respected: PRs only, all required checks green, squash merge, zero bypasses.

Review focus:

1. No residual OpenCode runtime concepts leak into `skills/`; Antigravity understands every skill directly while OpenCode compatibility remains intact.
2. Every skill's `name` matches its directory name (`kebab-case`) and triggers uniquely in cross-skill routing tests without colliding with built-in slash commands.
3. Orchestration clearly distinguishes agent-invoked tools (`invoke_subagent`, `define_subagent`, `send_message`, `manage_subagents`, `run_workflow`) from user-invoked slash orchestrators (`/swarm`, `/boost`, `/teamwork`), and enforces landing changes before killing `share`/`branch` workspaces.
4. `install/antigravity.sh` matches every safety invariant of `install/opencode.sh`, defaults to `$HOME/.gemini/config/skills`, and both installers exclude `.gemini` alongside `.opencode`/`.claude`/`.agents`.
5. All documentation links, dual-harness commands, CI policy checks, and negative test fixtures pass `make check` and `make links`.

Approval: Approved by repository owner request (2026-11-27, Milestone #10).

## Baseline

- Base commit on `main`: `66b9c9d` (`v1.3.0` verified immutable release).
- Baseline `make check`: PASS (11 skills validated, Ruff 0 errors, markdownlint 0 issues across 40 files, pytest 326 passed in 11.70 s, ShellCheck PASS, installer dry-run PASS, csstree PASS, 7 workflows PASS).
- `agy --version`: `1.5.18`. Empirical `agy plugin validate --json` confirmed that Title Case `name` triggers a loader warning (`name "..." doesn't match its folder "..."`), whereas lowercase kebab-case `name` matching the directory passes with 0 warnings/errors.

## File map

- Modify: `scripts/validate.py` — strict `name == skill_dir.name`, `compatibility` ≤ 500 chars, `allowed-tools`, retain OpenCode V2 `metadata.opencode/autoinvoke` check, validate both installers.
- Modify: `skills/*/SKILL.md` (11 files) — kebab-case `name`, unified `compatibility: agentskills`, Antigravity native orchestration/tooling, zero OpenCode-only text.
- Create: `docs/antigravity-orchestration.md` — native Antigravity orchestration architecture (alongside existing `docs/opencode-orchestration.md`).
- Create: `install/antigravity.sh` — global Antigravity installer (`$HOME/.gemini/config/skills`); update `install/opencode.sh` to exclude `.gemini` as well.
- Modify: `Makefile`, `.gitignore` — dual-installer ShellCheck/dry-run/install targets and `.gemini/` ignore rule.
- Modify: `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, `docs/antigravity-orchestration.md`, `docs/release-process.md`, `CHANGELOG.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/PULL_REQUEST_TEMPLATE.md` — dual-harness Antigravity + OpenCode documentation and templates.
- Create / Modify: `docs/plans/2026-11-27-antigravity-support.md`, `docs/plan.md` — Stage 10 plan and tracker registry.
- Modify: `tests/test_validation.py`, `tests/test_skill_suite.py`, `tests/test_installer.py`, `tests/test_release_assets.py`, `tests/test_secrets.py` — full dual-harness and negative test coverage.

## Tasks

### AGY-01 (#99) — Align skill frontmatter and validator with Antigravity & Agent Skills standard

Files:

- Modify: `scripts/validate.py`, all 11 `skills/*/SKILL.md` (frontmatter), `tests/test_validation.py`

Interfaces:

- Produces: strict `name == skill_dir.name`, `compatibility` (≤ 500 chars), optional `disable-model-invocation`, `metadata` (with OpenCode V2 `opencode/autoinvoke` preserved), `allowed-tools` contract in `scripts/validate.py`.

Verification:

- `python3 -m pytest -q tests/test_validation.py`
- `python3 scripts/validate.py`

### AGY-02 (#100) — Unify all 11 skills and add native Antigravity orchestration

Depends on: AGY-01

Files:

- Modify: all 11 `skills/*/SKILL.md`
- Create: `docs/antigravity-orchestration.md` (keeping `docs/opencode-orchestration.md`)
- Modify: `tests/test_skill_suite.py`

Interfaces:

- Consumes: AGY-01 frontmatter rules.
- Produces: unified Agent Skills-compliant skill suite with native Antigravity orchestration and `docs/antigravity-orchestration.md`, plus automated regression guards rejecting OpenCode-only runtime wording inside `skills/`.

Verification:

- `python3 -m pytest -q tests/test_skill_suite.py`
- `make check`

### AGY-03 (#101) — Add `install/antigravity.sh` alongside `install/opencode.sh` and update tooling & secret hygiene

Depends on: AGY-01, AGY-02

Files:

- Create: `install/antigravity.sh`
- Modify: `install/opencode.sh` (add `.gemini` secret exclusion), `Makefile`, `scripts/validate.py`, `.gitignore`, `tests/test_installer.py`, `tests/test_release_assets.py`, `tests/test_secrets.py`

Interfaces:

- Produces: `install/antigravity.sh` defaulting to `$HOME/.gemini/config/skills` with full parity alongside `install/opencode.sh`.

Verification:

- `shellcheck -x install/antigravity.sh install/opencode.sh install/lib.sh`
- `python3 -m pytest -q tests/test_installer.py tests/test_release_assets.py tests/test_secrets.py`
- `make check`

### AGY-04 (#102) — Update repository documentation, templates, `AGENTS.md`, and changelog for Antigravity + OpenCode

Depends on: AGY-02, AGY-03

Files:

- Modify: `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md`, `docs/antigravity-orchestration.md`, `docs/release-process.md`, `CHANGELOG.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/PULL_REQUEST_TEMPLATE.md`

Verification:

- `python3 scripts/validate.py`
- `make check`
- `make links`

### AGY-05 (#103) — Record support plan, verify end-to-end with Antigravity tooling, and close Milestone 10

Depends on: AGY-01, AGY-02, AGY-03, AGY-04

Files:

- Create/Modify: `docs/plans/2026-11-27-antigravity-support.md`, `docs/plan.md`

Verification:

- Empirical `agy plugin validate --json` check against a temporary staging bundle containing all 11 `skills/`
- `make check` and `make links`
- All Stage 10 PRs squash-merged into `main` with required CI green; issues #99–#103 and Milestone #10 closed.

## Delivery waves

- **PR 1 (`feat/antigravity-skills-and-validator`)**: `AGY-01` (#99) + `AGY-02` (#100) + initial plan file.
- **PR 2 (`feat/antigravity-installer`)**: `AGY-03` (#101).
- **PR 3 (`docs/antigravity-support-closeout`)**: `AGY-04` (#102) + `AGY-05` (#103).

## Risks and rollback

- Risk: Changing `name` from Title Case to lowercase kebab-case could affect trigger tests or reading-set sizes. Mitigation: verify `tests/test_skill_suite.py` cross-skill routing and `scripts/validate.py` byte limits before merging.
- Risk: Diverging safety logic between `install/antigravity.sh` and `install/opencode.sh`. Mitigation: parametrize `tests/test_installer.py` across both installers so every safety guard is verified on both scripts.
- Risk: External links to `antigravity.google/docs/*` or `agentskills.io` could fail in `make links`. Mitigation: run `make links` before merging PR 3.

## Execution ledger

| Task | Issue | Base | Status | Evidence | Ruling | Next |
|---|---|---|---|---|---|---|
| AGY-01 | #99 | `66b9c9d` | done | Merged in PR #104 (`67c14fa`); `make check` PASS (340 tests); `agy plugin validate` 11/11 skills, 0 errors/warnings; independent `readonly-reviewer` PASS | Preserve OpenCode V2 `metadata.opencode/autoinvoke` check in `validate.py`; enforce `dict[str, str]` on other `metadata` keys; use unified `compatibility: agentskills` | AGY-02 |
| AGY-02 | #100 | `66b9c9d` | done | Merged in PR #104 (`67c14fa`); 0 OpenCode refs across `skills/**/*.md`; `docs/antigravity-orchestration.md` added alongside `docs/opencode-orchestration.md` | Document `EnableWriteTools: false` no-shell fallback in `orchestration`/`code-review`; align `branch`/`share` wording with live `agy 1.5.18` schema and docs | AGY-03 |
| AGY-03 | #101 | `67c14fa` | done | Merged in PR #105 (`f6277cc`); `make check` PASS (343 tests, `shellcheck -x` on all 3 scripts, both dry-runs); independent `readonly-reviewer` 0 P0/P1 + P2-1..P2-3 fixed | Factor shared core into `install/lib.sh` with non-symlink guard; target `$HOME/.gemini/config/skills` ignoring `XDG_CONFIG_HOME`; reject symlinked `install/` dir | AGY-04 |
| AGY-04 | #102 | `f6277cc` | in_progress | PR #106 (`make check` PASS: 343 tests, 42 md files, `shellcheck -x`, both dry-runs; `curl` HTTP 200 on all 3 new URLs; `make links` `NOT_TESTED` locally due to `198.18.0.0/15` fake-IP SSRF guard; independent `readonly-reviewer` 1 P1 + 3 P2 addressed) | Document both Antigravity and OpenCode as Ready; note `install/antigravity.sh` ships after `v1.3.0`; keep released CHANGELOG versions immutable | AGY-05 |
| AGY-05 | #103 | `f6277cc` | in_progress | PR #106 (`make check` PASS; empirical `agy plugin validate --json` 11/11 skills, 0 errors/warnings; `make links` `NOT_TESTED` locally with `curl` HTTP 200 substitute; awaiting PR #106 CI + squash merge to close Milestone #10) | Do not cut release tag without explicit owner authorization | Close Milestone #10 |
