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

The installer symlinks skills into `${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills` by default:

```bash
git clone https://github.com/snaplyze/skills-hub.git
cd skills-hub

# Install every skill (currently frontend-design)
./install/opencode.sh

# Or install one skill
./install/opencode.sh frontend-design

# Copy instead of symlink
./install/opencode.sh --copy frontend-design

# Preview without writing
./install/opencode.sh --dry-run

# List discovered skills
./install/opencode.sh --list
```

Use `--force` to replace an existing installation. Start a new OpenCode session or run `/reload` after installing.

Manual installation is equivalent:

```bash
mkdir -p ~/.config/opencode/skills
ln -s "$PWD/skills/frontend-design" ~/.config/opencode/skills/frontend-design
```

OpenCode discovers directory skills with a `SKILL.md` and advertises them by their `description`. The skill ID is the directory name (`frontend-design`).

### Other harnesses

The skill is written in plain Markdown with relative references, so the content is portable. Harness-specific installers will be added when their target paths and frontmatter requirements are verified. Do not assume a Claude Code or Codex path until the installer exists.

## Repository layout

```text
skills-hub/
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── install/
│   └── opencode.sh
└── skills/
    └── frontend-design/
        ├── SKILL.md                 # workflow, principles, hard rules
        ├── LICENSE                  # MIT for the portable skill
        ├── references/
        │   ├── design-direction.md  # aesthetic direction, type, color, layout
        │   ├── design-system.md     # tokens, components, themes, handoff
        │   ├── ux-patterns.md       # flows, forms, states, copy, research-lite
        │   ├── accessibility.md     # WCAG 2.2 AA, keyboard, ARIA, testing
        │   ├── responsive-mobile.md # mobile-first, touch, safe areas
        │   ├── motion.md            # choreography, timing, performance
        │   ├── implementation.md    # modern CSS, React/Next, Tailwind, perf
        │   ├── quality-gates.md     # pre-delivery audit and definition of done
        │   └── sources.md           # standards, licenses, attribution
        ├── assets/
        │   ├── tokens.css           # starter light/dark token sheet
        │   ├── token-contrast-pairs.json # 64 audited light/dark pairs
        │   ├── design-brief.md      # brief, direction, and critique template
        │   └── audit-report.md      # severity-based audit template
        └── scripts/
            └── contrast.py          # dependency-free WCAG contrast checker
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

One command runs the full local suite:

```bash
python3 -m pip install -r requirements-dev.txt
make check
```

Or run individual checks:

```bash
make validate   # frontmatter, references, links, anchors, installer syntax
make lint       # ruff + markdownlint
make test       # contrast self-test + 64-pair fixture
make check      # everything CI runs
```

CI runs the same checks, plus ShellCheck, CSS parsing, CodeQL, dependency
review, and OpenSSF Scorecard.

## Repository protections

This is a public repository. `main` is protected by a repository ruleset:

- pull requests are required; direct pushes are blocked;
- required checks: `validate`, `Analyze (python)`, and `dependency-review`;
- conversations must be resolved;
- history must be linear; only squash merge is enabled;
- force pushes and branch deletions are blocked;
- CodeQL code scanning must not report error-level or high/critical security
  alerts.

Tags matching `v*` are protected from deletion and force updates.

Security features enabled:

- secret scanning and push protection;
- Dependabot alerts and security updates;
- private vulnerability reporting;
- CodeQL code scanning on `main` and pull requests;
- OpenSSF Scorecard on a weekly schedule;
- GitHub Actions with a read-only default token, pinned action commits, and
  approval required for first-time fork contributors.

See [GOVERNANCE.md](GOVERNANCE.md) for the decision and review model, and
[SECURITY.md](SECURITY.md) for private reporting.

## Adding a skill

1. Create `skills/<skill-id>/SKILL.md` with YAML frontmatter (`name`, `description`, `license`, optional `compatibility`).
2. Keep the description trigger-rich and scoped: what it does and when to use it.
3. Put detailed material in `references/`, templates in `assets/`, deterministic helpers in `scripts/`.
4. Use relative paths from the skill directory.
5. Add the skill to the README table.
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

MIT for this repository. See [LICENSE](LICENSE). Third-party sources and licenses are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and in `skills/frontend-design/references/sources.md`.
