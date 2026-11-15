# Repository settings evidence

Verified 2026-11-15 from the GitHub API and repository files. Recheck after any
settings change; this file records the state, not a claim that a setting cannot
regress.

## Branch and tag protection

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Default branch | `main` | Repository settings | Maintainer |
| Main ruleset | `main-protection` (#27259237), active | Rulesets API | Maintainer |
| Pull requests | Required; 0 approving reviews; extra approval for unattributed changes; conversation resolution required | Ruleset `main-protection` | Maintainer |
| Merge method | Squash only; linear history required | Ruleset and repository settings | Maintainer |
| Required checks | `validate`, `Analyze (python)`, `dependency-review`; strict up-to-date policy | Ruleset `main-protection` | Maintainer |
| Code scanning | CodeQL required; errors and high/critical security alerts block | Ruleset `main-protection` | Maintainer |
| Force push / deletion | Blocked | Ruleset `main-protection` | Maintainer |
| Tag ruleset | `tag-protection` (#27259245), active; blocks deletion and non-fast-forward only | Tag ruleset | Maintainer |
| Tag creation | Not gated; no required signatures | Tag ruleset | Owner decision required |
| CODEOWNERS | Advisory only; the ruleset does not require code-owner review | `.github/CODEOWNERS` | Maintainer |
| Environments | None configured; `release.yml` references a `release` environment, so the owner must create and protect it | Actions environments | Owner decision required |

## Actions and runners

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Allowed actions | Selected; GitHub-owned and verified actions; `ossf/scorecard-action@*` exception | Actions policy | Maintainer |
| Action pinning | Full commit SHA required | Actions policy | Maintainer |
| Default workflow token | Read-only | Actions policy | Maintainer |
| Fork pull requests | Approval required for all external contributors | Actions policy | Maintainer |
| Self-hosted runners | None | Actions runners API | Owner decision required |
| CodeQL | Runs on `main` and pull requests; Python only | `.github/workflows/codeql.yml` | Maintainer |
| Scorecard | Weekly, on push, and on `branch_protection_rule`; ruleset changes are covered by the weekly run; SARIF uploaded to code scanning | `.github/workflows/scorecard.yml` | Maintainer |

The repository has no self-hosted runners. If one is added, route only jobs
that match its labels, OS, architecture, and capabilities; never run untrusted
fork code on it, and keep fork approval enabled.

## Security features

| Setting | Current state | Where | Owner |
|---|---|---|---|
| Secret scanning | Enabled | Security settings | Maintainer |
| Push protection | Enabled | Security settings | Maintainer |
| Non-provider patterns | Disabled | Security settings | Owner decision required |
| Validity checks | Disabled | Security settings | Owner decision required |
| Dependabot alerts/updates | Enabled | Security settings | Maintainer |
| Private vulnerability reporting | Enabled | Security settings | Maintainer |
| Immutable releases | Disabled | Releases settings | Owner decision required |
| Release tag signatures | `v1.0.0` and `v1.0.1` are unsigned | Git tags | Owner decision required |

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

1. Create and protect a `release` environment with required reviewers.
2. Add a trusted release signing key/public key and sign new `v*` tags; configure
   the release workflow secret/public-key path so `git tag -v` succeeds.
3. Enable immutable releases in repository settings.
4. Enable non-provider secret scanning patterns and validity checks if the
   plan's privacy/cost constraints allow.
5. When a second regular maintainer joins, raise the ruleset approval count to
   1 and enable code-owner review and required signatures.
6. If self-hosted runners are added, configure labels/OS/architecture, enable
   fork approval for those jobs, and keep untrusted code on hosted runners.
