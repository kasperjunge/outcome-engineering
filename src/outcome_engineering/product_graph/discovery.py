from __future__ import annotations

from pathlib import Path

from outcome_engineering.product_graph.frontmatter import parse_flywheel_next, parse_frontmatter_scalar, parse_icp_references
from outcome_engineering.product_graph.model import (
    FLYWHEEL_COLLECTION,
    FLYWHEEL_MARKER_FILE,
    FLYWHEEL_NODE_MARKER_FILE,
    ICP_COLLECTION,
    ICP_KIND,
    MARKER_FILES,
    RELATIONSHIP_ORDER,
    RELATIONSHIP_TO_CHILD_KIND,
    STRATEGY_COLLECTION,
    FlywheelGraph,
    FlywheelNode,
    ProductNode,
)


def marker_files_in(path: Path) -> list[Path]:
    return sorted(child for child in path.iterdir() if child.is_file() and child.name in MARKER_FILES)


def flywheel_marker_files_in(path: Path) -> list[Path]:
    return sorted(child for child in path.iterdir() if child.is_file() and child.name in {FLYWHEEL_MARKER_FILE, FLYWHEEL_NODE_MARKER_FILE})


def discover_nodes(root: Path) -> list[ProductNode]:
    root = root.resolve()
    nodes: list[ProductNode] = []

    def visit_node_dir(path: Path, parent: ProductNode | None, relationship: str | None) -> ProductNode | None:
        markers = marker_files_in(path)
        if len(markers) != 1:
            return None

        marker = markers[0]
        node = ProductNode(
            path=path,
            kind=MARKER_FILES[marker.name],
            marker_file=marker,
            slug=path.name,
            parent=parent,
            relationship=relationship,
            children=[],
        )
        nodes.append(node)

        child_nodes: list[ProductNode] = []
        for rel_dir in relationship_dirs(path):
            for child_dir in sorted(child for child in rel_dir.iterdir() if child.is_dir()):
                child = visit_node_dir(child_dir, node, rel_dir.name)
                if child is not None:
                    child_nodes.append(child)

        node.children.extend(child_nodes)
        return node

    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {ICP_COLLECTION, STRATEGY_COLLECTION} or child.name in RELATIONSHIP_TO_CHILD_KIND:
            for node_dir in sorted(grandchild for grandchild in child.iterdir() if grandchild.is_dir()):
                visit_node_dir(node_dir, None, child.name)

    for marker in marker_files_in(root):
        nodes.append(
            ProductNode(
                path=root,
                kind=MARKER_FILES[marker.name],
                marker_file=marker,
                slug=root.name,
                parent=None,
                relationship=None,
                children=[],
            )
        )

    return nodes


def match_nodes(nodes: list[ProductNode], selector: str) -> list[ProductNode]:
    selector_path = Path(selector)
    if selector_path.exists():
        resolved_selector = selector_path.resolve()
        return [node for node in nodes if node.path == resolved_selector or node.marker_file == resolved_selector]
    return [node for node in nodes if node.id == selector or node.slug == selector]


def matching_nodes(root: Path, selector: str) -> list[ProductNode]:
    return match_nodes(discover_nodes(root), selector)


def find_node(root: Path, selector: str) -> ProductNode | None:
    matches = matching_nodes(root, selector)
    if len(matches) == 1:
        return matches[0]
    return None


def find_nodes_by_kind(root: Path, kind: str | None = None) -> list[ProductNode]:
    nodes = [node for node in discover_nodes(root) if node.kind not in {"vision", "strategy"}]
    if kind is None:
        return sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))
    return sorted((node for node in nodes if node.kind == kind), key=lambda node: (node.slug, str(node.path)))


def discover_flywheel(root: Path) -> FlywheelGraph | None:
    root = root.resolve()
    flywheels_dir = root / FLYWHEEL_COLLECTION
    if not flywheels_dir.is_dir():
        return None

    flywheel_dirs = sorted(child for child in flywheels_dir.iterdir() if child.is_dir() and (child / FLYWHEEL_MARKER_FILE).is_file())
    if not flywheel_dirs:
        return None

    path = flywheel_dirs[0]
    marker = path / FLYWHEEL_MARKER_FILE
    body = marker.read_text(encoding="utf-8").rstrip()
    return FlywheelGraph(
        path=path,
        marker_file=marker,
        slug=path.name,
        title=title_from_markdown(body, path.name),
        body=body,
        status=parse_frontmatter_scalar(body, "status"),
        nodes=discover_flywheel_nodes(path),
    )


