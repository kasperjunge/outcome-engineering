from __future__ import annotations

from typing import TYPE_CHECKING

from outcome_engineering.product_graph.discovery import marker_content, title_from_markdown
from outcome_engineering.product_graph.frontmatter import parse_frontmatter_scalar, parse_icp_references
from outcome_engineering.product_graph.model import PARENT_KIND_TO_CHILD_KIND, ProductNode
from outcome_engineering.product_graph.render import context_markdown

if TYPE_CHECKING:
    from pathlib import Path

    from outcome_engineering.product_graph.core import ProductGraph

NODE_KINDS = ("vision", "strategy", "icp", "outcome", "opportunity", "solution", "assumption-test", "prd")

SUMMARY_KEYS = ("id", "kind", "slug", "title", "status", "marker", "path")


def status_from_body(text: str) -> str | None:
    return parse_frontmatter_scalar(text, "status")


def issue_dicts(graph: ProductGraph) -> list[dict]:
    return [
        {
            "path": _relative_or_absolute(issue.path, graph.root),
            "message": issue.message,
        }
        for issue in graph.validate()
    ]


def build_graph_payload(graph: ProductGraph, *, read_only: bool = False) -> dict:
    root = graph.root
    discovered = graph.nodes()

    nodes: list[dict] = []
    edges: list[dict] = []
    icp_served_by: dict[str, list[str]] = {}

    for node in discovered:
        if node.kind not in NODE_KINDS:
            continue
        node_payload_dict = node_payload(root, node)
        node_payload_dict["deletable"] = node.path != root and not read_only
        nodes.append(node_payload_dict)
        if node.parent is not None:
            edges.append({"source": node.parent.id, "target": node.id, "type": "structural"})
        add_icp_edges(node.id, node_payload_dict["icps"], edges, icp_served_by)

    for node in nodes:
        if node["kind"] == "icp":
            node["servedBy"] = icp_served_by.get(node["id"], [])

    return {
        "root": root.name,
        "readOnly": read_only,
        "vision": _root_marker_text(discovered, "vision"),
        "strategy": _root_marker_text(discovered, "strategy"),
        "flywheel": flywheel_payload(graph),
        "schema": placement_schema(),
        "nodes": nodes,
        "edges": edges,
    }


def add_icp_edges(node_id: str, icp_refs: list[str], edges: list[dict], icp_served_by: dict[str, list[str]]) -> None:
    for ref in icp_refs:
        edges.append({"source": node_id, "target": ref, "type": "icp"})
        icp_served_by.setdefault(ref, [])
        if node_id not in icp_served_by[ref]:
            icp_served_by[ref].append(node_id)


def placement_schema() -> dict:
    return {
        "childKinds": {
            parent: sorted(child for child in children if child in NODE_KINDS)
            for parent, children in PARENT_KIND_TO_CHILD_KIND.items()
        }
    }


def list_nodes(graph: ProductGraph, kind: str | None = None) -> dict:
    nodes = [node for node in graph.nodes() if node.kind in NODE_KINDS]
    if kind is not None:
        nodes = [node for node in nodes if node.kind == kind]
    return {
        "nodes": [node_payload(graph.root, node) for node in sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))],
    }


def show_node(graph: ProductGraph, selector: str) -> dict:
    return {
        "node": node_payload(graph.root, graph.resolve(selector)),
    }


def trace_node(graph: ProductGraph, selector: str) -> dict:
    node = graph.resolve(selector)
    ancestors = graph.ancestors(node)
    return {
        "node": node_payload(graph.root, node),
        "trace": [node_summary(graph.root, ancestor) for ancestor in [*ancestors, node]],
        "children": [node_summary(graph.root, child) for child in node.children],
    }


def context_node(graph: ProductGraph, selector: str) -> dict:
    root = graph.root
    node = graph.resolve(selector)
    ancestors = graph.ancestors(node)
    icps = graph.related_icps(node, ancestors)
    files = graph.supporting_files(node)
    flywheel = graph.flywheel_context()

    return {
        "node": node_payload(root, node),
        "trace": [node_summary(root, ancestor) for ancestor in [*ancestors, node]],
        "icps": [node_payload(root, icp) for icp in icps],
        "children": [node_summary(root, child) for child in node.children],
        "supportingFiles": [_relative_or_absolute(path, root) for path in files],
        "flywheelContext": flywheel,
        "ancestors": [node_payload(root, ancestor) for ancestor in ancestors],
        "markdown": context_markdown(node, ancestors, icps, files, flywheel),
    }


def validation_payload(graph: ProductGraph) -> dict:
    issues = issue_dicts(graph)
    return {
        "valid": not issues,
        "issues": issues,
    }


def node_payload(root: Path, node: ProductNode) -> dict:
    body = marker_content(node).rstrip()
    return {
        "id": node.id,
        "kind": node.kind,
        "slug": node.slug,
        "title": title_from_markdown(body, node.slug),
        "status": status_from_body(body),
        "parent": node.parent.id if node.parent is not None else None,
        "children": [child.id for child in node.children],
        "icps": parse_icp_references(body) if node.kind in {"outcome", "opportunity"} else [],
        "body": body,
        "marker": _relative_or_absolute(node.marker_file, root),
        "path": _relative_or_absolute(node.path, root),
    }


def node_summary(root: Path, node: ProductNode) -> dict:
    payload = node_payload(root, node)
    return {key: payload[key] for key in SUMMARY_KEYS}


def flywheel_payload(graph: ProductGraph) -> dict | None:
    flywheel = graph.flywheel()
    if flywheel is None:
        return None
    return {
        "id": flywheel.id,
        "slug": flywheel.slug,
        "title": flywheel.title,
        "status": flywheel.status,
        "body": flywheel.body,
        "nodes": [
            {
                "id": node.id,
                "slug": node.slug,
                "title": node.title,
                "status": node.status,
                "body": node.body,
                "next": node.next,
            }
            for node in flywheel.nodes
        ],
    }


def _root_marker_text(nodes: list[ProductNode], kind: str) -> str:
    for node in nodes:
        if node.kind == kind:
            return marker_content(node).rstrip()
    return ""


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
