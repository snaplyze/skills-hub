# Skills Hub

[![CI](https://github.com/snaplyze/skills-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/snaplyze/skills-hub/actions/workflows/ci.yml)
[![CodeQL](https://github.com/snaplyze/skills-hub/actions/workflows/codeql.yml/badge.svg)](https://github.com/snaplyze/skills-hub/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/snaplyze/skills-hub/badge)](https://securityscorecards.dev/viewer/?uri=github.com/snaplyze/skills-hub)
[![Release](https://img.shields.io/github/v/release/snaplyze/skills-hub)](https://github.com/snaplyze/skills-hub/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenCode](https://img.shields.io/badge/OpenCode-ready-0f766e)](https://opencode.ai/)

Portable, high-craft skills for AI coding agents. Each skill is a self-contained directory with a `SKILL.md`, optional references, assets, and deterministic scripts. Install it globally into the agent you use; keep it versioned here.

The first skill is **Frontend Design** for **OpenCode**. Support for Claude Code, Codex, and other harnesses will follow without rewriting the skill content.

## Status

| Harness | Status | Installer |
|---|---|---|
| [OpenCode](https://opencode.ai/) | Ready | `install/opencode.sh` |
| Claude Code | Planned | — |
| Codex | Planned | — |
| Other agents | Planned | — |

## Skills

| Skill | Purpose | Harness |
|---|---|---|
| [`frontend-design`](skills/frontend-design/SKILL.md) | Distinctive, accessible web interface design and frontend quality | OpenCode |

### `frontend-design`

A complete design and frontend-quality skill for building, redesigning, and reviewing web interfaces. It combines aesthetic direction with design systems, UX states, accessibility, responsive behavior, motion, implementation guidance, and a pre-delivery audit.

Use it when you want:

- a page, component, or design system that does not look templated;
- typography, color, spacing, and layout decisions with a rationale;
- mobile, touch, dark-mode, and responsive behavior that actually works;
- accessible forms, navigation, dialogs, and states;
- a UI review with severity-ranked findings and concrete fixes;
- a visual direction grounded in the subject, not a generic SaaS template.

It is deliberately opinionated about craft and deliberately neutral about style. The brief and the existing product outrank its defaults.

## Install

### OpenCode

The installer copies skills into `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` by default. Copy mode snapshots content and never writes into this checkout. Use `--link` only when you want a live link to the clone. It requires Bash and GNU `realpath -m`; on systems without that command, use the minimal manual copy below.

New releases use signed `vX.Y.Z` tags. Tags published before the release gate
(`v1.0.1` and earlier) are unsigned and have no source-archive assets; do not
treat them as signed releases. Owner setup for the protected `release`
environment, tag-signature trust, and immutable releases is documented in
[docs/release-process.md](docs/release-process.md).

#### Install from a release

For a clean tag checkout, clone the tag, verify its signature separately, and
let the installer check that the checkout is clean and at exactly that tag:

```bash
VERSION=vX.Y.Z  # replace with a signed release tag
git clone --branch "$VERSION" --depth 1 https://github.com/snaplyze/skills-hub.git
cd skills-hub
git tag -v "$VERSION"          # verifies the signature with your local trust store
./install/opencode.sh --verify --ref "$VERSION"
```

Or install the source archive from the release:

```bash
VERSION=vX.Y.Z  # replace with a signed release tag
curl -fsSLO "https://github.com/snaplyze/skills-hub/releases/download/$VERSION/skills-hub-$VERSION.tar.gz"
curl -fsSLO "https://github.com/snaplyze/skills-hub/releases/download/$VERSION/SHA256SUMS"
sha256sum -c SHA256SUMS
tar -xzf "skills-hub-$VERSION.tar.gz"
cd "skills-hub-$VERSION"
./install/opencode.sh --copy
```

The archive has no `.git` metadata, so `--verify` does not apply; the checksum
and the release provenance attestation are the trust boundary. Verify
provenance with `gh attestation verify "skills-hub-$VERSION.tar.gz" --repo snaplyze/skills-hub`.

#### Install from main

Use `main` only for development. It is not a release and is not covered by the
release checksum:

```bash
git clone https://github.com/snaplyze/skills-hub.git
cd skills-hub

./install/opencode.sh                         # copy every skill
./install/opencode.sh frontend-design         # copy one skill
./install/opencode.sh --link frontend-design  # explicit symlink mode
./install/opencode.sh --dry-run               # preview, no writes
./install/opencode.sh --list                  # list skills and descriptions
```

| Flag | Behavior |
|---|---|
| `--copy` | Copy the skill tree (default). Excludes generated artifacts including `__pycache__`, `*.pyc`, `.ruff_cache`, `.pytest_cache`, `.mypy_cache`, `.venv`, `.git`, `.playwright-cli`, and `node_modules`. |
| `--link` | Symlink the skill directory. Explicit opt-in; links follow the clone and break if it moves or is deleted. |
| `--all` | Install every discovered skill. Invalid kebab-case IDs are rejected. |
| `--force` | Move an existing installation to `<target>/.skills-hub-backups/` and atomically replace it. |
| `--verify` | Require a clean tracked git checkout at an exact release tag (`vX.Y.Z`, optionally with a prerelease suffix). Fails on tracked/untracked changes or a non-git archive. |
| `--ref TAG` | Exact tag required with `--verify`; passing `--ref` implies `--verify`. |
| `--dry-run` | Print actions without writing. |
| `--list` | List skills, including folded YAML descriptions. |
| `--target DIR` | Override the target; leading `~/` is expanded. Unsafe roots are refused. |

The installer canonicalizes target and source paths and refuses `/`, `$HOME`,
the repository root or a path inside it, the source skill or its
ancestors/descendants, symlinked source/target roots, and paths with control
characters. It installs through a staging directory inside the target and keeps
replaced skills under `.skills-hub-backups`.

To update a copy install, re-run with `--force`; the previous version is kept in
the backup directory. To update a symlink install, pull the clone. To uninstall,
remove the installed skill:

```bash
rm -rf -- "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/frontend-design"
```

Start a new OpenCode session or run `/reload` after installing. A minimal
manual copy (without the installer's safety checks or artifact exclusions) is:

```bash
mkdir -p -- ~/.config/opencode/skills
cp -R -- skills/frontend-design ~/.config/opencode/skills/
```

OpenCode discovers directory skills with a `SKILL.md` and advertises them by their `description`. The skill ID is the directory name (`frontend-design`).

### Other harnesses

The skill is written in plain Markdown with relative references, so the content is portable. Harness-specific installers will be added when their target paths and frontmatter requirements are verified. Do not assume a Claude Code or Codex path until the installer exists.

## Repository layout

```text
skills-hub/
├── AGENTS.md                    # project facts for agents
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── GOVERNANCE.md
├── CHANGELOG.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── Makefile                     # local validation entry points
├── package.json                 # pinned Markdown/CSS tools
├── pyproject.toml               # Ruff configuration
├── requirements-dev.in          # direct Python development inputs
├── requirements-dev.txt         # hash-locked Python development tools
├── .github/                     # CI, security, issue/PR templates
├── docs/
│   ├── plan.md                  # audit and remediation registry
│   ├── release-process.md       # release gate and owner setup
│   └── repository-settings.md   # settings evidence and owner actions
├── install/
│   └── opencode.sh              # global OpenCode installer
├── scripts/
│   ├── validate.py              # repository-wide validation
│   ├── check_workflows.py       # Actions policy checks
│   ├── check_external_links.py  # scheduled link audit
│   └── release_notes.py         # SemVer/changelog release notes
├── tests/                       # validator, installer, release, workflow tests
└── skills/
    └── frontend-design/
        ├── SKILL.md             # workflow, principles, hard rules
        ├── LICENSE              # MIT for the portable skill
        ├── references/          # design, UX, accessibility, implementation
        ├── assets/              # tokens, contrast pairs, templates
        └── scripts/
            └── contrast.py      # dependency-free WCAG contrast checker
```

## Using the skill

Once installed, mention it in a prompt or let OpenCode load it when relevant:

```text
Use @frontend-design to redesign the pricing page. The product is a
tool-lending library for neighbors; the current page looks like generic SaaS.
```

```text
Use @frontend-design to audit the checkout flow. Focus on mobile, keyboard
access, error states, and whether the design feels specific to the product.
```

The skill will ask for a short design read before coding and report what it actually verified. It will not claim a screenshot is a usability test or an axe scan is full accessibility.

### Contrast checker

```bash
cd skills/frontend-design
python3 scripts/contrast.py "#1b1916" "#f7f6f2" --label "body on canvas"
python3 scripts/contrast.py --pairs assets/token-contrast-pairs.json --check
python3 scripts/contrast.py --self-test
```

It supports hex, `rgb()`, `hsl()`, alpha compositing, text/large-text/UI thresholds, JSON output, and a non-zero exit code for CI. The bundled fixture covers 64 light/dark pairs from the starter token sheet and passes WCAG 2.2 AA.

## Design principles of this hub

1. **Progressive disclosure.** `SKILL.md` is the entry point; references are loaded only when the task needs them.
2. **Deterministic where possible.** Scripts handle measurable checks; the model handles judgment.
3. **Evidence over claims.** The skill requires verification and reports gaps.
4. **Portable content.** Plain Markdown, relative paths, no harness-specific APIs in the body.
5. **No vendor lock-in.** Skills do not install packages, modify the OS, or authorize unrelated changes.
6. **Attribution.** Sources and licenses are recorded; adapted text is not copied wholesale.

## Validation

Prerequisites: Python 3.12+, Bash, and Node.js 22+ for the pinned Markdown
and CSS tools. OpenCode is only needed to test installation.

One command installs the hash-locked development tools and runs the full local
suite:

```bash
make deps
make check
```

Or run individual checks:

```bash
make validate   # frontmatter, links, anchors, tokens, fixture, installer syntax
make lint       # ruff + markdownlint (pinned npm tools)
make test       # pytest suite, including contrast CLI and negative fixtures
make shellcheck # ShellCheck on the installer
make workflows  # pinned-action and permissions policy
make links      # external link audit (network; scheduled)
make check      # every required local check, exactly once
```

CI runs `make check` and the separate CodeQL, Dependency Review, Secret Scan,
and Scorecard workflows. Link Audit is scheduled because external services are
not a required merge gate.

## Repository protections

This is a public repository. `main` is protected by a repository ruleset:

- pull requests are required; direct pushes are blocked;
- required checks: `validate`, `Analyze (python)`, and `dependency-review`;
- conversations must be resolved;
- history must be linear; only squash merge is enabled;
- force pushes and branch deletions are blocked;
- CodeQL code scanning must not report error-level or high/critical security
  alerts;
- CODEOWNERS is advisory under the current solo-maintainer ruleset.

Tags matching `v*` block deletion and force updates. The release workflow is dispatched from `main` with an annotated signed tag;
it verifies the signature against owner-configured trust material, requires the
tagged commit to be an ancestor of `origin/main`, requires successful
`validate` and `Analyze (python)` check-runs for that commit, and requires
immutable releases. It creates a **draft** release with a source archive,
`SHA256SUMS`, and a build provenance attestation; promotion is manual.
Tag creation itself is not gated by the workflow. The protected `release`
environment, tag ruleset, immutable-release setting, and signature trust
variables are repository settings configured by the owner; see
[docs/release-process.md](docs/release-process.md).

Security features enabled:

- secret scanning and push protection;
- a `Secret Scan` workflow using checksum-verified gitleaks;
- Dependabot alerts and security updates;
- private vulnerability reporting;
- CodeQL code scanning on `main` and pull requests;
- OpenSSF Scorecard weekly, on `main`, and after branch-protection changes;
  SARIF is uploaded to code scanning. Ruleset changes are covered by the
  weekly run because Actions has no `repository_ruleset` trigger;
- GitHub Actions with a read-only default token, job-scoped write permissions,
  pinned action commits, a GitHub-owned/verified action allowlist, and approval
  required for all external fork contributors;
- explicit settings evidence and owner-only release controls in
  [docs/repository-settings.md](docs/repository-settings.md).

See [GOVERNANCE.md](GOVERNANCE.md) for the decision and review model, and
[SECURITY.md](SECURITY.md) for private reporting. Agent-facing project facts
live in [AGENTS.md](AGENTS.md); audit and remediation tasks live in
[docs/plan.md](docs/plan.md).

## Adding a skill

1. Create `skills/<skill-id>/SKILL.md` with YAML frontmatter (`name`, `description`, `license`, optional `compatibility`).
2. Keep the description trigger-rich and scoped: what it does and when to use it.
3. Put detailed material in `references/`, templates in `assets/`, deterministic helpers in `scripts/`.
4. Use relative paths from the skill directory.
5. Document the skill in the README Skills section; update the harness status table if it adds a new client.
6. Validate links, scripts, and the installer.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. By
participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

[Report a vulnerability privately](https://github.com/snaplyze/skills-hub/security/advisories/new).
Do not open a public issue. See [SECURITY.md](SECURITY.md) for scope, response
expectations, and the repository's security controls.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT for this repository. See [LICENSE](LICENSE). Third-party sources are recorded in the canonical [`sources.md`](skills/frontend-design/references/sources.md); [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) points to that registry. Two community sources are explicitly marked for upstream verification.