def discover_flywheel_nodes(flywheel_path: Path) -> list[FlywheelNode]:
    nodes_dir = flywheel_path / "nodes"
    if not nodes_dir.is_dir():
        return []
    return [
        flywheel_node_from_dir(node_dir, node_dir / FLYWHEEL_NODE_MARKER_FILE)
        for node_dir in sorted(child for child in nodes_dir.iterdir() if child.is_dir())
        if (node_dir / FLYWHEEL_NODE_MARKER_FILE).is_file()
    ]


def flywheel_node_from_dir(node_dir: Path, marker: Path) -> FlywheelNode:
    body = marker.read_text(encoding="utf-8").rstrip()
    return FlywheelNode(
        path=node_dir,
        marker_file=marker,
        slug=node_dir.name,
        title=title_from_markdown(body, node_dir.name),
        body=body,
        status=parse_frontmatter_scalar(body, "status"),
        next=parse_flywheel_next(body),
    )


def node_ancestors(node: ProductNode) -> list[ProductNode]:
    ancestors: list[ProductNode] = []
    current = node.parent
    while current is not None:
        ancestors.append(current)
        current = current.parent
    return list(reversed(ancestors))


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-") if part)


def title_from_markdown(text: str, fallback: str) -> str:
    name = parse_frontmatter_scalar(text, "name")
    if name:
        return name
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return title_from_slug(fallback)


def marker_content(node: ProductNode) -> str:
    return node.marker_file.read_text(encoding="utf-8")


def node_icp_references(node: ProductNode) -> list[str]:
    return parse_icp_references(marker_content(node))


def resolve_icp_references(root: Path, node: ProductNode) -> list[ProductNode]:
    resolved: list[ProductNode] = []
    for ref in node_icp_references(node):
        match = find_node(root, ref)
        if match is not None and match.kind == ICP_KIND:
            resolved.append(match)
    return resolved


def related_icps(root: Path, node: ProductNode, ancestors: list[ProductNode]) -> list[ProductNode]:
    """ICPs a node serves, inherited from itself and its outcome/opportunity ancestors."""
    seen: dict[str, ProductNode] = {}
    for candidate in [*ancestors, node]:
        for icp in resolve_icp_references(root, candidate):
            seen.setdefault(icp.id, icp)
    return list(seen.values())


def supporting_files(node: ProductNode) -> list[Path]:
    relationship_names = set(RELATIONSHIP_TO_CHILD_KIND)
    return sorted(
        path
        for path in node.path.rglob("*")
        if path.is_file()
        and path != node.marker_file
        and not any(part in relationship_names for part in path.relative_to(node.path).parts[:-1])
    )


def flywheel_context(root: Path) -> str:
    flywheel = discover_flywheel(root)
    if flywheel is None:
        return ""

    lines = [f"### {flywheel.id}", "", flywheel.body.rstrip()]
    for node in flywheel.nodes:
        lines.extend(["", f"#### {node.id}", "", node.body.rstrip()])
    return "\n".join(lines)


def relationship_dirs(path: Path) -> list[Path]:
    order = {relationship: index for index, relationship in enumerate(RELATIONSHIP_ORDER)}
    return sorted(
        (child for child in path.iterdir() if child.is_dir() and child.name in RELATIONSHIP_TO_CHILD_KIND),
        key=lambda child: order[child.name],
    )


def parent_node_and_relationship(root: Path, path: Path) -> tuple[Path, str] | None:
    parent = path.parent
    if parent == root:
        return None
    relationship = parent.name
    if relationship not in RELATIONSHIP_TO_CHILD_KIND:
        return None
    node_parent = parent.parent
    if node_parent == root:
        return node_parent, relationship
    if len(marker_files_in(node_parent)) != 1:
        return None
    return node_parent, relationship
