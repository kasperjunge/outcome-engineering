from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path

from outcome_engineering.product_graph.core import NodeResolutionError as NodeResolutionError, ProductGraph
from outcome_engineering.product_graph.discovery import marker_content, title_from_markdown
from outcome_engineering.product_graph.frontmatter import parse_frontmatter_scalar, parse_icp_references
from outcome_engineering.product_graph.model import PARENT_KIND_TO_CHILD_KIND, ProductNode

NODE_KINDS = ("vision", "strategy", "icp", "outcome", "opportunity", "solution", "assumption-test", "prd")


@dataclass(frozen=True)
class SourceMetadata:
    root: str
    branch: str
    commit: str
    generated_at: str

    @classmethod
    def from_root(cls, root: Path) -> "SourceMetadata":
        return cls(
            root=str(root.resolve()),
            branch=os.environ.get("OE_SOURCE_BRANCH") or os.environ.get("SOURCE_BRANCH") or "main",
            commit=os.environ.get("OE_SOURCE_COMMIT")
            or os.environ.get("SOURCE_COMMIT")
            or os.environ.get("GITHUB_SHA")
            or "unknown",
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "branch": self.branch,
            "commit": self.commit,
            "generatedAt": self.generated_at,
        }


def title_from_body(text: str, fallback: str) -> str:
    return title_from_markdown(text, fallback)


def status_from_body(text: str) -> str | None:
    return parse_frontmatter_scalar(text, "status")


def issue_dicts(root: Path) -> list[dict]:
    root = root.resolve()
    issues = []
    for issue in ProductGraph(root).validate():
        issues.append(
            {
                "path": _relative_or_absolute(issue.path, root),
                "message": issue.message,
            }
        )
    return issues


def build_graph_payload(root: Path, *, read_only: bool = False, include_source: bool = False) -> dict:
    root = root.resolve()
    graph = ProductGraph(root)
    discovered = graph.nodes()

    nodes: list[dict] = []
    edges: list[dict] = []
    icp_served_by: dict[str, list[str]] = {}

    for node in discovered:
        if node.kind not in NODE_KINDS:
            continue
        node_payload, icp_refs = graph_node_payload(root, node, read_only=read_only)
        nodes.append(node_payload)
        if node.parent is not None:
            edges.append({"source": node.parent.id, "target": node.id, "type": "structural"})
        add_icp_edges(node.id, icp_refs, edges, icp_served_by)

    for node in nodes:
        if node["kind"] == "icp":
            node["servedBy"] = icp_served_by.get(node["id"], [])

    payload = {
        "root": root.name,
        "readOnly": read_only,
        "vision": _root_marker_text(discovered, "vision"),
        "strategy": _root_marker_text(discovered, "strategy"),
        "flywheel": flywheel_payload(graph),
        "schema": placement_schema(),
        "nodes": nodes,
        "edges": edges,
    }
    if include_source:
        payload["source"] = SourceMetadata.from_root(root).to_dict()
    return payload


def graph_node_payload(root: Path, node: ProductNode, *, read_only: bool) -> tuple[dict, list[str]]:
    body = marker_content(node).rstrip()
    icp_refs = parse_icp_references(body) if node.kind in {"outcome", "opportunity"} else []
    return (
        {
            "id": node.id,
            "kind": node.kind,
            "slug": node.slug,
            "title": title_from_body(body, node.slug),
            "status": status_from_body(body),
            "parent": node.parent.id if node.parent is not None else None,
            "children": [child.id for child in node.children],
            "icps": icp_refs,
            "body": body,
            "marker": _relative_or_absolute(node.marker_file, root),
            "path": _relative_or_absolute(node.path, root),
            "deletable": node.path != root and not read_only,
        },
        icp_refs,
    )


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


