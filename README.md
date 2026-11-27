# Skills Hub

[![CI](https://github.com/snaplyze/skills-hub/actions/workflows/ci.yml/badge.svg)](https://github.com/snaplyze/skills-hub/actions/workflows/ci.yml)
[![CodeQL](https://github.com/snaplyze/skills-hub/actions/workflows/codeql.yml/badge.svg)](https://github.com/snaplyze/skills-hub/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/snaplyze/skills-hub/badge)](https://securityscorecards.dev/viewer/?uri=github.com/snaplyze/skills-hub)
[![Release](https://img.shields.io/github/v/release/snaplyze/skills-hub)](https://github.com/snaplyze/skills-hub/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Antigravity](https://img.shields.io/badge/Antigravity-ready-1a73e8)](https://antigravity.google/)
[![OpenCode](https://img.shields.io/badge/OpenCode-ready-0f766e)](https://opencode.ai/)

Portable, high-craft skills for AI coding agents following the [Agent Skills open standard](https://agentskills.io/specification). Each skill is a self-contained directory with a `SKILL.md`, optional references, assets, and deterministic scripts. Install them globally into the agent you use; keep them versioned here.

The repository includes **Frontend Design** plus a compact 10-skill agent workflow suite for **Google Antigravity** (App, CLI `agy`, IDE & extensions) and **OpenCode**: specification, planning, orchestration, execution, debugging, TDD, review, delivery, clean code, and skill authoring. The workflow skills are deliberately smaller than hook-heavy frameworks: they use standard skill frontmatter and unified portable Markdown, with no plugin or session bootstrap.

## Status

| Harness | Status | Installer |
|---|---|---|
| [Google Antigravity](https://antigravity.google/) (App, CLI, IDE) | Ready | `install/antigravity.sh` |
| [OpenCode](https://opencode.ai/) | Ready | `install/opencode.sh` |
| Claude Code | Planned | — |
| Codex | Planned | — |
| Other agents | Planned | — |

## Skills

| Skill | Purpose | Harness |
|---|---|---|
| [`frontend-design`](skills/frontend-design/SKILL.md) | Distinctive, accessible web interface design and frontend quality | Antigravity, OpenCode |
| [`orchestration`](skills/orchestration/SKILL.md) | Route complex work across native subagents, workflows, and orchestrators without a plugin | Antigravity, OpenCode |
| [`specification`](skills/specification/SKILL.md) | Turn ambiguous requests into testable specs with non-goals and acceptance | Antigravity, OpenCode |
| [`implementation-planning`](skills/implementation-planning/SKILL.md) | Turn a spec into small, testable, dependency-aware tasks | Antigravity, OpenCode |
| [`autonomous-execution`](skills/autonomous-execution/SKILL.md) | Execute approved plans with subagents, isolated workspaces, TDD gates, and a ledger | Antigravity, OpenCode |
| [`systematic-debugging`](skills/systematic-debugging/SKILL.md) | Reproduce, locate root cause, fix, and prove with a regression test | Antigravity, OpenCode |
| [`test-driven-development`](skills/test-driven-development/SKILL.md) | Red-green-refactor with behavior-focused tests | Antigravity, OpenCode |
| [`code-review`](skills/code-review/SKILL.md) | Request fresh-context review and evaluate feedback with evidence | Antigravity, OpenCode |
| [`delivery`](skills/delivery/SKILL.md) | Verify, open a scoped PR, merge without bypass, and report evidence | Antigravity, OpenCode |
| [`clean-code`](skills/clean-code/SKILL.md) | Language-agnostic readability, boundaries, errors, and refactoring | Antigravity, OpenCode |
| [`skill-authoring`](skills/skill-authoring/SKILL.md) | Design, test, and integrate portable agent skills (Agent Skills standard) | Antigravity, OpenCode |

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

### Agent workflow suite

These skills cover the path from an ambiguous request to a verified merge. They are independent enough to load on demand, but designed to hand off to one another: `specification` → `implementation-planning` → `autonomous-execution` → `code-review` → `delivery`, with `systematic-debugging`, `test-driven-development`, and `clean-code` available at the points where they change the outcome. `skill-authoring` is the meta-skill for extending the suite. `orchestration` is the thin routing layer over native orchestration — see [`docs/antigravity-orchestration.md`](docs/antigravity-orchestration.md) for Google Antigravity (`invoke_subagent`, `define_subagent`, `run_workflow`, `/swarm`, `/boost`, `/teamwork`) and [`docs/opencode-orchestration.md`](docs/opencode-orchestration.md) for OpenCode V2.

No hooks, plugin bootstrap, or session injection are required. Trigger quality comes from each skill description and explicit routing. Each skill is loaded independently; the suite is not a single context load. Project plans live in `docs/plans/`; long runs keep a `progress.md` ledger beside the plan, not in a tool-owned hidden directory.

## Install

Both global installers share [`install/lib.sh`](install/lib.sh) and use copy mode by default (snapshotting content without writing into this checkout). Use `--link` only when you want live symlinks to the clone. They require Bash and GNU coreutils/findutils/tar (`realpath -m`, `sort -z`, `mv -T`, `find -printf`, GNU `tar`); on systems without those tools, use the minimal manual copy below.

Release `v1.3.0` is signed and immutable; the public trust file is [`docs/release-signing/allowed_signers`](docs/release-signing/allowed_signers). Tags published before the release gate (`v1.0.1` and earlier) are unsigned and have no source-archive assets; do not treat them as signed releases. The protected `release` environment, tag-signature trust, tag rules, and immutable-release setup are recorded in [docs/repository-settings.md](docs/repository-settings.md) and [docs/release-process.md](docs/release-process.md).

### Google Antigravity

The Antigravity installer copies skills into `$HOME/.gemini/config/skills` by default — the unified personal skills directory read by **Antigravity App**, **Antigravity CLI (`agy`)**, and **Antigravity IDE** (it intentionally ignores `XDG_CONFIG_HOME`).

#### Install from a release (Antigravity)

```bash
VERSION=vX.Y.Z  # replace with a signed release tag
git clone --branch "$VERSION" --depth 1 https://github.com/snaplyze/skills-hub.git
cd skills-hub
git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile=docs/release-signing/allowed_signers \
  verify-tag "$VERSION"
./install/antigravity.sh --verify --ref "$VERSION"
```

Or install from a checksum-verified release archive:

```bash
VERSION=vX.Y.Z  # replace with a signed release tag
curl -fsSLO "https://github.com/snaplyze/skills-hub/releases/download/$VERSION/skills-hub-$VERSION.tar.gz"
curl -fsSLO "https://github.com/snaplyze/skills-hub/releases/download/$VERSION/SHA256SUMS"
sha256sum -c SHA256SUMS
tar -xzf "skills-hub-$VERSION.tar.gz"
cd "skills-hub-$VERSION"
./install/antigravity.sh --copy
```

#### Install from main (Antigravity)

Use `main` only for development (it is not a signed release):

```bash
git clone https://github.com/snaplyze/skills-hub.git
cd skills-hub

./install/antigravity.sh                         # copy every skill
./install/antigravity.sh frontend-design         # copy one skill
./install/antigravity.sh --link frontend-design  # explicit symlink mode
./install/antigravity.sh --dry-run               # preview, no writes
./install/antigravity.sh --list                  # list skills and descriptions
```

Antigravity rereads skills automatically before each turn; in the Antigravity CLI, run `/skills reload` (or start a new conversation) to refresh slash commands (`/<skill-name>`). For a zero-copy personal setup without symlinks, you can also point `~/.gemini/config/skills.json` at your clone's absolute `skills/` path:

```json
{
  "entries": [
    { "path": "/absolute/path/to/skills-hub/skills" }
  ]
}
```

To uninstall a skill from Antigravity, remove its folder:

```bash
rm -rf -- "$HOME/.gemini/config/skills/frontend-design"
```

Minimal manual copy (without safety checks or artifact exclusions):

```bash
mkdir -p -- ~/.gemini/config/skills
cp -R -- skills/frontend-design ~/.gemini/config/skills/
```

Antigravity discovers skills with a `SKILL.md` one level deep under workspace `.agents/skills/` (highest priority) and global `~/.gemini/config/skills/`, advertising each skill by its `name` (exposed as `/<name>`) and `description`.

### OpenCode

The OpenCode installer copies skills into `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` by default.

#### Install from a release (OpenCode)

```bash
VERSION=vX.Y.Z  # replace with a signed release tag
git clone --branch "$VERSION" --depth 1 https://github.com/snaplyze/skills-hub.git
cd skills-hub
git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile=docs/release-signing/allowed_signers \
  verify-tag "$VERSION"
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

The archive has no `.git` metadata, so `--verify` does not apply; the checksum and the release provenance attestation are the trust boundary. Verify provenance with `gh attestation verify "skills-hub-$VERSION.tar.gz" --repo snaplyze/skills-hub`.

#### Install from main (OpenCode)

```bash
git clone https://github.com/snaplyze/skills-hub.git
cd skills-hub

./install/opencode.sh                         # copy every skill
./install/opencode.sh frontend-design         # copy one skill
./install/opencode.sh --link frontend-design  # explicit symlink mode
./install/opencode.sh --dry-run               # preview, no writes
./install/opencode.sh --list                  # list skills and descriptions
```

To uninstall a skill from OpenCode:

```bash
rm -rf -- "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/frontend-design"
```

OpenCode reloads skills automatically after install; run `opencode reload` (or `/reload` / Command Palette → Reload configuration) to force a refresh without restarting. Minimal manual copy:

```bash
mkdir -p -- ~/.config/opencode/skills
cp -R -- skills/frontend-design ~/.config/opencode/skills/
```

OpenCode discovers directory skills with a `SKILL.md` and advertises them by their `description`. In OpenCode V2, project-local skill directories take precedence over global `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills/`, extra skill paths can be configured via `skills[]`, and per-skill access can be controlled with `permission.skill` (`allow` / `ask` / `deny`) in OpenCode configuration.

### Installer flags and safety

Both `./install/antigravity.sh` and `./install/opencode.sh` support the same options:

| Flag | Behavior |
|---|---|
| `--copy` | Copy the skill tree (default). Excludes generated artifacts and secret-like files (`__pycache__`, `*.py[cod]`, `.ruff_cache`, `.pytest_cache`, `.mypy_cache`, `.venv`, `venv`, `.git`, `.playwright-cli`, `node_modules`, `.DS_Store`, `.env`, `.env.*` except `.env.example`, `*.key`, `*.pem`, `*.p12`, `secrets`, `credentials*`, `id_*` SSH keys, `.opencode`, `.claude`, `.agents`, `.gemini`). |
| `--link` | Symlink the skill directory. Explicit opt-in; links follow the clone and break if it moves or is deleted. |
| `--all` | Install every discovered skill. Invalid kebab-case IDs are rejected. |
| `--force` | Move an existing installation to `<target>/.skills-hub-backups/` and atomically replace it. |
| `--verify` | Require a clean tracked git checkout at an exact release tag (`vX.Y.Z`, optionally with a prerelease suffix). Fails on tracked/untracked changes or a non-git archive. |
| `--ref TAG` | Exact tag required with `--verify`; passing `--ref` implies `--verify`. |
| `--dry-run` | Print actions without writing. |
| `--list` | List skills, including folded YAML descriptions. |
| `--target DIR` | Override the target; leading `~/` is expanded. Unsafe roots are refused. |

The installers canonicalize target and source paths and refuse `/`, `$HOME`, the repository root or a path inside it, the source skill or its ancestors/descendants, symlinked source/target roots, symlinked `install/lib.sh`, symlinks inside skill trees, and paths with control characters. They run a pre-flight check before writing, install through a staging directory inside the target, keep replaced skills under `.skills-hub-backups`, and restore backups on interruption. To update a copy install, re-run with `--force`; to update a symlink install, pull the clone.

### Other harnesses

The skills are written in unified plain Markdown following the [Agent Skills open standard](https://agentskills.io/specification), so the content is portable. Additional harness-specific installers will be added when their target paths and discovery rules are verified. Do not assume a Claude Code or Codex path until the installer exists.

## Repository layout

```text
skills-hub/
├── AGENTS.md                        # project facts for agents
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── GOVERNANCE.md
├── CHANGELOG.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── Makefile                         # local validation entry points
├── package.json                     # pinned Markdown/CSS tools
├── package-lock.json                # locked npm dependency tree
├── pyproject.toml                   # Ruff configuration
├── requirements-dev.in              # direct Python development inputs
├── requirements-dev.txt             # hash-locked Python development tools
├── .github/                         # CI, security, issue/PR templates
├── docs/
│   ├── plan.md                      # audit and stage registry
│   ├── plans/                       # project-local task plans and ledgers
│   ├── antigravity-orchestration.md # native Antigravity orchestration guide
│   ├── opencode-orchestration.md    # native OpenCode routing architecture
│   ├── release-process.md           # release gate and owner setup
│   ├── release-signing/             # public SSH allowed-signers and rotation
│   └── repository-settings.md       # settings evidence and owner actions
├── install/
│   ├── antigravity.sh               # global Antigravity installer
│   ├── opencode.sh                  # global OpenCode installer
│   └── lib.sh                       # shared installer core and safety guards
├── scripts/
│   ├── validate.py                  # repository-wide validation
│   ├── check_workflows.py           # Actions policy checks
│   ├── check_external_links.py      # scheduled link audit
│   ├── release_notes.py             # SemVer/changelog release notes
│   └── release_checks.py            # required check-run gate
├── tests/                           # validator, installer, release, workflow tests
└── skills/                          # 11 portable skills; see the Skills table
    ├── frontend-design/             # design references, assets, contrast script
    ├── orchestration/               # native subagent & workflow routing
    └── ...                          # nine workflow skills
```

## Using the skills

Once installed, let Antigravity or OpenCode trigger a skill automatically from your prompt, or invoke it explicitly (`/<skill-name>` in Antigravity, `@<skill-name>` in OpenCode):

```text
/frontend-design Redesign the pricing page. The product is a tool-lending
library for neighbors; the current page looks like generic SaaS.
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
3. **Evidence over claims.** Skills require verification and report gaps.
4. **Portable content.** Unified Agent Skills Markdown, relative paths, no harness-locked runtime APIs in the skill body.
5. **No vendor lock-in.** Skills do not install packages, modify the OS, or authorize unrelated changes.
6. **Attribution.** Sources and licenses are recorded; adapted text is not copied wholesale.

## Validation

Prerequisites: Python 3.12+, Bash, and Node.js 22+ for the pinned Markdown and CSS tools. Antigravity (`agy`) or OpenCode is only needed to test installation and discovery locally.

One command installs the hash-locked development tools and runs the full local suite:

```bash
make deps
make check
```

Or run individual checks:

```bash
make validate   # frontmatter, links, anchors, tokens, fixture, installer syntax
make lint       # ruff + markdownlint (pinned Python/npm tools)
make test       # pytest suite, including contrast CLI and negative fixtures
make shellcheck # ShellCheck (-x) on both installers and install/lib.sh
make dry-run    # preview both Antigravity and OpenCode installs
make workflows  # pinned-action and permissions policy
make links      # external link audit (network; scheduled)
make check      # every required local check, exactly once
```

CI runs `make check` and the separate CodeQL, Dependency Review, Secret Scan, and Scorecard workflows. Link Audit is scheduled because external services are not a required merge gate.

## Repository protections

This is a public repository. `main` is protected by a repository ruleset:

- pull requests are required; direct pushes are blocked;
- required checks: `validate`, `Analyze (python)`, `Analyze (actions)`, `dependency-review`, and `gitleaks`;
- conversations must be resolved;
- history must be linear; only squash merge is enabled;
- force pushes and branch deletions are blocked;
- CodeQL code scanning must not report error-level or high/critical security alerts;
- CODEOWNERS is advisory under the current solo-maintainer ruleset.

Tags matching `v*` restrict creation (owner bypass), block deletion and force updates, and require signed tags. The release workflow is dispatched from `main` with an annotated signed tag; it verifies the signature against owner-configured trust material, requires the tagged commit to be an ancestor of `origin/main`, requires successful `validate`, `Analyze (python)`, `Analyze (actions)`, and `gitleaks` check-runs for that commit, and requires the owner to verify immutable releases separately. It creates a **draft** release with a source archive, `SHA256SUMS`, `.sigstore.json` bundle, and a build provenance attestation; promotion is manual. Tag creation itself is not gated by the workflow. The protected `release` environment, tag ruleset, immutable-release setting, and signature trust variables are repository settings configured by the owner; see [docs/release-process.md](docs/release-process.md).

Security features enabled:

- secret scanning and push protection;
- a `Secret Scan` workflow using checksum-verified gitleaks;
- Dependabot alerts and security updates;
- private vulnerability reporting;
- CodeQL code scanning on `main` and pull requests;
- OpenSSF Scorecard weekly, on `main`, and after branch-protection changes; SARIF is uploaded to code scanning. Ruleset changes are covered by the weekly run because Actions has no `repository_ruleset` trigger;
- GitHub Actions with a read-only default token, job-scoped write permissions, pinned action commits, a GitHub-owned/verified action allowlist (with an explicit exception for `ossf/scorecard-action@*`), and approval required for all external fork contributors;
- explicit settings evidence and owner-only release controls in [docs/repository-settings.md](docs/repository-settings.md).

See [GOVERNANCE.md](GOVERNANCE.md) for the decision and review model, and [SECURITY.md](SECURITY.md) for private reporting. Agent-facing project facts live in [AGENTS.md](AGENTS.md); audit and stage tasks live in [docs/plan.md](docs/plan.md).

## Adding a skill

1. Create `skills/<skill-id>/SKILL.md` with YAML frontmatter (`name` matching `<skill-id>` in lowercase kebab-case, `description`, `license`, optional `compatibility`, `allowed-tools`, `metadata`, `disable-model-invocation`).
2. Keep the description trigger-rich and scoped: what it does and when to use it.
3. Put detailed material in `references/`, templates in `assets/`, deterministic helpers in `scripts/`.
4. Use relative paths from the skill directory and keep instructions harness-neutral.
5. Document the skill in the README Skills section; update the harness status table if it adds a new client.
6. Validate links, scripts, and installers (`make check`).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. By participating, you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

[Report a vulnerability privately](https://github.com/snaplyze/skills-hub/security/advisories/new). Do not open a public issue. See [SECURITY.md](SECURITY.md) for scope, response expectations, and the repository's security controls.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT for this repository. See [LICENSE](LICENSE). Third-party sources for `frontend-design` are recorded in [`sources.md`](skills/frontend-design/references/sources.md); [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) points to that registry and serves as the canonical attribution registry for the agent workflow skills. Sources without verified upstream license files remain ideas-only.
