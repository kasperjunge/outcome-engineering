from __future__ import annotations

from pathlib import Path

from outcome_engineering.model import (
    ALLOWED_CHILD_RELATIONSHIPS,
    MARKER_FILES,
    RELATIONSHIP_TO_CHILD_KIND,
    ProductNode,
    ValidationIssue,
)


def marker_files_in(path: Path) -> list[Path]:
    return sorted(child for child in path.iterdir() if child.is_file() and child.name in MARKER_FILES)


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
        if child.is_dir() and child.name in RELATIONSHIP_TO_CHILD_KIND:
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


def relationship_dirs(path: Path) -> list[Path]:
    return sorted(child for child in path.iterdir() if child.is_dir() and child.name in RELATIONSHIP_TO_CHILD_KIND)


def validate(root: Path) -> list[ValidationIssue]:
    root = root.resolve()
    issues: list[ValidationIssue] = []

    if not root.exists():
        return [ValidationIssue(root, "path does not exist")]
    if not root.is_dir():
        return [ValidationIssue(root, "path is not a directory")]

    seen_ids: dict[str, Path] = {}

    for path in sorted([root, *[p for p in root.rglob("*") if p.is_dir()]]):
        markers = marker_files_in(path)
        if path == root:
            root_marker_names = {marker.name for marker in markers}
            unexpected_root_markers = root_marker_names - {"VISION.md", "STRATEGY.md"}
            if unexpected_root_markers:
                issues.append(ValidationIssue(path, f"root has invalid marker files: {', '.join(sorted(unexpected_root_markers))}"))
            continue
        if len(markers) > 1:
            issues.append(ValidationIssue(path, f"node directory has multiple marker files: {', '.join(m.name for m in markers)}"))
            continue
        if len(markers) == 1:
            marker = markers[0]
            kind = MARKER_FILES[marker.name]
            node_id = f"{kind}.{path.name}"
            if node_id in seen_ids:
                issues.append(ValidationIssue(path, f"duplicate node id {node_id}; first seen at {seen_ids[node_id]}"))
            else:
                seen_ids[node_id] = path

            parent_info = parent_node_and_relationship(root, path)
            if path == root:
                continue
            if parent_info is None:
                issues.append(ValidationIssue(path, "node is not inside a valid relationship directory"))
                continue
            parent_path, relationship = parent_info
            expected_kinds = RELATIONSHIP_TO_CHILD_KIND[relationship]
            if kind not in expected_kinds:
                issues.append(
                    ValidationIssue(
                        path,
                        f"{marker.name} is not valid under {relationship}/; expected {', '.join(sorted(expected_kinds))}",
                    )
                )
            if relationship == "experiments":
                parent_markers = marker_files_in(parent_path)
                parent_kind = MARKER_FILES[parent_markers[0].name] if len(parent_markers) == 1 else "unknown"
                if parent_kind != "assumption":
                    issues.append(ValidationIssue(path, "experiments can only live under an assumption"))

    for path in sorted([root, *[p for p in root.rglob("*") if p.is_dir()]]):
        markers = marker_files_in(path)
        current_kind = "root"
        if len(markers) == 1:
            current_kind = MARKER_FILES[markers[0].name]

        for rel_dir in relationship_dirs(path):
            if rel_dir.name not in ALLOWED_CHILD_RELATIONSHIPS[current_kind]:
                issues.append(ValidationIssue(rel_dir, f"{rel_dir.name}/ is not allowed under {current_kind}"))
            for child_dir in sorted(child for child in rel_dir.iterdir() if child.is_dir()):
                child_markers = marker_files_in(child_dir)
                if len(child_markers) == 0:
                    issues.append(ValidationIssue(child_dir, f"missing marker file for child under {rel_dir.name}/"))

    return issues


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
