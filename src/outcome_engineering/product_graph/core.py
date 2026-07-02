from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from outcome_engineering.product_graph.discovery import (
    discover_flywheel,
    discover_nodes,
    flywheel_context,
    marker_content,
    match_nodes,
    node_ancestors,
    related_icps,
    supporting_files,
)
from outcome_engineering.product_graph.model import KIND_TO_RELATIONSHIP, FlywheelGraph, ProductNode, ValidationIssue
from outcome_engineering.product_graph.mutations import create_node, delete_node, write_marker
from outcome_engineering.product_graph.read import context_node
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

    Discovery walks the filesystem once per instance and is cached; the
    mutation methods invalidate the cache. Callers that mutate the graph
    behind this instance's back should create a fresh one.
    """

    root: Path
    _nodes_cache: list[ProductNode] | None = field(default=None, init=False, compare=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", self.root.resolve())

    @staticmethod
    def kinds() -> tuple[str, ...]:
        return tuple(sorted(KIND_TO_RELATIONSHIP))

    def validate(self) -> list[ValidationIssue]:
        return validate(self.root)

    def nodes(self) -> list[ProductNode]:
        if self._nodes_cache is None:
            object.__setattr__(self, "_nodes_cache", discover_nodes(self.root))
        return self._nodes_cache

    def _invalidate(self) -> None:
        object.__setattr__(self, "_nodes_cache", None)

    def find(self, selector: str) -> ProductNode | None:
        matches = self.matching(selector)
        if len(matches) == 1:
            return matches[0]
        return None

    def matching(self, selector: str) -> list[ProductNode]:
        return match_nodes(self.nodes(), selector)

    def resolve(self, selector: str) -> ProductNode:
        matches = self.matching(selector)
        if len(matches) == 1:
            return matches[0]
        if matches:
            raise NodeResolutionError(selector, "ambiguous")
        raise NodeResolutionError(selector, "not found")

    def find_by_kind(self, kind: str | None = None) -> list[ProductNode]:
        nodes = [node for node in self.nodes() if node.kind not in {"vision", "strategy"}]
        if kind is None:
            return sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))
        return sorted((node for node in nodes if node.kind == kind), key=lambda node: (node.slug, str(node.path)))

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

    def context(self, selector: str) -> dict:
        return context_node(self, selector)

    def create_node(self, kind: str, slug: str, title: str | None = None, under: str | None = None) -> ProductNode:
        node = create_node(self.root, kind, slug, title, under)
        self._invalidate()
        return node

    def write_marker(self, selector: str, content: str) -> ProductNode:
        node = write_marker(self.root, selector, content)
        self._invalidate()
        return node

    def delete_node(self, selector: str, *, cascade: bool = False) -> ProductNode:
        node = delete_node(self.root, selector, cascade=cascade)
        self._invalidate()
        return node