def list_nodes(root: Path, kind: str | None = None) -> dict:
    root = root.resolve()
    graph = ProductGraph(root)
    nodes = [node for node in graph.nodes() if node.kind in NODE_KINDS]
    if kind is not None:
        nodes = [node for node in nodes if node.kind == kind]
    return {
        "nodes": [node_payload(root, node) for node in sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))],
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def show_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    graph = ProductGraph(root)
    return {
        "node": node_payload(root, graph.resolve(selector)),
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def trace_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    graph = ProductGraph(root)
    node = graph.resolve(selector)
    ancestors = graph.ancestors(node)
    return {
        "node": node_payload(root, node),
        "trace": [node_summary(root, ancestor) for ancestor in [*ancestors, node]],
        "children": [node_summary(root, child) for child in node.children],
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def context_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    graph = ProductGraph(root)
    node = graph.resolve(selector)
    ancestors = graph.ancestors(node)
    icps = graph.related_icps(node, ancestors)
    files = graph.supporting_files(node)
    flywheel = graph.flywheel_context()

    structured = {
        "node": node_payload(root, node),
        "trace": [node_summary(root, ancestor) for ancestor in [*ancestors, node]],
        "icps": [node_payload(root, icp) for icp in icps],
        "children": [node_summary(root, child) for child in node.children],
        "supportingFiles": [_relative_or_absolute(path, root) for path in files],
        "flywheelContext": flywheel,
        "ancestors": [node_payload(root, ancestor) for ancestor in ancestors],
    }
    return {
        **structured,
        "markdown": context_markdown(node, ancestors, icps, files, flywheel),
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def validation_payload(root: Path) -> dict:
    issues = issue_dicts(root)
    return {
        "valid": not issues,
        "issues": issues,
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def node_payload(root: Path, node: ProductNode) -> dict:
    body = marker_content(node).rstrip()
    return {
        "id": node.id,
        "kind": node.kind,
        "slug": node.slug,
        "title": title_from_body(body, node.slug),
        "status": status_from_body(body),
        "parent": node.parent.id if node.parent is not None else None,
        "children": [child.id for child in node.children],
        "icps": parse_icp_references(body) if node.kind in {"outcome", "opportunity"} else [],
        "body": body,
        "marker": _relative_or_absolute(node.marker_file, root),
        "path": _relative_or_absolute(node.path, root),
    }


def node_summary(root: Path, node: ProductNode) -> dict:
    body = marker_content(node).rstrip()
    return {
        "id": node.id,
        "kind": node.kind,
        "slug": node.slug,
        "title": title_from_body(body, node.slug),
        "status": status_from_body(body),
        "marker": _relative_or_absolute(node.marker_file, root),
        "path": _relative_or_absolute(node.path, root),
    }


def resolve_node(root: Path, selector: str) -> ProductNode:
    return ProductGraph(root).resolve(selector)


def matching_nodes(root: Path, selector: str) -> list[ProductNode]:
    return ProductGraph(root).matching(selector)


def context_markdown(
    node: ProductNode,
    ancestors: list[ProductNode],
    icps: list[ProductNode],
    files: list[Path],
    flywheel: str,
) -> str:
    lines = [f"# Context: {node.id}", "", "## Trace"]
    append_node_references(lines, ancestors)
    lines.append(f"- {node.id} ({node.marker_file})")

    append_node_reference_section(lines, "ICPs", icps)
    append_node_reference_section(lines, "Children", node.children)
    append_path_section(lines, "Supporting Files", files)

    if flywheel:
        lines.extend(["", "## Flywheel Context", "", flywheel])

    append_marker_content_section(lines, "Ancestor Content", ancestors)
    append_marker_content_section(lines, "ICP Content", icps)
    lines.extend(["", "## Node Content", "", marker_content(node).rstrip()])
    return "\n".join(lines)


def append_node_reference_section(lines: list[str], title: str, nodes: list[ProductNode]) -> None:
    if not nodes:
        return
    lines.extend(["", f"## {title}"])
    append_node_references(lines, nodes)


def append_node_references(lines: list[str], nodes: list[ProductNode]) -> None:
    for node in nodes:
        lines.append(f"- {node.id} ({node.marker_file})")


def append_path_section(lines: list[str], title: str, paths: list[Path]) -> None:
    if not paths:
        return
    lines.extend(["", f"## {title}"])
    for path in paths:
        lines.append(f"- {path}")


def append_marker_content_section(lines: list[str], title: str, nodes: list[ProductNode]) -> None:
    if not nodes:
        return
    lines.extend(["", f"## {title}"])
    for node in nodes:
        lines.extend(["", f"### {node.id}", "", marker_content(node).rstrip()])


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
