from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pathlib import Path

from outcome_engineering.graph import (
    discover_flywheel,
    discover_nodes,
    find_node,
    flywheel_context,
    marker_content,
    node_ancestors,
    parse_frontmatter_scalar,
    parse_icp_references,
    related_icps,
    supporting_files,
    title_from_markdown,
    validate,
)
from outcome_engineering.model import PARENT_KIND_TO_CHILD_KIND, ProductNode

NODE_KINDS = ("vision", "strategy", "icp", "outcome", "opportunity", "solution", "assumption-test", "prd")


class NodeResolutionError(ValueError):
    def __init__(self, selector: str, reason: str) -> None:
        super().__init__(f"{reason}: {selector}")
        self.selector = selector
        self.reason = reason


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
    for issue in validate(root):
        issues.append(
            {
                "path": _relative_or_absolute(issue.path, root),
                "message": issue.message,
            }
        )
    return issues


def build_graph_payload(root: Path, *, read_only: bool = False, include_source: bool = False) -> dict:
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
                "title": title_from_body(body, node.slug),
                "status": status_from_body(body),
                "parent": node.parent.id if node.parent is not None else None,
                "children": [child.id for child in node.children],
                "icps": icp_refs,
                "body": body,
                "marker": _relative_or_absolute(node.marker_file, root),
                "path": _relative_or_absolute(node.path, root),
                "deletable": node.path != root and not read_only,
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

    payload = {
        "root": root.name,
        "readOnly": read_only,
        "vision": _root_marker_text(discovered, "vision"),
        "strategy": _root_marker_text(discovered, "strategy"),
        "flywheel": flywheel_payload(root),
        "schema": placement_schema(),
        "nodes": nodes,
        "edges": edges,
    }
    if include_source:
        payload["source"] = SourceMetadata.from_root(root).to_dict()
    return payload


def placement_schema() -> dict:
    return {
        "childKinds": {
            parent: sorted(child for child in children if child in NODE_KINDS)
            for parent, children in PARENT_KIND_TO_CHILD_KIND.items()
        }
    }


def list_nodes(root: Path, kind: str | None = None) -> dict:
    root = root.resolve()
    nodes = [node for node in discover_nodes(root) if node.kind in NODE_KINDS]
    if kind is not None:
        nodes = [node for node in nodes if node.kind == kind]
    return {
        "nodes": [node_payload(root, node) for node in sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))],
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def show_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    return {
        "node": node_payload(root, resolve_node(root, selector)),
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def trace_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    node = resolve_node(root, selector)
    ancestors = node_ancestors(node)
    return {
        "node": node_payload(root, node),
        "trace": [node_summary(root, ancestor) for ancestor in [*ancestors, node]],
        "children": [node_summary(root, child) for child in node.children],
        "source": SourceMetadata.from_root(root).to_dict(),
    }


def context_node(root: Path, selector: str) -> dict:
    root = root.resolve()
    node = resolve_node(root, selector)
    ancestors = node_ancestors(node)
    icps = related_icps(root, node, ancestors)
    files = supporting_files(node)
    flywheel = flywheel_context(root)

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
    root = root.resolve()
    node = find_node(root, selector)
    if node is not None:
        return node
    if matching_nodes(root, selector):
        raise NodeResolutionError(selector, "ambiguous")
    raise NodeResolutionError(selector, "not found")


def matching_nodes(root: Path, selector: str) -> list[ProductNode]:
    root = root.resolve()
    selector_path = Path(selector)
    if selector_path.exists():
        resolved_selector = selector_path.resolve()
        return [node for node in discover_nodes(root) if node.path == resolved_selector or node.marker_file == resolved_selector]
    return [node for node in discover_nodes(root) if node.id == selector or node.slug == selector]


def context_markdown(
    node: ProductNode,
    ancestors: list[ProductNode],
    icps: list[ProductNode],
    files: list[Path],
    flywheel: str,
) -> str:
    lines = [f"# Context: {node.id}", "", "## Trace"]
    for ancestor in ancestors:
        lines.append(f"- {ancestor.id} ({ancestor.marker_file})")
    lines.append(f"- {node.id} ({node.marker_file})")

    if icps:
        lines.extend(["", "## ICPs"])
        for icp in icps:
            lines.append(f"- {icp.id} ({icp.marker_file})")

    if node.children:
        lines.extend(["", "## Children"])
        for child in node.children:
            lines.append(f"- {child.id} ({child.marker_file})")

    if files:
        lines.extend(["", "## Supporting Files"])
        for path in files:
            lines.append(f"- {path}")

    if flywheel:
        lines.extend(["", "## Flywheel Context", "", flywheel])

    if ancestors:
        lines.extend(["", "## Ancestor Content"])
        for ancestor in ancestors:
            lines.extend(["", f"### {ancestor.id}", "", marker_content(ancestor).rstrip()])

    if icps:
        lines.extend(["", "## ICP Content"])
        for icp in icps:
            lines.extend(["", f"### {icp.id}", "", marker_content(icp).rstrip()])

    lines.extend(["", "## Node Content", "", marker_content(node).rstrip()])
    return "\n".join(lines)


def flywheel_payload(root: Path) -> dict | None:
    flywheel = discover_flywheel(root)
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
