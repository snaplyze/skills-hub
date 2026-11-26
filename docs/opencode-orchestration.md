# Native OpenCode orchestration

This repository uses a **skill-only** orchestration layer. It keeps the useful routing and quality gates from orchestration frameworks without a plugin, hooks, session bootstrap, marketplace, TUI overlay, or hardcoded model-profile installer.

## What it is

`skills/orchestration/SKILL.md` tells the main session when to:

- work directly;
- send one bounded read-only or implementation task to a native OpenCode subagent;
- run parallel independent read-only investigations;
- serialize writers that share files;
- request a fresh review and verify the integrated result.

In OpenCode V2, the native `subagent` tool runs children asynchronously in the background, returns a `sessionID` immediately, notifies the parent via `<background-result>` when a child goes idle, and supports multi-turn follow-ups via `sessionID`. Built-in `explore` denies `edit`/`write`/`patch`, `skill`, and `question` by default while still permitting `shell` and `external_directory`; built-in `general` denies `question` and `subagent` while inheriting `edit`, `shell`, `skill`, and `external_directory` (`allow` by default in V2). The skill describes roles as portable briefs rather than installing custom agents. If you want permission-enforced read-only review (with both `edit` and `shell` denied), add a local `.opencode/agents/reviewer.md` using V2 `permissions` without any plugin.

## Comparison

| Concern | oh-my-opencode-slim | claude-orchestration | This repository (over OpenCode V2) |
|---|---|---|---|
| Runtime | OpenCode plugin, custom background manager, marketplace, TUI | Claude Code plugin + installer + profiles + runtime smoke | One Markdown skill over native V2 `subagent` |
| Agents | Multiple named specialists and model presets | Five plugin-scoped specialists | Built-in `explore` and `general` with explicit briefs (or local `.opencode/agents/*.md`) |
| Model/effort profiles | Yes, configurable presets | Yes, subscription profiles | Not bundled in the skill; V2 supports `model: provider/model#variant` per agent and ad-hoc `model` overrides locally |
| Hooks/bootstrap | Yes | Claude plugin/rule | No |
| Background execution & cancellation | Plugin-managed job manager | Ordinary subagents | Native V2 async `subagent` (`sessionID`, `<background-result>`, TUI cancel `ctrl+d`) and optional native `automation`; no plugin scheduler |
| Main risk | Configuration and surface area | Harness-specific install and profiles | Routing discipline, write-root bounds, and `explore` shell discipline |

The goal is not to reproduce every feature. It is to preserve the decisions that improve outcomes: route the right work, protect context, keep one writer per file, review material changes, and prove completion.

## Zero-config use

Install the skills normally:

```bash
./install/opencode.sh --copy
```

Then ask for complex work in plain language. The `orchestration` description triggers it; OpenCode V2's native `subagent` tool handles asynchronous delegation. No `opencode.json`, plugin entry, hook, or extra background daemon is required.

If the project already defines custom agents (for example `.opencode/agents/reviewer.md`), substitute their names for `explore`/`general` in the brief. The skill does not install or change those definitions.

## Routing examples

**Map before changing**

```text
Brief: map the authentication entry points, session storage, and callback paths.
Read-only. Do not run mutating shell commands or edit files. Return file paths
and a short flow.
```

**Two independent writers**

```text
Writer A owns src/parser/ and its tests (within the repository root).
Writer B owns src/renderer/ and its tests (within the repository root).
Do not touch shared types; report the interface change instead.
```

**Review the actual diff**

```text
Review spec + diff from BASE to HEAD (fresh child session, read-only). Report
P0/P1/P2 with file:line, evidence, impact, and a concrete fix. Do not edit or
approve on my behalf.
```

## Limits

- **No bundled model or effort presets.** OpenCode V2 natively supports per-agent `model#variant` in `.opencode/agents/*.md` and ad-hoc `model` parameters on `subagent` calls; this skill intentionally stays model-agnostic for portability.
- **No plugin-managed continuation loops or multiplexer panes.** OpenCode V2 provides async background subagents with `sessionID` follow-ups, TUI subagent switching/cancellation (`ctrl+d`), and native `automation`; this skill stays a thin routing layer without plugin state.
- **No sandbox added by the skill.** A read-only brief is an instruction, not a permission system: `explore` still permits `shell` and `external_directory` defaults to `allow` in OpenCode V2. Use OpenCode V2 `permissions` or a local `.opencode/agents/*.md` definition when hard enforcement is required.
- **No automatic orchestration on every prompt.** The skill must be relevant to the task; small sequential edits stay direct.

## Verification

- `python3 scripts/validate.py` checks the skill frontmatter and links.
- `tests/test_skill_suite.py` checks the native routing contract and the docs.
- `make check` runs the full repository suite.

See [the plan](plan.md) for the task record and [the workflow skills](../skills/orchestration/SKILL.md) for the operational instructions.
