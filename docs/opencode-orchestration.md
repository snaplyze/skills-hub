# Native OpenCode orchestration

This repository uses a **skill-only** orchestration layer. It keeps the useful routing and quality gates from orchestration frameworks without a plugin, hooks, session bootstrap, background job scheduler, marketplace, TUI, or model-profile installer.

## What it is

`skills/orchestration/SKILL.md` tells the main session when to:

- work directly;
- send one bounded read-only or implementation task to a native OpenCode subagent;
- run parallel independent read-only investigations;
- serialize writers that share files;
- request a fresh review and verify the integrated result.

The native `subagent` tool exposes `explore` (read-only mapping) and `general` (implementation, testing, or review when the brief says read-only). The skill describes roles as briefs, not as new agent definitions.

## Comparison

| Concern | oh-my-opencode-slim | claude-orchestration | This repository |
|---|---|---|---|
| Runtime | OpenCode plugin, background jobs, task controls, marketplace, TUI | Claude Code plugin + installer + profiles + runtime smoke | One Markdown skill + native `subagent` |
| Agents | Multiple named specialists and model presets | Five plugin-scoped specialists | `explore` and `general` with explicit briefs |
| Model/effort profiles | Yes, configurable presets | Yes, subscription profiles | No; use the local OpenCode config |
| Hooks/bootstrap | Yes | Claude plugin/rule | No |
| Background scheduler | Yes | Ordinary subagents, no scheduler | No; native subagent calls only |
| Main risk | Configuration and surface area | Harness-specific install and profiles | Routing discipline and ownership |

The goal is not to reproduce every feature. It is to preserve the decisions that improve outcomes: route the right work, protect context, keep one writer per file, review material changes, and prove completion.

## Zero-config use

Install the skills normally:

```bash
./install/opencode.sh --copy
```

Then ask for complex work in plain language. The `orchestration` description triggers it; OpenCode's native subagent tool does the delegation. No `opencode.json`, plugin entry, hook, or background service is required.

If the project already defines custom agents, substitute their names for `explore`/`general` in the brief. The skill does not install or change those definitions.

## Routing examples

**Map before changing**

```text
Brief: map the authentication entry points, session storage, and callback paths.
Read-only. Return file paths and a short flow; do not edit.
```

**Two independent writers**

```text
Writer A owns src/parser/ and its tests.
Writer B owns src/renderer/ and its tests.
Do not touch shared types; report the interface change instead.
```

**Review the actual diff**

```text
Review spec + diff from BASE to HEAD. Read-only. Report P0/P1/P2 with file:line,
evidence, impact, and a concrete fix. Do not edit or approve on my behalf.
```

## Limits

- No per-agent model or effort selection. Configure that locally if needed; it is not portable and is not part of this skill.
- No background job lifecycle, automatic continuation, cancellation UI, or multiplexer panes. Use native subagent calls and the main session.
- No sandbox boundary. A review brief is an instruction, not a permission system; the active OpenCode permissions remain authoritative.
- No automatic orchestration on every prompt. The skill must be relevant to the task; small sequential edits stay direct.

## Verification

- `python3 scripts/validate.py` checks the skill frontmatter and links.
- `tests/test_skill_suite.py` checks the native routing contract and the docs.
- `make check` runs the full repository suite.

See [the plan](plan.md) for the task record and [the workflow skills](../skills/orchestration/SKILL.md) for the operational instructions.
