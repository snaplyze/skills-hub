# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add a native `orchestration` skill that routes complex work over `explore`/`general` subagents without a plugin, hooks, or background scheduler.
- Add a compact OpenCode workflow skill suite: specification, implementation
  planning, autonomous execution, systematic debugging, TDD, code review,
  delivery, clean code, and skill authoring. The skills are portable Markdown
  with no hooks or plugin bootstrap.

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
