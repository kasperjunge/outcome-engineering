from __future__ import annotations

from importlib import resources
from pathlib import Path

from typer.testing import CliRunner

from outcome_engineering import cli
from outcome_engineering.example import create_example
from outcome_engineering.graph import (
    create_node,
    delete_node,
    find_node,
    find_nodes_by_kind,
    marker_content,
    node_ancestors,
    node_icp_references,
    parse_icp_references,
    related_icps,
    supporting_files,
    validate,
    write_marker,
)
from outcome_engineering.serve import build_graph_payload, make_server
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


def test_comprehensive_example_graph_is_valid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False, comprehensive=True)

    assert validate(root) == []


def test_comprehensive_example_exercises_ui_payload(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False, comprehensive=True)

    payload = build_graph_payload(root)
    ids = {node["id"] for node in payload["nodes"]}
    statuses = {node["status"] for node in payload["nodes"]}
    icp_edges = [edge for edge in payload["edges"] if edge["type"] == "icp"]
    structural_edges = [edge for edge in payload["edges"] if edge["type"] == "structural"]

    assert len(payload["nodes"]) >= 40
    assert "icp.enterprise-product-ops" in ids
    assert "outcome.agent-legible-product-memory" in ids
    assert "prd.traceable-prd-panel-mvp" in ids
    assert {"active", "planned", "shipped", "blocked"} <= statuses
    assert len(icp_edges) >= 6
    assert len(structural_edges) >= 30
    assert payload["vision"] and payload["strategy"]


def test_boligsiden_example_graph_is_valid(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False, boligsiden=True)

    assert validate(root) == []


def test_boligsiden_example_exercises_marketplace_payload(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False, boligsiden=True)

    payload = build_graph_payload(root)
    ids = {node["id"] for node in payload["nodes"]}
    icp_edges = [edge for edge in payload["edges"] if edge["type"] == "icp"]
    structural_edges = [edge for edge in payload["edges"] if edge["type"] == "structural"]

    assert len(payload["nodes"]) >= 45
    assert "icp.active-home-buyer" in ids
    assert "icp.estate-agent" in ids
    assert "outcome.buyer-search-confidence" in ids
    assert "outcome.seller-market-readiness" in ids
    assert "outcome.market-transparency-trust" in ids
    assert "prd.smart-alerts-mvp" in ids
    assert "prd.agent-fit-comparison-mvp" in ids
    assert len(icp_edges) >= 5
    assert len(structural_edges) >= 35
    assert "simulated" in payload["strategy"]


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


def test_build_graph_payload_exposes_placement_schema(tmp_path: Path) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    schema = build_graph_payload(root)["schema"]["childKinds"]

    assert schema["root"] == ["icp", "outcome"]
    assert schema["outcome"] == ["opportunity"]
    assert schema["solution"] == ["assumption-test", "prd"]


def test_write_marker_overwrites_node_content(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()
    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)

    node = write_marker(root, outcome.id, "# Activation\n\nEdited body.")

    assert node.id == outcome.id
    assert marker_content(node) == "# Activation\n\nEdited body.\n"


def test_write_marker_unknown_selector_raises(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()

    try:
        write_marker(root, "outcome.missing", "# X\n")
    except ValueError as error:
        assert "not found" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_delete_node_removes_leaf(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()
    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    opportunity = create_node(root, kind="opportunity", slug="setup", title=None, under=outcome.id)

    delete_node(root, opportunity.id)

    assert not opportunity.path.exists()
    assert find_node(root, outcome.id) is not None
    assert validate(root) == []


def test_delete_node_with_children_requires_cascade(tmp_path: Path) -> None:
    root = tmp_path / "product"
    root.mkdir()
    outcome = create_node(root, kind="outcome", slug="activation", title=None, under=None)
    create_node(root, kind="opportunity", slug="setup", title=None, under=outcome.id)

    try:
        delete_node(root, outcome.id)
    except ValueError as error:
        assert "has children" in str(error)
    else:
        raise AssertionError("expected ValueError")

    delete_node(root, outcome.id, cascade=True)
    assert not outcome.path.exists()


def test_server_serves_ui_and_graph_api(tmp_path: Path) -> None:
    import json
    import threading
    from urllib.request import urlopen

    root = tmp_path / "product"
    create_example(root, force=False)

    server = make_server(root, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        page = urlopen(base + "/").read().decode("utf-8")
        assert "/api/graph" in page  # the UI fetches its data live

        payload = json.loads(urlopen(base + "/api/graph").read().decode("utf-8"))
        ids = {node["id"] for node in payload["nodes"]}
        assert "outcome.delegation-confidence" in ids
        assert payload["schema"]["childKinds"]["root"] == ["icp", "outcome"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_server_handles_favicon_without_browser_console_404(tmp_path: Path) -> None:
    import threading
    from urllib.request import urlopen

    root = tmp_path / "product"
    create_example(root, force=False)

    server = make_server(root, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        response = urlopen(base + "/favicon.ico")

        assert response.status == 204
        assert response.read() == b""
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_graph_template_keeps_focus_toggles_attached_to_nodes() -> None:
    page = (resources.files("outcome_engineering") / "templates" / "graph.html").read_text(encoding="utf-8")

    assert 'class: "toggle", transform: `translate(${x},${y + NODE_H / 2 + 12})`' in page


def test_graph_template_keeps_invalid_edits_recoverable() -> None:
    page = (resources.files("outcome_engineering") / "templates" / "graph.html").read_text(encoding="utf-8")

    assert "if (res.data.issues && res.data.issues.length)" in page
    assert "save.disabled = false;" in page
    assert "clearIssues();" in page


def test_serve_command_reports_bind_failure_without_traceback(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "product"
    create_example(root, force=False)

    def fail_bind(*args, **kwargs) -> None:
        raise OSError(48, "Address already in use")

    monkeypatch.setattr(cli, "serve_graph", fail_bind)

    result = CliRunner().invoke(cli.app, ["serve", str(root), "--host", "127.0.0.1", "--port", "8765", "--no-open"])

    assert result.exit_code == 1
    assert "Could not bind 127.0.0.1:8765" in result.output
    assert "Traceback" not in result.output


def test_server_create_edit_delete_round_trip(tmp_path: Path) -> None:
    import json
    import threading
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

    root = tmp_path / "product"
    root.mkdir()

    server = make_server(root, host="127.0.0.1", port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    def call(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = Request(base + path, data=data, method=method, headers={"Content-Type": "application/json"})
        try:
            with urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8"))

    try:
        status, created = call("POST", "/api/nodes", {"kind": "outcome", "slug": "activation", "title": "Activation"})
        assert status == 201 and created["id"] == "outcome.activation"

        # illegal placement is rejected, graph untouched
        status, err = call("POST", "/api/nodes", {"kind": "prd", "slug": "x", "under": "outcome.activation"})
        assert status == 400 and "cannot create prd under outcome" in err["error"]

        status, edited = call("PUT", "/api/nodes/outcome.activation", {"content": "# Activation\n\nNew body.\n"})
        assert status == 200 and edited["issues"] == []
        assert "New body." in (root / "outcomes" / "activation" / "OUTCOME.md").read_text(encoding="utf-8")

        call("POST", "/api/nodes", {"kind": "opportunity", "slug": "setup", "under": "outcome.activation"})
        status, err = call("DELETE", "/api/nodes/outcome.activation")
        assert status == 400 and "has children" in err["error"]

        status, _ = call("DELETE", "/api/nodes/outcome.activation?cascade=true")
        assert status == 200
        assert not (root / "outcomes" / "activation").exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
