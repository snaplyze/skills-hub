# Third-party notices

This repository contains original skill text synthesized from public sources and standards. It does not reproduce the source skills wholesale. The registry linked below identifies the ideas, patterns, standards, and licenses that informed it.

## Skill sources

The canonical source, standards, and license registry for the frontend-design
skill is [`skills/frontend-design/references/sources.md`](skills/frontend-design/references/sources.md).
It lists the eight source skills, thirteen standards and references, the
license status of each source, and the unresolved upstream-license notes. This
file is the repository-level pointer so the lists cannot drift.

## Agent workflow skills

The `specification`, `implementation-planning`, `autonomous-execution`,
`systematic-debugging`, `test-driven-development`, `code-review`, `delivery`,
`clean-code`, `skill-authoring`, and `orchestration` skills are original synthesis; no upstream text is reproduced wholesale, although
short standard phrases may coincide. They are informed by:

- [obra/superpowers](https://github.com/obra/superpowers) — MIT, copyright
  Jesse Vincent;
- [sickn33/agentic-awesome-skills — clean-code](https://github.com/sickn33/agentic-awesome-skills/tree/main/skills/clean-code)
  — repository code MIT, original content CC BY 4.0; the skill names ClawForge
  as its source. Recheck upstream terms before redistributing substantial text.
- [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim)
  — MIT; orchestration/routing ideas only.
- [snaplyze/claude-orchestration](https://github.com/snaplyze/claude-orchestration)
  — Apache-2.0; orchestration/routing ideas only;
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) — MIT;
  planning, incremental delivery, review, git, and doubt-driven ideas;
- [OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files)
  — MIT; persistent project-local planning and recovery ideas;
- [wshobson/agents](https://github.com/wshobson/agents) — MIT; multi-reviewer
  and parallel ownership ideas;
- [anthropics/skills](https://github.com/anthropics/skills) — the README marks
  many skills Apache 2.0; used for skill-authoring patterns only, with
  per-skill license verification required.

The workflow skills deliberately avoid hooks, plugins, and session bootstrap;
their ideas are expressed in new Markdown and tested as OpenCode skills.

## Notes

- WCAG, WAI-ARIA, and W3C documents are referenced as standards. Their text is not reproduced here. Consult the W3C document license for redistribution of their text.
- Product names, trademarks, and brand assets belong to their respective owners.
- Fonts named in examples are suggestions, not bundled assets. Check each font's license before shipping.
- If you contribute adapted text, add it to the relevant registry: frontend-design material in `skills/frontend-design/references/sources.md`; workflow-skill material in this file or `docs/plan.md`, with the license and a link.
