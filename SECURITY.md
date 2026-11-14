# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| `1.x` (latest release) | Yes |
| Older releases | No |

Security fixes are applied to the latest release and `main`.

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

Use GitHub's private vulnerability reporting:

- [Report a vulnerability privately](https://github.com/snaplyze/skills-hub/security/advisories/new)
- [Security overview](https://github.com/snaplyze/skills-hub/security)

1. Open the private advisory form.
2. Include the details below.
3. Do not disclose the issue publicly until a fix and disclosure date are agreed.

If private reporting is unavailable, contact the maintainer privately through
their GitHub profile and ask for a secure channel. Do not include exploit
details in a public issue.

## What to include

- A short description of the issue and its impact.
- Affected skill, script, workflow, or installer path.
- Reproduction steps or a minimal proof of concept.
- Affected versions or commit range.
- Any known mitigations.
- Whether you want public credit, and under what name.

## Scope

In scope:

- skill instructions that could cause unsafe or destructive behavior;
- the OpenCode installer and any future harness installers;
- validation and CI scripts;
- GitHub Actions workflows and repository configuration;
- documentation that gives unsafe guidance.

Out of scope:

- vulnerabilities in third-party tools, agents, or libraries;
- issues in projects where a skill is used;
- social engineering, spam, or denial-of-service testing;
- secrets or personal data found in user projects.

## Response

- Acknowledge receipt within 3 business days.
- Triage and confirm scope within 7 business days where possible.
- Coordinate a fix and disclosure date based on severity and complexity.
- Credit reporters who want credit, unless they prefer to remain anonymous.

## Safe harbor

Good-faith security research is welcome. Do not access, modify, or exfiltrate
data that is not yours; do not degrade service; do not use social engineering.
If you are unsure whether a test is acceptable, ask first.

## Security controls in this repository

- Secret scanning and push protection are enabled.
- Dependabot alerts and security updates are enabled.
- CodeQL code scanning runs on `main` and pull requests.
- OpenSSF Scorecard runs weekly.
- `main` requires pull requests, passing checks, resolved conversations, linear
  history, and blocks force pushes and deletions.
- GitHub Actions use least-privilege permissions and pinned action commits.
