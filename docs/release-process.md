# Release process

This document is for maintainers. It describes the release gate in
[`.github/workflows/release.yml`](../.github/workflows/release.yml), the
settings the owner must configure outside the repository, and the residual
risks the workflow cannot remove.

The workflow does not create tags or publish releases. It is dispatched from
`main` with a signed tag as input, then creates a **draft** release with a
source archive, a SHA-256 checksum, and a build provenance attestation.
Promotion is a manual owner action. Dispatching from `main` avoids running
workflow code from the untrusted tag before the tag is verified.

## Preconditions

A release can proceed only when all of these are true:

- The workflow is dispatched from a reviewed `main`; write collaborators are
  trusted not to dispatch a modified workflow from a branch.

- The dispatched tag matches `vX.Y.Z`, with an optional SemVer prerelease suffix
  such as `v1.2.3-rc.1`.
- `CHANGELOG.md` contains exactly one non-empty `## [X.Y.Z]` section for the
  tag. For a prerelease, use the exact version in the heading, for example
  `## [1.2.3-rc.1]`.
- The tag is annotated and signed, and its signature verifies against the
  owner-provided trust material.
- The tagged commit is an ancestor of `origin/main`.
- The required `validate` and `Analyze (python)` check-runs for that commit
  are completed successfully.
- The protected `release` environment approves the job.

Tags published before this gate (`v1.0.1` and earlier) are unsigned, have no
source-archive assets, and are not covered by these checks.

Any missing or failed condition stops the workflow before a release is
created. The workflow fails closed with an `::error::` message.

## Release checklist

1. Add user-facing changes under `## [Unreleased]` and open a pull request.
2. Before cutting the release, open a pull request that moves the entries into
   `## [X.Y.Z] - YYYY-MM-DD`, leaves an empty `## [Unreleased]`, and uses the
   same version as the future tag. Confirm that `skills/` contains every skill
   listed in the README and that the current-HEAD archive test passes. Merge it.
3. Wait for `validate` and `Analyze (python)` on `main`, and for
   `dependency-review` on the pull request. Do not bypass branch protection.
4. From a clean `main` checkout, create a signed annotated tag:

   ```bash
   git switch main
   git pull --ff-only
   git tag -s v1.2.3 -m "skills-hub v1.2.3"
   git tag -v v1.2.3
   git push origin v1.2.3
   ```

5. Approve the `release` environment deployment in the Actions run.
6. Inspect the draft release: `release-notes.md` content, the source archive,
   `SHA256SUMS`, and the provenance attestation.
7. Promote the draft manually after review. Do not publish a failed or
   incomplete draft.

For a prerelease, use a tag such as `v1.2.3-rc.1` and the matching changelog
heading. The workflow passes `--prerelease --latest=false`; stable drafts leave
latest selection to the publication step.

## Owner setup

The following settings are repository or environment settings. The workflow
cannot create, verify, or enforce them, and no change to them is made by this
document.

### Protected `release` environment

Create an environment named `release` and add protection rules:

- require reviewers, and prefer reviewers other than the person who pushed the
  tag;
- allow deployments from `main` (the workflow is dispatched from `main`); add `v*` only if you also use tag-based deployment;
- do not allow administrators to bypass the protection.

The workflow references `environment: release`. If the environment does not
exist, GitHub can run the job without the intended approval gate, so create it
before the first release.

Solo-maintainer exception: the current environment has one reviewer and
`prevent_self_review` is false. This is accepted only because no second
reviewer exists; the signed tag, required checks, changelog notes, draft review,
checksums, provenance, and immutable release are compensating controls. When a
second maintainer joins, add that person as a reviewer and set
`prevent_self_review` to true before the next release. Do not use a second
account merely to satisfy the approval gate.

### Tag ruleset

Keep a ruleset for `v*` tags that blocks deletion and force updates, and, where
the available rule set supports it, restricts tag creation to maintainers and
requires signed tags. The workflow independently verifies the tag signature
with `git verify-tag`, so missing tag-rule support does not make an unsigned tag
publishable.

The current `tag-protection` ruleset restricts creation to the repository owner
through its configured bypass actor. That bypass only allows the owner to create
a tag; it does not bypass signature verification, main ancestry, required
check-runs, the protected environment, or immutable-release controls. Keep the
owner-only creation rule while there is one release manager; when a second
release manager joins, replace the bypass with a non-bypass release role.

Tag creation itself is not the release trigger. A maintainer who can push a tag
can provide it as the workflow input; the signature, ancestry, and check-run
checks still apply, and the immutable setting is owner-verified.

### Tag signature trust

Choose one trust source and configure it as a repository/environment variable
or, for multi-line values, a repository/environment secret with the same name.
These values are public material, never private keys. The workflow reads the
variable first and falls back to the secret.

| Variable or secret | Use |
|---|---|
| `RELEASE_TAG_GPG_PUBLIC_KEY` | ASCII-armored OpenPGP public key used to verify OpenPGP-signed tags |
| `RELEASE_TAG_ALLOWED_SIGNERS` | An SSH allowed-signers file used to verify SSH-signed tags |

