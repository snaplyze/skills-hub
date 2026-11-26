# Repository settings evidence

Verified 2026-11-26 from the GitHub API and repository files. Recheck after any
settings change; this file records the state, not a claim that a setting cannot
regress.

## Branch and tag protection

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Default branch | `main` | Repository settings | Maintainer |
| Main ruleset | `main-protection` (#27259237), active | Rulesets API | Maintainer |
| Pull requests | Required; 0 approving reviews; extra approval for unattributed changes; conversation resolution required | Ruleset `main-protection` | Maintainer |
| Merge method | Squash only; linear history required | Ruleset and repository settings | Maintainer |
| Required checks | `validate`, `Analyze (python)`, `Analyze (actions)`, `dependency-review`, `gitleaks`; strict up-to-date policy | Ruleset `main-protection` | Maintainer |
| Code scanning | CodeQL required; errors and high/critical security alerts block | Ruleset `main-protection` | Maintainer |
| Force push / deletion | Blocked | Ruleset `main-protection` | Maintainer |
| Tag ruleset | `tag-protection` (#27259245), active; blocks creation, deletion, non-fast-forward; requires signatures; owner-only creation via configured bypass; bypass does not bypass release workflow signature/ancestry/check-run gates | Tag ruleset | Maintainer |
| Tag creation | Gated by the tag ruleset with owner bypass; signatures required | Tag ruleset | Maintainer |
| CODEOWNERS | Advisory only; the ruleset does not require code-owner review | `.github/CODEOWNERS` | Maintainer |
| Environments | `release` exists; required reviewer `snaplyze`; deployment policy allows `main`; self-review allowed by solo exception; admin bypass disabled | Actions environments | Maintainer |

## Actions and runners

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Allowed actions | Selected; GitHub-owned and verified actions; `ossf/scorecard-action@*` exception | Actions policy | Maintainer |
| Action pinning | Full commit SHA required | Actions policy | Maintainer |
| Default workflow token | Read-only | Actions policy | Maintainer |
| Fork pull requests | Approval required for all external contributors | Actions policy | Maintainer |
| Self-hosted runners | None | Actions runners API | Owner decision required |
| CodeQL | Runs on `main` and pull requests; Python and GitHub Actions | `.github/workflows/codeql.yml` | Maintainer |
| Scorecard | Weekly, on push, and on `branch_protection_rule`; ruleset changes are covered by the weekly run; SARIF uploaded to code scanning | `.github/workflows/scorecard.yml` | Maintainer |

The repository has no self-hosted runners. If one is added, route only jobs
that match its labels, OS, architecture, and capabilities; never run untrusted
fork code on it, and keep fork approval enabled.

## Security features

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Secret scanning | Enabled | Security settings | Maintainer |
| Push protection | Enabled | Security settings | Maintainer |
| Non-provider patterns | Disabled; API did not enable on this personal public repository | Security settings | Owner decision required |
| Validity checks | Disabled; API did not enable on this personal public repository | Security settings | Owner decision required |
| Dependabot alerts/updates | Enabled | Security settings | Maintainer |
| Private vulnerability reporting | Enabled | Security settings | Maintainer |
| Immutable releases | Enabled | Releases settings | Maintainer |
| Release tag signatures | Required by ruleset; trust variable `RELEASE_TAG_ALLOWED_SIGNERS` is set; `v1.1.0`, `v1.2.0`, and `v1.3.0` signed/immutable; `v1.0.0`/`v1.0.1` predate the rule | Tag ruleset and repository variables | Maintainer |

## Claim-to-evidence map

- `README.md` and `GOVERNANCE.md` describe main protection, required checks,
  squash-only history, and tag deletion protection: rulesets #27259237 and
  #27259245.
- `SECURITY.md` describes secret scanning, push protection, Dependabot,
  CodeQL, Scorecard, fork approval, and read-only Actions defaults: the
  settings above.
- `AGENTS.md` records the owner CI decision: hosted by default; self-hosted
  only for suitable jobs.

## Owner actions that cannot be completed from repository code

1. Non-provider secret scanning patterns and validity checks remain disabled;
   the personal public repository API did not enable them.
2. When a second regular maintainer joins, raise the main ruleset approval
   count to 1 and require code-owner review.
3. When a second reviewer joins, add them to the `release` environment and set
   `prevent_self_review` to true; do not use a second account only to satisfy
   the gate.
4. If self-hosted runners are added, configure labels/OS/architecture, enable
   fork approval for those jobs, and keep untrusted code on hosted runners.
5. Rotate the SSH release signing key and update
   `RELEASE_TAG_ALLOWED_SIGNERS` before the current key is retired.
