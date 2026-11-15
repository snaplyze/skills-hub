# Governance

## Maintainer model

Skills Hub is currently maintained by **[@snaplyze](https://github.com/snaplyze)**.
The maintainer has final responsibility for scope, releases, and repository
security.

The project aims for a small, high-signal collection. A skill is accepted when
it is distinct, well-scoped, tested, and maintainable. More skills are not
automatically better.

## Decisions

- Small changes: open a pull request and use lazy consensus.
- New skills or breaking changes: open an issue or discussion first.
- If consensus is unclear, the maintainer decides and records the rationale in
  the issue or pull request.
- Security decisions follow [SECURITY.md](SECURITY.md) and may be handled
  privately until disclosure is safe.

## Review and merge policy

`main` is protected by a repository ruleset:

- pull requests are required;
- required status checks must pass;
- conversations must be resolved;
- history must be linear;
- force pushes and deletions are blocked;
- CodeQL code scanning must not report error-level or high/critical security
  alerts.

Squash merge is the only enabled merge method. Branches are deleted after merge.

The required approval count is currently **0** so a solo maintainer can merge
their own pull requests. Extra approval for unattributed changes is enabled;
CODEOWNERS is advisory until a second regular maintainer joins. At that point,
raise the approval count to 1, enable code-owner review, and require signed
commits/tags. Do not bypass the ruleset for routine work.

The current settings, their source, the verification date, and owner-only
actions are recorded in [`docs/repository-settings.md`](docs/repository-settings.md).

## Becoming a maintainer

A contributor may be invited after a sustained record of high-quality,
well-reviewed contributions and good community judgment. Maintainer access is
granted by the current maintainer and reviewed periodically.

## Releases

- Versions follow [Semantic Versioning](https://semver.org/).
- User-facing changes are recorded in [CHANGELOG.md](CHANGELOG.md).
- Releases are tagged `vX.Y.Z` from `main`.
- The release workflow fails closed unless the tag is signed, its commit is an
  ancestor of `main`, and the required checks passed. It creates a draft
  release; promotion is a manual step.
- `CHANGELOG.md` is the single source of release notes. The workflow extracts
  the matching version section and fails if it is missing.
- Tag protection blocks deletion and force updates. Tag signing, immutable
  releases, and the protected `release` environment are owner-only setup
  actions recorded in [`docs/repository-settings.md`](docs/repository-settings.md).

## Changes to governance

Changes to this document require a pull request and maintainer approval. The
current maintainer may make emergency security changes first and document them
afterward.
