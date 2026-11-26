---
name: Clean Code
description: Use when refactoring existing code or reviewing a diff for readability, boundaries, errors, duplication, and coupling. Applies language-agnostic heuristics while preserving behavior and following repository conventions. Not for implementing a new feature from scratch, UI/visual design audits (use frontend-design), reviewing correctness instead of code quality, or cosmetic rewrites that do not serve the task.
license: MIT
compatibility: opencode
---

# Clean Code

## First principle

Code is clean when the next engineer can understand it, change it, and verify it without reconstructing the author's private context. Repository conventions outrank generic style rules. Behavior preservation outranks elegance.

## Decision order

1. Preserve current behavior and public contracts.
2. Read the surrounding code and tests; follow existing seams and naming.
3. Remove the smallest real source of confusion: a bad name, duplicated logic, mixed abstraction, hidden state, or a missing test.
4. Verify with the narrow test, then the affected suite.
5. Stop when the requested improvement is complete; do not turn a fix into a rewrite.

## Scope discipline

Touch only what the task requires. If you notice an unrelated problem, record it as `Noticed, not touching: <path:line> — <issue>` and leave it for a separate task. Do not combine a refactor with a feature or bug fix unless the change cannot be separated safely; if mixed, explain why. Do not modernize, reformat, or clean adjacent code because it is convenient.

## Simplicity check

Before adding an abstraction, ask:

- What is the simplest thing that could work now?
- Does this abstraction earn its complexity, or is it speculative?
- Would a staff engineer ask why this is not a direct function?
- Am I building for a hypothetical future requirement?
- Can a branch, mode, or wrapper be deleted instead of polished?

Three similar lines are often better than a premature abstraction. Prove correctness first; optimize or generalize only with evidence.

## Heuristics

- **Names:** say what the thing is or does, in domain language. Avoid encodings, vague `data`/`manager`, and misleading type words.
- **Functions:** one job at one level of abstraction. Small is useful, not a line-count contest. Keep side effects explicit.
- **Arguments:** fewer is usually clearer. Replace boolean flags and long positional lists with a named object or separate operation when it improves the contract.
- **Boundaries:** keep parsing, validation, business rules, I/O, and presentation separate. Do not let a low-level detail leak into a policy layer.
- **Errors:** handle failure explicitly at the boundary; do not swallow it, return ambiguous sentinels, or log and continue when the caller must know. Preserve context in the error.
- **Null/optional:** make absence explicit in the type or contract where the language supports it. Do not return null as an implicit "not found" without documenting it.
- **Comments:** explain why, constraints, and non-obvious intent. Do not narrate the code. Keep legal, security, and external-format notes.
- **Duplication:** remove duplicated knowledge, not coincidentally similar lines. Prefer a named concept over a copy.
- **Coupling:** depend on the smallest interface. Avoid train wrecks and hidden global state. Keep data and behavior together where the language encourages it.
- **Dead code:** delete code that is proven unused; do not keep commented-out versions or compatibility shims without a migration reason. When reachability is uncertain (public exports, dynamic dispatch, reflection, or pasted snippets without full callers), list the candidates and confirm before deleting.
- **Pasted snippets or diffs:** this skill also applies to pasted code or diffs; state any missing repository-convention context explicitly.
- **Formatting:** use the project's formatter and structure. High-level flow first, details below.
- **Objects and data:** keep invariants with the behavior that protects them; expose data only when it is a deliberate DTO/boundary. Avoid asking an object for its internals and then doing its job elsewhere.
- **Classes/modules:** one reason to change is a useful test. A module should tell a coherent story and hide its implementation behind a small interface.
- **Tests:** follow F.I.R.S.T. where practical — fast, independent, repeatable, self-validating, timely. Test behavior, not private structure.

## Refactor loop

1. Establish a green baseline or record the existing failure.
2. Add or identify a test that protects the behavior being changed.
3. Make one small structural change.
4. Run the narrow test and affected suite.
5. Commit the refactor separately from behavior changes.
6. Repeat only while it serves the task.

Do not mix a refactor with a feature or bug fix unless the change cannot be separated safely; if mixed, explain why.

## Smells to investigate

Rigidity, fragility, immobility, viscosity, needless complexity, needless repetition, opaque names, mixed abstraction, primitive obsession, feature envy, temporal coupling, hidden temporal dependencies, and tests that mirror implementation instead of behavior. A smell is a question, not an automatic rewrite.

## Language exceptions

- A short function is not always better if it fragments a single coherent operation.
- Exceptions versus result types, nullability, argument counts, and class size depend on the language and repository.
- Performance-critical code may use a less "pretty" shape when measurement justifies it; document the tradeoff.
- Generated code, vendored code, and narrow compatibility layers may follow different rules.

## Checklist

- [ ] Names are domain-specific and searchable.
- [ ] Each unit has one understandable job.
- [ ] Failure and empty paths are explicit.
- [ ] Comments explain why, not what.
- [ ] Duplication represents shared knowledge, not coincidence.
- [ ] No dead or commented-out code was left behind.
- [ ] Relevant tests pass; new behavior has coverage.
- [ ] The diff is scoped to the request; unrelated findings are recorded, not fixed.
- [ ] The simplest working shape was chosen; abstractions are justified.

## Handoff

Use `test-driven-development` before changing behavior and `code-review` for the final diff.
