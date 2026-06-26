from __future__ import annotations

from pathlib import Path

from outcome_engineering.example import create_example
from outcome_engineering.graph import create_node, find_node, find_nodes_by_kind, marker_content, node_ancestors, supporting_files, validate
from outcome_engineering.skill_installer import install_skill, install_skill_for_agent


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


def test_create_node_builds_valid_graph(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup-is-confusing", title=None, under=outcome.id)
    solution = create_node(root, kind="solution", slug="setup-wizard", title=None, under=opportunity.id)
    assumption = create_node(root, kind="assumption", slug="wizard-reduces-confusion", title=None, under=solution.id)
    experiment = create_node(root, kind="experiment", slug="prototype-test", title=None, under=assumption.id)
    prd = create_node(root, kind="prd", slug="setup-wizard-mvp", title=None, under=solution.id)

    assert validate(root) == []
    assert outcome.marker_file == root / "outcomes" / "activation" / "OUTCOME.md"
    assert experiment.marker_file == assumption.path / "experiments" / "prototype-test" / "EXPERIMENT.md"
    assert prd.marker_file == solution.path / "prds" / "setup-wizard-mvp" / "PRD.md"


def test_create_experiment_requires_assumption_parent(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup-is-confusing", title=None, under=outcome.id)
    solution = create_node(root, kind="solution", slug="setup-wizard", title=None, under=opportunity.id)

    try:
        create_node(root, kind="experiment", slug="prototype-test", title=None, under=solution.id)
    except ValueError as error:
        assert "cannot create experiment under solution" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_find_node_and_ancestors(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    node = find_node(root, "solution.agent-central")

    assert node is not None
    assert [ancestor.id for ancestor in node_ancestors(node)] == [
        "outcome.delegation-confidence",
        "opportunity.agents-lack-safe-access-to-tools",
    ]


def test_find_nodes_by_kind(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    solutions = find_nodes_by_kind(root, "solution")

    assert [node.id for node in solutions] == ["solution.agent-central", "solution.delegation-interview"]


def test_marker_content_and_supporting_files(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)
    node = find_node(root, "opportunity.users-do-not-know-what-to-delegate")

    assert node is not None
    assert "# Users Do Not Know What To Delegate" in marker_content(node)
    assert [path.name for path in supporting_files(node)] == ["interview-patterns.md"]


def test_install_skill(tmp_path: Path) -> None:
    target = tmp_path / "skills" / "oe-cli"

    installed_at = install_skill(target=target)

    assert installed_at == target
    assert (target / "SKILL.md").exists()
    assert "name: oe-cli" in (target / "SKILL.md").read_text(encoding="utf-8")


def test_install_skill_for_agents(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude"))

    installed = install_skill_for_agent("all")

    assert installed == [
        tmp_path / "codex" / "skills" / "oe-cli",
        tmp_path / "claude" / "skills" / "oe-cli",
    ]
    assert (tmp_path / "codex" / "skills" / "oe-cli" / "SKILL.md").exists()
    assert (tmp_path / "claude" / "skills" / "oe-cli" / "SKILL.md").exists()
