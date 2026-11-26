# Contributing

Thanks for helping improve Skills Hub. This repository collects portable, high-craft skills for AI coding agents. Contributions are welcome when they are specific, tested, and respectful of the project's scope.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## What belongs here

Good contributions:

- fix a real bug in a skill, installer, or validation script;
- add a well-scoped skill with clear triggers and references;
- improve accessibility, correctness, or clarity;
- add deterministic checks that catch a real class of mistakes;
- update documentation, examples, or attribution.

Please open an issue or a discussion before a large new skill so the scope can be agreed on. Do not add a skill that duplicates an existing one without explaining the difference.

## Development setup

Requirements:

- Python 3.12 or newer;
- Bash;
- Node.js 22+ for the pinned Markdown and CSS tools; `make deps` installs the
  hash-locked Python and npm development tools;
- OpenCode (only if you want to test discovery locally).

```bash
make deps
```

## Validate before opening a pull request

```bash
make validate   # frontmatter, links, anchors, tokens, fixture, installer syntax
make lint       # ruff + markdownlint
make test       # pytest suite, including contrast CLI and negative fixtures
make check      # every required local check, once; this is what CI runs
```

CI runs `make check` and separate CodeQL, Dependency Review, Secret Scan, and
Scorecard workflows. The Link Audit runs on a schedule because external
services are not a required merge gate.

Or run the commands individually:

```bash
python3 scripts/validate.py
ruff check .
node_modules/.bin/markdownlint-cli2 "**/*.md" "#node_modules"
python3 -m pytest -q
shellcheck install/opencode.sh
./install/opencode.sh --dry-run --target /tmp/opencode/skills-hub-check
node_modules/.bin/csstree-validator skills/frontend-design/assets/tokens.css
python3 scripts/check_workflows.py --strict
```

## Skill structure

```text
skills/<skill-id>/
├── SKILL.md          # frontmatter + core workflow
├── LICENSE           # usually MIT
├── references/       # detailed material, loaded on demand
├── assets/           # templates, tokens, fixtures
└── scripts/          # deterministic helpers
```

Rules:

- The directory name is the skill ID: lowercase kebab-case, 1–64 characters.
- `SKILL.md` starts with YAML frontmatter containing `name`, `description`, and `license` (optional: `compatibility`, `metadata`, `disable-model-invocation`).
- The description must explain what the skill does and when to use it. It is the primary trigger; OpenCode also lists the skill ID and name before loading the skill.
- Keep `SKILL.md` focused on the workflow. Put depth in `references/` and tell the model when to read each file.
- Use relative paths such as `references/design-direction.md`.
- Use real, tested scripts for measurable checks; do not fake deterministic results.
- Write original text. If you adapt material, add the source and license to `skills/frontend-design/references/sources.md` for `frontend-design` or to `THIRD_PARTY_NOTICES.md` for workflow skills (which also points to `sources.md`).
- Use English for skill content so it stays portable across harnesses.
- Do not include secrets, private URLs, personal data, or generated credentials.

## GitHub Actions

- Pin every action to a full commit SHA with a version comment, for example
  `actions/checkout@<40-char-sha> # v7.0.1`.
- Use GitHub-owned or verified actions. The repository restricts Actions to
  that allowlist, with an explicit exception for OpenSSF Scorecard.
- Keep `permissions` least-privilege and prefer job-level permissions over
  workflow-level write permissions.
- Do not add a workflow that requires repository secrets for fork pull
  requests. External fork workflows require maintainer approval.

## Commit messages

Use Conventional Commits where practical:

```text
feat: add mobile-design skill
fix: correct WCAG target-size guidance
docs: clarify OpenCode installation
chore: update pinned actions
```

Keep commits focused. Squash merge is the only enabled merge method.

## Pull requests

1. Fork the repository and create a branch from `main`.
2. Make the change and run `make check`.
3. Open a pull request with a clear summary and test evidence.
4. Address review comments and keep the branch up to date.
5. A maintainer merges with squash.

`main` is protected: pull requests are required, required checks must pass, conversations must be resolved, history is linear, and force pushes/deletions are blocked. Direct pushes to `main` are not part of the normal workflow.

## Review criteria

- Does the change solve a real problem?
- Is the skill trigger description accurate and scoped?
- Does the skill load references progressively instead of dumping everything?
- Are accessibility, performance, and responsive claims accurate?
- Are sources and licenses recorded?
- Do the checks pass, and is the evidence real?

## License

By contributing, you agree that your contributions are licensed under the repository's [MIT License](LICENSE).
