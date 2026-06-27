from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from outcome_engineering.graph import (
    discover_nodes,
    marker_content,
    parse_icp_references,
)

# Kinds that are rendered as graph nodes. vision/strategy are prose context, not
# nodes in the node-link graph, so they are surfaced as panel content instead.
NODE_KINDS = ("icp", "outcome", "opportunity", "solution", "assumption-test", "prd")

DATA_PLACEHOLDER = "__GRAPH_DATA__"
TITLE_PLACEHOLDER = "__GRAPH_TITLE__"


def _title_from_body(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def _status_from_body(text: str) -> str | None:
    inside = False
    for line in text.splitlines():
        marker = line.strip()
        if marker.startswith("```"):
            if inside:
                break
            inside = marker.startswith("```yaml")
            continue
        if inside and marker.startswith("status:"):
            return marker[len("status:") :].strip() or None
    return None


def _root_marker_text(nodes: list, kind: str) -> str:
    for node in nodes:
        if node.kind == kind:
            return marker_content(node).rstrip()
    return ""


def build_graph_payload(root: Path) -> dict:
    """Serialize the discovered product graph into a render-ready payload.

    The payload separates the two edge meanings the model defines: structural
    parent->child trace edges, and many-to-many ICP reference edges. vision and
    strategy are returned as prose context rather than nodes.
    """
    root = root.resolve()
    discovered = discover_nodes(root)

    nodes: list[dict] = []
    edges: list[dict] = []
    icp_served_by: dict[str, list[str]] = {}

    for node in discovered:
        if node.kind not in NODE_KINDS:
            continue
        body = marker_content(node).rstrip()
        icp_refs = parse_icp_references(body) if node.kind in {"outcome", "opportunity"} else []
        nodes.append(
            {
                "id": node.id,
                "kind": node.kind,
                "slug": node.slug,
                "title": _title_from_body(body, node.slug),
                "status": _status_from_body(body),
                "parent": node.parent.id if node.parent is not None else None,
                "icps": icp_refs,
                "body": body,
            }
        )
        if node.parent is not None:
            edges.append({"source": node.parent.id, "target": node.id, "type": "structural"})
        for ref in icp_refs:
            edges.append({"source": node.id, "target": ref, "type": "icp"})
            icp_served_by.setdefault(ref, [])
            if node.id not in icp_served_by[ref]:
                icp_served_by[ref].append(node.id)

    for node in nodes:
        if node["kind"] == "icp":
            node["servedBy"] = icp_served_by.get(node["id"], [])

    return {
        "root": root.name,
        "vision": _root_marker_text(discovered, "vision"),
        "strategy": _root_marker_text(discovered, "strategy"),
        "nodes": nodes,
        "edges": edges,
    }


def _load_template() -> str:
    return (resources.files("outcome_engineering") / "templates" / "graph.html").read_text(encoding="utf-8")


def render_html(payload: dict) -> str:
    """Inline the payload into the self-contained HTML template.

    The result has no external dependencies and opens directly from file://.
    """
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    # Keep the JSON from breaking out of the <script> element it is embedded in.
    data = data.replace("</", "<\\/")
    title = payload.get("root") or "product"
    return _load_template().replace(DATA_PLACEHOLDER, data).replace(TITLE_PLACEHOLDER, title)
