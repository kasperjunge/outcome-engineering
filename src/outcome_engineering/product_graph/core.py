from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from outcome_engineering.product_graph.discovery import (
    discover_flywheel,
    discover_nodes,
    find_node,
    find_nodes_by_kind,
    flywheel_context,
    marker_content,
    node_ancestors,
    related_icps,
    supporting_files,
)
from outcome_engineering.product_graph.model import FlywheelGraph, ProductNode, ValidationIssue
from outcome_engineering.product_graph.mutations import create_node, delete_node, write_marker
from outcome_engineering.product_graph.validation import validate


class NodeResolutionError(ValueError):
    def __init__(self, selector: str, reason: str) -> None:
        super().__init__(f"{reason}: {selector}")
        self.selector = selector
        self.reason = reason


@dataclass(frozen=True)
class ProductGraph:
    """Core filesystem-backed product graph interface.

    CLI commands, HTTP handlers, hosted APIs, and future integrations should
    depend on this facade instead of composing lower-level modules directly.
    """

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    def validate(self) -> list[ValidationIssue]:
        return validate(self.root)

    def nodes(self) -> list[ProductNode]:
        return discover_nodes(self.root)

    def find(self, selector: str) -> ProductNode | None:
        return find_node(self.root, selector)

    def matching(self, selector: str) -> list[ProductNode]:
        selector_path = Path(selector)
        if selector_path.exists():
            resolved_selector = selector_path.resolve()
            return [node for node in self.nodes() if node.path == resolved_selector or node.marker_file == resolved_selector]
        return [node for node in self.nodes() if node.id == selector or node.slug == selector]

    def resolve(self, selector: str) -> ProductNode:
        node = self.find(selector)
        if node is not None:
            return node
        if self.matching(selector):
            raise NodeResolutionError(selector, "ambiguous")
        raise NodeResolutionError(selector, "not found")

    def find_by_kind(self, kind: str | None = None) -> list[ProductNode]:
        return find_nodes_by_kind(self.root, kind)

    def flywheel(self) -> FlywheelGraph | None:
        return discover_flywheel(self.root)

    def ancestors(self, node: ProductNode) -> list[ProductNode]:
        return node_ancestors(node)

    def marker_content(self, node: ProductNode) -> str:
        return marker_content(node)

    def related_icps(self, node: ProductNode, ancestors: list[ProductNode]) -> list[ProductNode]:
        return related_icps(self.root, node, ancestors)

    def supporting_files(self, node: ProductNode) -> list[Path]:
        return supporting_files(node)

    def flywheel_context(self) -> str:
        return flywheel_context(self.root)

    def create_node(self, kind: str, slug: str, title: str | None = None, under: str | None = None) -> ProductNode:
        return create_node(self.root, kind, slug, title, under)

    def write_marker(self, selector: str, content: str) -> ProductNode:
        return write_marker(self.root, selector, content)

    def delete_node(self, selector: str, *, cascade: bool = False) -> ProductNode:
        return delete_node(self.root, selector, cascade=cascade)
