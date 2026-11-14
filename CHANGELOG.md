# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add `AGENTS.md` with project information for agents and a skills table in
  the README.

### Changed

- Use the public clone URL in the README.
- Audit the project and add `docs/plan.md` with prioritized remediation tasks.
- Clarify that Dependency Review still has a workflow-level `pull-requests:
  write`; moving it to job scope is tracked in `docs/plan.md` (AUD-20).
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
