from __future__ import annotations

from pathlib import Path

from outcome_engineering.example import create_example
from outcome_engineering.graph import (
    create_node,
    find_node,
    find_nodes_by_kind,
    marker_content,
    node_ancestors,
    node_icp_references,
    parse_icp_references,
    related_icps,
    supporting_files,
    validate,
)
from outcome_engineering.viz import build_graph_payload, render_html
from outcome_engineering.cli import parse_skills_option
from outcome_engineering.skill_installer import (
    SKILL_NAMES,
    install_project_skill,
    install_project_skills,
    install_skill,
    install_skill_for_agent,
    install_skills_for_agent,
)


def test_example_graph_is_valid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    assert validate(root) == []


def test_assumption_tests_must_belong_to_solutions(tmp_path: Path) -> None:
    root = tmp_path / "product"
    assumption_test = root / "outcomes" / "activation" / "opportunities" / "setup" / "assumption-tests" / "test"
    assumption_test.mkdir(parents=True)
    (root / "outcomes" / "activation" / "OUTCOME.md").write_text("# Activation\n", encoding="utf-8")
    (root / "outcomes" / "activation" / "opportunities" / "setup" / "OPPORTUNITY.md").write_text("# Setup\n", encoding="utf-8")
    (assumption_test / "ASSUMPTION_TEST.md").write_text("# Test\n", encoding="utf-8")

    issues = validate(root)

    assert any("assumption-tests/ is not allowed under opportunity" in issue.message for issue in issues)


