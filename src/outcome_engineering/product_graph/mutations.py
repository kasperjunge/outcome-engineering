from __future__ import annotations

import shutil
from pathlib import Path

from outcome_engineering.product_graph.discovery import find_node, title_from_slug
from outcome_engineering.product_graph.model import (
    KIND_TO_MARKER_FILE,
    KIND_TO_RELATIONSHIP,
    PARENT_KIND_TO_CHILD_KIND,
    ROOT_KINDS,
    ProductNode,
)
from outcome_engineering.product_graph.node_templates import render_template


def create_node(root: Path, kind: str, slug: str, title: str | None, under: str | None) -> ProductNode:
    root = root.resolve()
    if kind not in KIND_TO_RELATIONSHIP:
        supported = ", ".join(sorted(KIND_TO_RELATIONSHIP))
        raise ValueError(f"unsupported node kind {kind!r}; expected one of: {supported}")

    parent: ProductNode | None = None
    parent_kind = "root"
    parent_path = root
    relationship = KIND_TO_RELATIONSHIP[kind]
    if kind not in ROOT_KINDS:
        if under is None:
            raise ValueError(f"{kind} requires --under")
        parent = find_node(root, under)
        if parent is None:
            raise ValueError(f"parent not found: {under}")
        parent_kind = parent.kind
        parent_path = parent.path
    elif under is not None:
        raise ValueError(f"{kind} cannot use --under; {relationship} live under the product graph root")

    allowed_child_kinds = PARENT_KIND_TO_CHILD_KIND.get(parent_kind, set())
    if kind not in allowed_child_kinds:
        allowed = ", ".join(sorted(allowed_child_kinds)) or "none"
        raise ValueError(f"cannot create {kind} under {parent_kind}; allowed child kinds: {allowed}")

    node_path = parent_path / relationship / slug
    if node_path.exists():
        raise FileExistsError(f"{node_path} already exists")

    marker = KIND_TO_MARKER_FILE[kind]
    node_path.mkdir(parents=True)
    marker_path = node_path / marker
    marker_path.write_text(render_template(kind, slug, title or title_from_slug(slug)), encoding="utf-8")

    return ProductNode(
        path=node_path,
        kind=kind,
        marker_file=marker_path,
        slug=slug,
        parent=parent,
        relationship=relationship,
        children=[],
    )


def write_marker(root: Path, selector: str, content: str) -> ProductNode:
    """Overwrite a node's marker file with new content."""
    node = find_node(root, selector)
    if node is None:
        raise ValueError(f"node not found or ambiguous: {selector}")
    if not content.endswith("\n"):
        content += "\n"
    node.marker_file.write_text(content, encoding="utf-8")
    return node


def delete_node(root: Path, selector: str, cascade: bool = False) -> ProductNode:
    """Remove a node directory from the graph."""
    node = find_node(root, selector)
    if node is None:
        raise ValueError(f"node not found or ambiguous: {selector}")
    if node.path == root.resolve():
        raise ValueError("cannot delete the graph root")
    if node.children and not cascade:
        kinds = ", ".join(sorted({child.kind for child in node.children}))
        raise ValueError(f"{node.id} has children ({kinds}); pass cascade to remove the subtree")
    shutil.rmtree(node.path)
    return node