Set only one. The workflow imports the OpenPGP key into a temporary
`GNUPGHOME`, or writes the allowed-signers file to a temporary path, and runs
`git verify-tag`. The allowed-signers file must contain the principal used for
the tag. The public copy is
[`docs/release-signing/allowed_signers`](release-signing/allowed_signers); its
rotation is documented in
[`docs/release-signing/README.md`](release-signing/README.md). A lightweight
tag, an unsigned annotated tag, a signature from an unknown key, or both
variables being set fails the job.

Create the tag with the matching local configuration, for example:

```bash
# OpenPGP
git config user.signingkey <fingerprint>
git tag -s v1.2.3 -m "skills-hub v1.2.3"

# SSH signature
git config gpg.format ssh
git config user.signingkey ~/.ssh/id_ed25519.pub
git tag -s v1.2.3 -m "skills-hub v1.2.3"
```

Rotate the variable when the signing key changes.

### Immutable releases

Enable GitHub's immutable releases setting before the first release. This
prevents assets from being replaced after publication. The workflow's
`GITHUB_TOKEN` cannot read the admin-only immutable-releases endpoint, so the
owner must verify the setting with an admin token and record it in
`docs/repository-settings.md` before dispatching. The draft review and checksum
are additional controls, not substitutes.

### Actions allowlist and permissions

The workflow pins every action to a full commit SHA. It uses:

- `actions/checkout` to fetch full history;
- `actions/attest-build-provenance` to create the provenance attestation.

`actions/attest-build-provenance` is a GitHub-owned action. Keep the repository
Actions allowlist and the Scorecard allowlist consistent with it. The release
job requests `contents: write`, `checks: read`, `id-token: write`, and
`attestations: write`; the top-level workflow permission remains
`contents: read`. Do not move write permissions to workflow scope.

### Main protection

The release gate depends on the existing protection of `main`: pull requests,
required checks, linear history, and blocked force pushes and deletions. Do not
weaken those rules to make a release pass. A release from a commit that is not
an ancestor of `origin/main` fails even if the tag itself is valid.

## What the workflow checks

1. `scripts/release_notes.py` validates the tag and extracts the matching
   changelog section. The workflow passes the result to
   `gh release create --notes-file`. `CHANGELOG.md` is the only release-notes
   source; generated release notes and label-based notes are not used. The
   former `.github/release.yml` label configuration has been removed.
2. The tag object must be annotated, and the signature must verify against the
   configured trust source.
3. The tag commit must be an ancestor of a freshly fetched `origin/main`.
4. The latest `validate` and `Analyze (python)` check-runs for the exact commit
   must be completed with conclusion `success` and must have been created by
   GitHub Actions.
5. `git archive` creates `skills-hub-<tag>.tar.gz`; `SHA256SUMS` contains its
   SHA-256 digest.
6. `actions/attest-build-provenance` attests the archive.
7. `gh release create` creates a draft with the archive, `SHA256SUMS`, and the
   extracted notes. It uses `--prerelease --latest=false` for a prerelease;
   stable drafts leave latest selection to the publication step.

## Verifying a release

Download all assets from the release into one directory:

```bash
VERSION=v1.2.3
gh release download "$VERSION" --repo snaplyze/skills-hub \
  --pattern 'skills-hub-*.tar.gz' --pattern 'SHA256SUMS'
sha256sum -c SHA256SUMS
gh attestation verify "skills-hub-${VERSION}.tar.gz" --repo snaplyze/skills-hub
```

The archive install is checksum-verified but has no `.git` directory, so the
installer's `--verify` mode cannot inspect it. For a clean tag checkout (verify
the signature separately), clone the signed tag and use `--verify --ref`:

```bash
git clone --branch "$VERSION" --depth 1 \
  https://github.com/snaplyze/skills-hub.git
cd skills-hub
git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile=docs/release-signing/allowed_signers \
  verify-tag "$VERSION"
./install/opencode.sh --verify --ref "$VERSION"
```

## Manual promotion and residual risks

- The release is a draft. A maintainer must review it and publish it manually;
  the workflow cannot enforce that a human inspects the assets.
- The `release` environment, tag ruleset, immutable-release setting, and
  Actions allowlist are external settings. They are not stored in Git and can
  drift. Review them when release controls change.
- Tag signatures depend on the configured public key or allowed-signers file.
  An incorrect or stale variable blocks releases; that is fail-closed by
  design.
- Provenance attestations require `actions/attest-build-provenance` to be
  allowed and attestations to be available for the repository. If they are
  not, the workflow fails before creating a draft.
- Required check-runs can expire under GitHub's retention limits. Very old
  commits may need a new check run before a release, which is intentional.
- A failed run can leave a draft release or an attestation behind. Delete the
  draft before re-running the tag workflow.
- The workflow uses the repository `GITHUB_TOKEN` scoped to the job and
  protected environment. It does not create tags, edit `main`, or change
  repository settings.
- A maintainer with repository administration access can still publish a
  release outside this workflow. Repository policy, review, and audit logs are
  the control for that case.