def test_create_node_builds_valid_graph(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup-is-confusing", title=None, under=outcome.id)
    solution = create_node(root, kind="solution", slug="setup-wizard", title=None, under=opportunity.id)
    assumption_test = create_node(root, kind="assumption-test", slug="wizard-reduces-confusion", title=None, under=solution.id)
    prd = create_node(root, kind="prd", slug="setup-wizard-mvp", title=None, under=solution.id)

    assert validate(root) == []
    assert outcome.marker_file == root / "outcomes" / "activation" / "OUTCOME.md"
    assert assumption_test.marker_file == solution.path / "assumption-tests" / "wizard-reduces-confusion" / "ASSUMPTION_TEST.md"
    assert prd.marker_file == solution.path / "prds" / "setup-wizard-mvp" / "PRD.md"


def test_opportunity_children_are_ordered_problem_then_solution(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup-is-confusing", title=None, under=outcome.id)
    create_node(root, kind="solution", slug="setup-wizard", title=None, under=opportunity.id)
    create_node(root, kind="opportunity", slug="unclear-first-step", title=None, under=opportunity.id)

    node = find_node(root, opportunity.id)

    assert node is not None
    assert [(child.kind, child.slug) for child in node.children] == [
        ("opportunity", "unclear-first-step"),
        ("solution", "setup-wizard"),
    ]


def test_create_assumption_test_requires_solution_parent(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup-is-confusing", title=None, under=outcome.id)

    try:
        create_node(root, kind="assumption-test", slug="setup-pain-is-frequent", title=None, under=opportunity.id)
    except ValueError as error:
        assert "cannot create assumption-test under opportunity" in str(error)
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


def test_parse_icp_references_block_and_inline() -> None:
    block = """# Outcome

```yaml
type: outcome
id: outcome.x
icps:
  - icp.a
  - icp.b
status: draft
```
"""
    inline = """# Outcome

```yaml
type: outcome
id: outcome.x
icps: [icp.a, "icp.b"]
status: draft
```
"""
    assert parse_icp_references(block) == ["icp.a", "icp.b"]
    assert parse_icp_references(inline) == ["icp.a", "icp.b"]


def test_create_icp_lives_under_root_collection(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    icp = create_node(root, kind="icp", slug="smb-ops-lead", title=None, under=None)

    assert icp.marker_file == root / "icps" / "smb-ops-lead" / "ICP.md"
    assert validate(root) == []


def test_create_icp_rejects_under(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    try:
        create_node(root, kind="icp", slug="smb-ops-lead", title=None, under="outcome.x")
    except ValueError as error:
        assert "cannot use --under" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_example_graph_resolves_icp_inherited_through_ancestors(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    outcome = find_node(root, "outcome.delegation-confidence")
    solution = find_node(root, "solution.delegation-interview")

    assert outcome is not None and solution is not None
    assert node_icp_references(outcome) == ["icp.solo-knowledge-worker"]
    inherited = related_icps(root, solution, node_ancestors(solution))
    assert [icp.id for icp in inherited] == ["icp.solo-knowledge-worker"]


def test_unknown_icp_reference_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)
    outcome_marker = root / "outcomes" / "delegation-confidence" / "OUTCOME.md"
    outcome_marker.write_text(
        outcome_marker.read_text(encoding="utf-8").replace("icp.solo-knowledge-worker", "icp.does-not-exist"),
        encoding="utf-8",
    )

    issues = validate(root)

    assert any("does not resolve to a known ICP" in issue.message for issue in issues)


def test_icp_reference_only_allowed_on_outcome_and_opportunity(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)
    solution_marker = root / "outcomes" / "delegation-confidence" / "opportunities" / "agents-lack-safe-access-to-tools" / "solutions" / "agent-central" / "SOLUTION.md"
    text = solution_marker.read_text(encoding="utf-8")
    solution_marker.write_text(text.replace("id: solution.agent-central\n", "id: solution.agent-central\nicps: [icp.solo-knowledge-worker]\n"), encoding="utf-8")

    issues = validate(root)

    assert any("solution cannot reference ICPs" in issue.message for issue in issues)


def test_misplaced_icp_marker_is_invalid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)
    stray = root / "outcomes" / "delegation-confidence" / "icps" / "stray"
    stray.mkdir(parents=True)
    (stray / "ICP.md").write_text("# Stray\n", encoding="utf-8")

    issues = validate(root)

    assert any("only valid directly under icps/" in issue.message for issue in issues)


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


def test_install_skills_for_agents_installs_bundled_skills(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex"))
    monkeypatch.setenv("CLAUDE_HOME", str(tmp_path / "claude"))

    installed = install_skills_for_agent("all")

    assert installed == [
        *(tmp_path / "codex" / "skills" / skill_name for skill_name in SKILL_NAMES),
        *(tmp_path / "claude" / "skills" / skill_name for skill_name in SKILL_NAMES),
    ]
    for agent in ("codex", "claude"):
        for skill_name in SKILL_NAMES:
            assert (tmp_path / agent / "skills" / skill_name / "SKILL.md").exists()


def test_install_project_skill_targets_playwright_style_dirs(tmp_path: Path) -> None:
    claude_target = install_project_skill("claude", cwd=tmp_path)
    agents_target = install_project_skill("agents", cwd=tmp_path, force=True)

    assert claude_target == tmp_path / ".claude" / "skills" / "oe-cli"
    assert agents_target == tmp_path / ".agents" / "skills" / "oe-cli"
    assert (claude_target / "SKILL.md").exists()
    assert (agents_target / "SKILL.md").exists()


def test_install_project_skills_targets_playwright_style_dirs(tmp_path: Path) -> None:
    claude_targets = install_project_skills("claude", cwd=tmp_path)
    agents_targets = install_project_skills("agents", cwd=tmp_path, force=True)

    assert claude_targets == [tmp_path / ".claude" / "skills" / skill_name for skill_name in SKILL_NAMES]
    assert agents_targets == [tmp_path / ".agents" / "skills" / skill_name for skill_name in SKILL_NAMES]
    for skill_name in SKILL_NAMES:
        assert (tmp_path / ".claude" / "skills" / skill_name / "SKILL.md").exists()
        assert (tmp_path / ".agents" / "skills" / skill_name / "SKILL.md").exists()


def test_parse_skills_option() -> None:
    assert parse_skills_option(["--skills"]) == "claude"
    assert parse_skills_option(["--skills=agents"]) == "agents"


def test_build_graph_payload_separates_structural_and_icp_edges(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    payload = build_graph_payload(root)

    ids = {node["id"] for node in payload["nodes"]}
    assert "outcome.delegation-confidence" in ids
    assert "icp.solo-knowledge-worker" in ids
    # vision/strategy are prose context, not nodes
    assert all(node["kind"] != "vision" and node["kind"] != "strategy" for node in payload["nodes"])
    assert payload["vision"] and payload["strategy"]

    structural = {(e["source"], e["target"]) for e in payload["edges"] if e["type"] == "structural"}
    icp_edges = {(e["source"], e["target"]) for e in payload["edges"] if e["type"] == "icp"}
    assert ("outcome.delegation-confidence", "opportunity.users-do-not-know-what-to-delegate") in structural
    assert ("outcome.delegation-confidence", "icp.solo-knowledge-worker") in icp_edges

    icp_node = next(node for node in payload["nodes"] if node["id"] == "icp.solo-knowledge-worker")
    assert icp_node["servedBy"] == ["outcome.delegation-confidence"]


def test_render_html_is_self_contained(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    html = render_html(build_graph_payload(root))

    assert "__GRAPH_DATA__" not in html
    assert "__GRAPH_TITLE__" not in html
    assert "Delegation Confidence" in html
    # no external dependencies: nothing fetched over the network
    assert "http://" not in html.replace("http://www.w3.org/2000/svg", "")
    assert "https://" not in html
    assert "src=" not in html
