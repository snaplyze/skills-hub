---
name: Test-Driven Development
description: "Use when implementing a feature, behavior change, or bugfix that can be expressed as a failing test. Requires red-green-refactor: write a behavioral test, watch it fail for the right reason, write the minimal implementation, then refactor with the suite green. Not for documentation-only or purely visual changes that cannot be asserted meaningfully."
license: MIT
compatibility: opencode
---

# Test-Driven Development

## The iron law

Do not write production code without a failing test that demands it, unless the task is impossible to test mechanically and the gap is explicitly reported. Code written before the test is deleted or moved behind a failing test before it is kept.

The three laws:

1. Do not write production code until a failing test exists.
2. Do not write more test than is sufficient to fail.
3. Do not write more production code than is sufficient to pass.

## The cycle

1. **Red:** write one small test for the next behavior. Run it. It must fail because the behavior is missing, not because the test is broken.
2. **Green:** write the minimum production code that makes that test pass. Do not add unrequested cases.
3. **Refactor:** improve names, duplication, and boundaries while keeping the suite green. Do not change behavior in the refactor.
4. Repeat with the next behavior.

If a new test passes immediately, either the behavior already exists or the test does not exercise it. Determine which before continuing.

## What makes a useful test

- It asserts observable behavior at a stable boundary, not private implementation details.
- It is deterministic, isolated, and fast enough to run during the loop.
- It has a clear name that states the scenario and expected result.
- It covers failure, empty, boundary, and permission behavior where relevant.
- It fails for one understandable reason.
- It does not depend on execution order or shared mutable state.

Use real collaborators when cheap; use fakes or mocks at external boundaries (network, clock, filesystem, payment, email) and verify the interaction only where the interaction is the contract.

## Bugfix flow

First reproduce the bug with a failing regression test. Confirm it fails against the current code for the reported reason. Then fix the cause and keep the test. Delete only tests that are proven redundant, not tests that are inconvenient.

## Test quality rules

- Prefer a few meaningful integration tests over many shallow unit tests that mirror classes.
- Do not chase coverage percentage; cover risks, branches, and failure modes.
- Avoid sleeps, wall-clock dependence, random data without a seed, and brittle snapshots.
- Assert the result and the important side effect; avoid asserting the number of internal calls unless that count is the contract.
- Keep fixtures small and local; do not hide setup in a shared mutable fixture.

## When a test is not feasible

For purely visual, exploratory, or environment-specific work, define a reproducible manual check and record the evidence. Do not pretend a manual check is an automated test. For a legacy area with no seam, add the narrowest characterization test or capture a deterministic fixture first.

## Red flags

- Production code written before the test.
- A test that was never run failing.
- Tests that assert private methods, call order, or log strings instead of behavior.
- A bug fix without a regression test.
- Weakening an assertion to make a green build.
- A suite that only passes in one order or on one machine.

## Handoff

Use `clean-code` for the refactor and `code-review` for the diff. Delivery requires the full suite, not only the new test. If a test cannot be written, get explicit agreement on the substitute and record it as NOT_TESTED.
