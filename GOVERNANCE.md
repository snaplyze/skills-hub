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
their own pull requests. When a second regular maintainer joins, raise it to 1
and enable code-owner review. Do not bypass the ruleset for routine work.

## Becoming a maintainer

A contributor may be invited after a sustained record of high-quality,
well-reviewed contributions and good community judgment. Maintainer access is
granted by the current maintainer and reviewed periodically.

## Releases

- Versions follow [Semantic Versioning](https://semver.org/).
- User-facing changes are recorded in [CHANGELOG.md](CHANGELOG.md).
- Releases are tagged `vX.Y.Z` from `main`.
- Tag protection blocks deletion and force updates of release tags.
- Release notes are generated from the changelog categories and curated before
  publishing.

## Changes to governance

Changes to this document require a pull request and maintainer approval. The
current maintainer may make emergency security changes first and document them
afterward.
