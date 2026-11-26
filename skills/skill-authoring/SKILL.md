---
name: Skill Authoring
description: Use when creating or editing an OpenCode skill, defining its trigger description, workflow, references, and pressure tests. Covers progressive disclosure, compact instructions, baseline-vs-skill evaluation, trigger quality, validation, and repository integration without hooks or plugins. Not for writing application documentation or general agent rules.
license: MIT
compatibility: opencode
---

# Skill Authoring

## What a skill is

A skill is a small, portable instruction package that changes behavior at the moment it is relevant. `SKILL.md` is the entry point; deeper material belongs in `references/` and is loaded only when needed. Descriptions are the trigger surface; the body is the workflow.

## Discover the need

Collect a real prompt or session where the current agent failed. Name the behavior change, not the topic. Check whether an existing skill already covers it; prefer editing that skill over adding a near-duplicate. Decide the skill type: workflow (a sequence), technique (a method), reference (a lookup), or pattern (a reusable design). Each type has a different test and amount of prose.

## Directory shape

Use `skills/<lowercase-kebab-id>/SKILL.md`, optional `references/` for depth, `assets/` for templates/data, and `scripts/` only for deterministic checks. Keep the entry point short; a reference must be named in routing and loaded only when needed. When a skill adds Markdown files under `references/` or `assets/`, also add `skills/<lowercase-kebab-id>/assets/reading-sets.json` (`{"sets": {"<name>": ["SKILL.md", ...]}}`, each set ≤ 32,768 B) so the repository validator enforces the reading budget.

## Design before prose

1. **Name the behavior change.** What should an agent do differently after loading this skill? If the answer is "know more", the skill is probably documentation.
2. **Define the trigger and the anti-trigger.** Write the description with the situation, the job, and what it is not for. Test it against realistic prompts.
3. **Choose the smallest workflow.** One job per skill. Remove rules the model already follows, duplicated global instructions, and advice that does not change a decision.
4. **Design the failure path.** What does the agent do when the input is ambiguous, a check is unavailable, or the task is outside scope?
5. **Decide progressive disclosure.** Keep the core workflow inline. Move long tables, examples, templates, or platform-specific details to references or assets and link them.

## SKILL.md structure

```text
---
name: <display name>
description: <when to use + what it does + anti-trigger>
license: MIT
compatibility: opencode
# Optional OpenCode V2 controls:
# disable-model-invocation: true
# metadata:
#   version: "1.0.0"
#   opencode/autoinvoke: false
---

# <title>
One-paragraph purpose.

## Workflow
Numbered decisions and actions, not a feature tour.

## Rules / red flags
Only constraints that change behavior.

## Output / handoff
What the agent returns and which skill or action comes next.
```

Use short sections and imperative language. Prefer examples over adjectives. Do not copy an upstream skill's text; synthesize the idea and cite the source.

## Trigger mining

Mine real prompts, failures, and near-misses before writing. Group them by the behavior the agent should change, not by topic. For each group, record:

- a positive prompt that should load the skill;
- a negative prompt that should not;
- the failure mode without the skill;
- the observable difference with the skill;
- the cheapest pressure variant (ambiguous, incomplete, adversarial, or large input).

If there is no real behavior change or no credible trigger, do not add the skill. Prefer editing an existing skill over a near-duplicate.

## Test the skill

Use TDD for behavior-shaping documentation:

1. **Baseline:** run realistic prompts without the skill; record the failure mode (for example, jumps to code, skips verification, invents requirements).
2. **Write:** add the smallest instruction that addresses that failure.
3. **Retest:** run the same prompts and pressure variants; check that the behavior changes for the intended reason.
4. **Trigger test:** confirm the description fires on relevant prompts and not on nearby false positives.
5. **Mutation test:** remove or weaken a rule and confirm the test scenario catches the regression.
6. **Budget test:** keep the loaded set small; link references instead of dumping them.

If you cannot run an agent evaluation, use a documented tabletop trigger matrix and state that it is not behavioral evidence. For a reference skill, test lookup accuracy and staleness; for a workflow, test sequence and stop conditions; for a technique, test application and failure cases; for a pattern, test selection and tradeoffs.

Record each evaluation:

```text
Prompt:
Baseline (no skill):
With skill:
Triggered? yes/no
Evidence:
Verdict: keep / revise / drop
```

Compare on the same prompt and model. Do not claim a quantitative improvement without a baseline and a repeatable check.

## Repository integration

- Add the skill under `skills/<lowercase-kebab-id>/SKILL.md`.
- Validate frontmatter, links, anchors, file references, and the loaded reading budget.
- Add it to the README skills table and any project skill listing.
- Record sources and licenses; do not copy upstream text. Verify the license of the exact source, not only the repository root.
- Add a CHANGELOG entry and plan/tracker task when the repository uses them.
- Keep the skill self-contained; no hooks, plugins, or hidden runtime dependencies.
- Version a material behavior change in the skill metadata or changelog; re-run the trigger/eval cases before merging.

## Red flags

- The description could apply to any task.
- The skill repeats general agent rules or repository policy.
- The body is a long essay with no decision points.
- The trigger fires on unrelated work.
- No failure path or handoff.
- Only happy-path examples.
- The skill is too large to load on a typical task.

## Output

A validated, trigger-tested skill with a clear workflow, minimal loaded context, and documented sources.
