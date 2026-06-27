from __future__ import annotations

from pathlib import Path

from outcome_engineering.model import (
    ALLOWED_CHILD_RELATIONSHIPS,
    KIND_TO_MARKER_FILE,
    KIND_TO_RELATIONSHIP,
    MARKER_FILES,
    PARENT_KIND_TO_CHILD_KIND,
    RELATIONSHIP_ORDER,
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


def find_node(root: Path, selector: str) -> ProductNode | None:
    root = root.resolve()
    selector_path = Path(selector)
    if selector_path.exists():
        resolved_selector = selector_path.resolve()
        for node in discover_nodes(root):
            if node.path == resolved_selector or node.marker_file == resolved_selector:
                return node
        return None

    matches = [node for node in discover_nodes(root) if node.id == selector or node.slug == selector]
    if len(matches) == 1:
        return matches[0]
    return None


def find_nodes_by_kind(root: Path, kind: str | None = None) -> list[ProductNode]:
    nodes = [node for node in discover_nodes(root) if node.kind not in {"vision", "strategy"}]
    if kind is None:
        return sorted(nodes, key=lambda node: (node.kind, node.slug, str(node.path)))
    return sorted((node for node in nodes if node.kind == kind), key=lambda node: (node.slug, str(node.path)))


def node_ancestors(node: ProductNode) -> list[ProductNode]:
    ancestors: list[ProductNode] = []
    current = node.parent
    while current is not None:
        ancestors.append(current)
        current = current.parent
    return list(reversed(ancestors))


def create_node(root: Path, kind: str, slug: str, title: str | None, under: str | None) -> ProductNode:
    root = root.resolve()
    if kind not in KIND_TO_RELATIONSHIP:
        supported = ", ".join(sorted(KIND_TO_RELATIONSHIP))
        raise ValueError(f"unsupported node kind {kind!r}; expected one of: {supported}")

    parent: ProductNode | None = None
    parent_kind = "root"
    parent_path = root
    if kind != "outcome":
        if under is None:
            raise ValueError(f"{kind} requires --under")
        parent = find_node(root, under)
        if parent is None:
            raise ValueError(f"parent not found: {under}")
        parent_kind = parent.kind
        parent_path = parent.path
    elif under is not None:
        raise ValueError("outcome cannot use --under; outcomes live under the product graph root")

    allowed_child_kinds = PARENT_KIND_TO_CHILD_KIND.get(parent_kind, set())
    if kind not in allowed_child_kinds:
        allowed = ", ".join(sorted(allowed_child_kinds)) or "none"
        raise ValueError(f"cannot create {kind} under {parent_kind}; allowed child kinds: {allowed}")

    relationship = KIND_TO_RELATIONSHIP[kind]
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


def render_template(kind: str, slug: str, title: str) -> str:
    sections = {
        "outcome": "## Measures\n\n- TODO\n\n## Known / Unknown\n\n- Known: TODO\n- Unknown: TODO\n",
        "opportunity": "## Evidence\n\n- TODO\n\n## Known / Unknown\n\n- Known: TODO\n- Unknown: TODO\n",
        "solution": "## Product Risks\n\n- Value: TODO\n- Usability: TODO\n- Feasibility: TODO\n- Viability: TODO\n\n## Assumptions\n\n- TODO\n",
        "assumption-test": "## Assumption\n\nTODO\n\n## Risk Type\n\nTODO\n\n## Test\n\nTODO\n\n## Success / Failure Signal\n\nTODO\n\n## Decision It Informs\n\nTODO\n",
        "prd": "## Problem\n\nTODO\n\n## User Stories\n\n- TODO\n\n## Acceptance Criteria\n\n- TODO\n",
    }
    body = sections[kind]
    return f"""# {title}

```yaml
type: {kind}
id: {kind}.{slug}
status: draft
```

{body}
"""


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-") if part)


def marker_content(node: ProductNode) -> str:
    return node.marker_file.read_text(encoding="utf-8")


def supporting_files(node: ProductNode) -> list[Path]:
    relationship_names = set(RELATIONSHIP_TO_CHILD_KIND)
    return sorted(
        path
        for path in node.path.rglob("*")
        if path.is_file()
        and path != node.marker_file
        and not any(part in relationship_names for part in path.relative_to(node.path).parts[:-1])
    )


def relationship_dirs(path: Path) -> list[Path]:
    order = {relationship: index for index, relationship in enumerate(RELATIONSHIP_ORDER)}
    return sorted(
        (child for child in path.iterdir() if child.is_dir() and child.name in RELATIONSHIP_TO_CHILD_KIND),
        key=lambda child: order[child.name],
    )


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
            _parent_path, relationship = parent_info
            expected_kinds = RELATIONSHIP_TO_CHILD_KIND[relationship]
            if kind not in expected_kinds:
                issues.append(
                    ValidationIssue(
                        path,
                        f"{marker.name} is not valid under {relationship}/; expected {', '.join(sorted(expected_kinds))}",
                    )
                )

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
