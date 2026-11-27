# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- First-class **Google Antigravity** support (App, CLI `agy`, IDE, and IDE
  extensions) alongside OpenCode:
  - Global installer `install/antigravity.sh` targeting
    `$HOME/.gemini/config/skills` (shared across Antigravity App, CLI, and IDE)
    with full safety parity via shared `install/lib.sh`.
  - Native Antigravity orchestration guide (`docs/antigravity-orchestration.md`)
    covering `invoke_subagent`, `define_subagent`, `send_message`,
    `manage_subagents`, built-in `research`/`browser`/`self` subagents,
    `branch`/`share` workspace isolation, Dynamic Workflows (`run_workflow`),
    and user-invoked `/swarm`, `/boost`, and `/teamwork`.
  - Agent Skills open-standard frontmatter enforcement in `scripts/validate.py`
    (lowercase kebab-case `name` matching directory ID, `compatibility` ≤ 500
    chars, `allowed-tools`, and `dict[str, str]` `metadata` checks while
    preserving OpenCode V2 `metadata.opencode/autoinvoke` validation).

### Changed

- Unify all 11 skills under the Agent Skills open standard (`name` matching
  directory ID, `compatibility: agentskills`) and remove OpenCode-specific
  runtime descriptions from `skills/` so Antigravity and OpenCode interpret
  every skill consistently.
- Adapt `orchestration`, `autonomous-execution`, `code-review`, `delivery`,
  `skill-authoring`, `frontend-design`, and `systematic-debugging` for native
  Antigravity subagents, workflows, `/browser`, `/diff`, `/compact`, `/boost`,
  and headless `agy -p ... --output-format json`.
- Factor shared installer logic into `install/lib.sh`, update `Makefile` with
  `install-antigravity`, `install-opencode`, dual `shellcheck -x`, and dual
  `dry-run`, and update repository docs, `AGENTS.md`, and issue/PR templates
  for both Antigravity and OpenCode.

### Security

- Ignore `.gemini/` in `.gitignore` and exclude `.gemini` in both installers'
  copy mode; reject symlinked `install/` directories and installer scripts in
  `scripts/validate.py` and wrapper scripts.

## [1.3.0] - 2026-11-26

### Added

- OpenCode V2 frontmatter support (`metadata`, `disable-model-invocation`) and
  strict duplicate-key YAML parsing (`UniqueKeySafeLoader`) in
  `scripts/validate.py`, plus generalized `assets/reading-sets.json` support for
  any skill with `references/`.
- CodeQL `Analyze (actions)` workflow analysis alongside `Analyze (python)` and
  `gitleaks` in required `main` branch protection and release check-run gates.
- Sigstore provenance bundle release asset (`skills-hub-<tag>.tar.gz.sigstore.json`)
  for offline `gh attestation verify --bundle` verification.
- Light-theme contrast coverage for `--color-surface-raised` and mandatory
  both-theme (`light` + `dark`) semantic token coverage enforcement in
  `scripts/validate.py`.
- Deterministic SSH-signed tag and `.git`-independent archive fixtures across
  `tests/test_release_signature.py` and `tests/test_release_assets.py`.

### Changed

- Upgrade the 10-skill OpenCode workflow suite (`orchestration`,
  `specification`, `implementation-planning`, `autonomous-execution`,
  `systematic-debugging`, `test-driven-development`, `code-review`, `delivery`,
  `clean-code`, `skill-authoring`) and `docs/opencode-orchestration.md` for
  OpenCode V2 (`v2.4.1`) and Skill Suite v2: project-local `docs/plans/` files,
  unified ledgers/briefs, rulings, bounded review-fix loops, secret-safe diff
  checks, tests-first review, mutation checks, trigger mining, and separated
  cross-skill anti-triggers.
- Update `frontend-design` for Baseline 2026 CSS (`:user-invalid`, `@supports`
  for `animation-timeline: view()`, `<dialog>` `display allow-discrete`),
  Next.js 16 `preload` and React Compiler v1.0, W3C DTCG handoff, verified
  upstream licenses (`Leonxlnx/taste-skill` MIT, WCAG 2.2 = ISO/IEC 40500:2025,
  WAI-ARIA 1.3), and restore `new-page` reading-budget headroom (`31,411 / 32,768 B`).
- Speed up `scripts/validate.py` (`190 -> 73 ms` in-process via single-pass
  parsing and in-process contrast checks), `pytest` (`23.7 -> 9.8 s`, CI
  `validate` `61 -> 20-30 s` by excluding `node_modules` copies and reducing
  subprocess fan-out), `install/opencode.sh` (streaming `tar` scaling), and
  `scripts/check_external_links.py` (pruned `os.walk` + bounded per-host
  concurrency).
- Update pinned development dependencies (`PyYAML 6.0.4`, `ruff 0.17.6`,
  `markdownlint-cli2 0.24.2`) and GitHub Actions (`codeql-action v4.39.5`,
  `dependency-review-action v5.0.1`, `scorecard-action v2.6.0`), drop no-op
  CodeQL `autobuild`, add workflow-skills area to `bug_report.yml`, add
  `#.venv`/`#.playwright-cli` markdownlint exclusions, document OpenCode V2
  discovery/`skills[]`/`permission.skill` in `README.md`, and remove local
  private environment details from public `AGENTS.md`.

### Fixed

- Fix `install/opencode.sh` YAML description parsing for `--list`, reject
  symlinks inside skill trees, harden `--verify` against `.gitignore`d files via
  `git archive`, add pre-flight validation, and document `opencode reload`.
