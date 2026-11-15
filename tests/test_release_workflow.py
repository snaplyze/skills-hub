"""Contract tests for the release workflow ordering and safe trigger."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def load_workflow() -> tuple[dict, str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    return yaml.safe_load(text), text


def test_release_is_dispatched_from_main_not_tag_push() -> None:
    data, _ = load_workflow()
    triggers = data.get("on", data.get(True))
    assert set(triggers) == {"workflow_dispatch"}
    assert "tag" in triggers["workflow_dispatch"]["inputs"]
    job = data["jobs"]["release"]
    assert job["if"] == "github.ref == 'refs/heads/main'"


def test_trust_checks_precede_tag_controlled_code() -> None:
    data, _ = load_workflow()
    names = [step.get("name", "") for step in data["jobs"]["release"]["steps"]]
    signature = names.index("Verify signed tag")
    ancestry = names.index("Verify tag commit is on main")
    checks = names.index("Verify required check-runs")
    notes = names.index("Validate tag and extract release notes")
    assert signature < ancestry < checks < notes


def test_release_is_draft_and_has_provenance() -> None:
    _, text = load_workflow()
    assert "--draft" in text
    assert "actions/attest-build-provenance@" in text
    assert "args+=(--latest)" not in text
    assert "gate/scripts/release_checks.py" in text
    assert "actions: read" in text
    assert "ref: main" in text
    assert "path: gate" in text
