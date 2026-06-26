from __future__ import annotations

from pathlib import Path

from outcome_engineering.example import create_example
from outcome_engineering.graph import validate


def test_example_graph_is_valid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    assert validate(root) == []


def test_experiments_must_belong_to_assumptions(tmp_path: Path) -> None:
    root = tmp_path / "product"
    experiment = root / "outcomes" / "activation" / "opportunities" / "setup" / "solutions" / "wizard" / "experiments" / "test"
    experiment.mkdir(parents=True)
    (root / "outcomes" / "activation").mkdir(parents=True, exist_ok=True)
    (root / "outcomes" / "activation" / "OUTCOME.md").write_text("# Activation\n", encoding="utf-8")
    (root / "outcomes" / "activation" / "opportunities" / "setup").mkdir(parents=True, exist_ok=True)
    (root / "outcomes" / "activation" / "opportunities" / "setup" / "OPPORTUNITY.md").write_text("# Setup\n", encoding="utf-8")
    (root / "outcomes" / "activation" / "opportunities" / "setup" / "solutions" / "wizard").mkdir(parents=True, exist_ok=True)
    (root / "outcomes" / "activation" / "opportunities" / "setup" / "solutions" / "wizard" / "SOLUTION.md").write_text("# Wizard\n", encoding="utf-8")
    (experiment / "EXPERIMENT.md").write_text("# Test\n", encoding="utf-8")

    issues = validate(root)

    assert any("experiments/ is not allowed under solution" in issue.message for issue in issues)
    assert any("experiments can only live under an assumption" in issue.message for issue in issues)