- Fix `skills/frontend-design/scripts/contrast.py` hex/RGB/HSL/non-finite
  parsing bugs and CSS Color 4 angle/unitless support, plus string-aware CSS
  declaration parsing in `scripts/validate.py`.
- Fix workflow-test and skill-suite test fragility with structural YAML/TOML
  and inline-comment-aware shell assertions, wrap-independent ledger checks, and
  cross-skill trigger isolation covering all 11 skills.

### Security

- Resolve Code Scanning alert #13 in `.github/workflows/ci.yml` and harden
  `scripts/check_workflows.py` and `.github/workflows/scorecard.yml`.
- Harden `.github/workflows/release.yml`, `scripts/release_checks.py`, and
  `scripts/release_notes.py`: checkout tags via `refs/tags/...`, execute
  `gate/scripts/release_notes.py` from `main`, verify `RELEASE_TAG_ALLOWED_SIGNERS`
  parity with `gate/docs/release-signing/allowed_signers`, require `gitleaks`
  and `Analyze (actions)` check-runs, and fail closed on timeouts/errors.
- Harden `scripts/check_external_links.py` with strict `http`/`https`-only
  openers, non-global IP/DNS-rebinding socket pinning, bounded redirects without
  unbounded body reads, and `--allow-local` opt-in for loopback testing.
- Enforce path/symlink containment, CommonMark/GFM link extraction, and
  `docs/**` link coverage in `scripts/validate.py`.

## [1.2.0] - 2026-11-15

### Added

- Add a native `orchestration` skill that routes complex work over
  `explore`/`general` subagents without a plugin, hooks, or background
  scheduler.
- Add a compact OpenCode workflow skill suite: specification, implementation
  planning, autonomous execution, systematic debugging, TDD, code review,
  delivery, clean code, and skill authoring. The skills are portable Markdown
  with no hooks or plugin bootstrap.
- Publish the public release-signing trust file and exact tag-verification
  commands.
- Add archive coverage for every skill in the current release tree.

### Changed

- Harden the skill contract tests with trigger matrices, workflow-content
  mutation, documentation path/count guards, and simple-skill validation
  coverage.
- Hand off approved implementation plans from `orchestration` to
  `autonomous-execution`.
- Use one module-scoped server for external-link tests.
- Run required CI with full history and tags so release-signature checks are
  mandatory.
- Compact the plan registry and sync the open audit tasks with the tracker.

## [1.1.0] - 2026-11-15

### Added

- Add `AGENTS.md` with project information for agents and a skills table in
  the README.
- Add a negative-test suite for the validator and contrast CLI, an explicit
  reading-set budget manifest, and deterministic external-link audit.
- Add `scripts/release_notes.py`, release-gate tests, and installer safety
  tests.
- Add a checksum-verified `Secret Scan` workflow and a scheduled Link Audit.
- Add `docs/release-process.md` and `docs/repository-settings.md` with release
  controls, settings evidence, and owner-only actions.
- Add the deterministic `katex` security override and a real release-archive
  checksum test.

### Changed

- Make the OpenCode installer copy by default, add `--verify`/`--ref`, safe
  target canonicalization, atomic installs, backups, and artifact exclusions.
- Gate releases on signed tags, ancestry, required check-runs, changelog
  notes, a protected environment, draft promotion, checksums, and provenance.
- Use hash-locked Python/npm toolchains, Python 3.12, pinned runners, one
  `make check` entry point, and job-scoped Dependency Review permissions.
- Split and trim the frontend-design instruction set into a verified 32 KiB
  reading budget; align references with the starter tokens and canonical
  templates.
- Canonicalize skill attribution in `references/sources.md`; make the root
  notices a pointer.
- Fix AA contrast for semantic text/subtle/accent/border combinations and
  add fixture coverage for every semantic token.
- Use the public clone URL in the README.
- Audit the project and add `docs/plan.md` with prioritized remediation tasks.
- Move Dependency Review's `pull-requests: write` permission to job scope
  (AUD-20).
- Correct README, CONTRIBUTING, and GOVERNANCE claims about local versus CI
  checks, repository layout, prerequisites, and release-note generation.
- Restrict GitHub Actions to GitHub-owned and verified actions with an explicit
  Scorecard allowlist, and require approval for all external fork workflows.
- Document the pinned-action, least-privilege, and allowlist requirements in
  the contribution guide.

## [1.0.1] - 2026-11-14

### Changed

- Moved GitHub Actions write permissions to job scope and kept Scorecard
  results in the OpenSSF dashboard instead of code scanning.
- Added direct links to private vulnerability reporting in the README and
  security policy.

## [1.0.0] - 2026-11-14

### Added

- `frontend-design` skill for OpenCode:
  - subject-grounded visual direction and anti-generic design guidance;
  - design systems, tokens, themes, component contracts, and handoff;
  - UX flows, forms, feedback states, navigation, and research-lite methods;
  - WCAG 2.2 AA accessibility guidance and testing protocol;
  - responsive, mobile, touch, and safe-area patterns;
  - motion design, performance, and reduced-motion guidance;
  - modern CSS, React/Next.js, Tailwind, and implementation guidance;
  - pre-delivery quality gates and severity-based audit templates.
- Dependency-free WCAG contrast checker with alpha compositing, JSON output,
  and CI exit codes.
- Starter light/dark token sheet with 64 audited contrast pairs.
- Design brief, audit report, and token fixtures.
- OpenCode global installer with symlink/copy modes, dry-run, force, and target
  overrides.
- Repository validation, CI, CodeQL, dependency review, and OpenSSF Scorecard
  workflows.
- Contribution guide, code of conduct, security policy, governance, issue
  templates, and pull request template.
