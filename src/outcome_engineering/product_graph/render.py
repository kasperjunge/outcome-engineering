"""Render product graph nodes as agent-facing markdown."""

from __future__ import annotations

from pathlib import Path

from outcome_engineering.product_graph.discovery import marker_content
from outcome_engineering.product_graph.model import ProductNode


def context_markdown(
    node: ProductNode,
    ancestors: list[ProductNode],
    icps: list[ProductNode],
    files: list[Path],
    flywheel: str,
) -> str:
    lines = [f"# Context: {node.id}", "", "## Trace"]
    _append_node_references(lines, ancestors)
    lines.append(f"- {node.id} ({node.marker_file})")

    _append_node_reference_section(lines, "ICPs", icps)
    _append_node_reference_section(lines, "Children", node.children)
    _append_path_section(lines, "Supporting Files", files)

    if flywheel:
        lines.extend(["", "## Flywheel Context", "", flywheel])

    _append_marker_content_section(lines, "Ancestor Content", ancestors)
    _append_marker_content_section(lines, "ICP Content", icps)
    lines.extend(["", "## Node Content", "", marker_content(node).rstrip()])
    return "\n".join(lines)


def _append_node_reference_section(lines: list[str], title: str, nodes: list[ProductNode]) -> None:
    if not nodes:
        return
    lines.extend(["", f"## {title}"])
    _append_node_references(lines, nodes)


def _append_node_references(lines: list[str], nodes: list[ProductNode]) -> None:
    for node in nodes:
        lines.append(f"- {node.id} ({node.marker_file})")


def _append_path_section(lines: list[str], title: str, paths: list[Path]) -> None:
    if not paths:
        return
    lines.extend(["", f"## {title}"])
    for path in paths:
        lines.append(f"- {path}")


def _append_marker_content_section(lines: list[str], title: str, nodes: list[ProductNode]) -> None:
    if not nodes:
        return
    lines.extend(["", f"## {title}"])
    for node in nodes:
        lines.extend(["", f"### {node.id}", "", marker_content(node).rstrip()])
