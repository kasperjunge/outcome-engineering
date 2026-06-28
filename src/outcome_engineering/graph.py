from __future__ import annotations

import shutil
from pathlib import Path

from outcome_engineering.model import (
    ALLOWED_CHILD_RELATIONSHIPS,
    ICP_COLLECTION,
    ICP_KIND,
    ICP_REFERENCE_FIELD,
    ICP_REFERRING_KINDS,
    KIND_TO_MARKER_FILE,
    KIND_TO_RELATIONSHIP,
    MARKER_FILES,
    PARENT_KIND_TO_CHILD_KIND,
    RELATIONSHIP_ORDER,
    RELATIONSHIP_TO_CHILD_KIND,
    ROOT_KINDS,
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
        if not child.is_dir():
            continue
        if child.name == ICP_COLLECTION or child.name in RELATIONSHIP_TO_CHILD_KIND:
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
    """Overwrite a node's marker file with new content.

    The graph is the filesystem, so editing a node is editing its marker file.
    Callers are expected to re-validate afterward; freeform markdown edits are
    not rejected here so a mid-edit typo never loses the user's work.
    """
    node = find_node(root, selector)
    if node is None:
        raise ValueError(f"node not found or ambiguous: {selector}")
    if not content.endswith("\n"):
        content += "\n"
    node.marker_file.write_text(content, encoding="utf-8")
    return node


def delete_node(root: Path, selector: str, cascade: bool = False) -> ProductNode:
    """Remove a node directory from the graph.

    A node with descendants is refused unless ``cascade`` is set, so an outcome's
    whole trace subtree can never be removed by a single accidental click.
    """
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


def render_template(kind: str, slug: str, title: str) -> str:
    sections = {
        "icp": "## Who They Are\n\nTODO\n\n## Jobs / Pains\n\n- TODO\n\n## Why They Choose Us\n\n- TODO\n\n## Where They Are Not A Fit\n\n- TODO\n",
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


def parse_icp_references(text: str) -> list[str]:
    """Extract the icp ids a node declares it serves, from its fenced yaml block.

    Supports both inline (``icps: [icp.a, icp.b]``) and block list form::

        icps:
          - icp.a
          - icp.b
    """
    lines = _yaml_block_lines(text)
    references: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped == f"{ICP_REFERENCE_FIELD}:" or stripped.startswith(f"{ICP_REFERENCE_FIELD}:"):
            inline = stripped[len(ICP_REFERENCE_FIELD) + 1 :].strip()
            if inline:
                references.extend(_parse_inline_list(inline))
            else:
                index += 1
                while index < len(lines) and lines[index].strip().startswith("- "):
                    references.append(lines[index].strip()[2:].strip())
                    index += 1
                continue
        index += 1
    return [ref for ref in (_strip_quotes(ref) for ref in references) if ref]


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


def _yaml_block_lines(text: str) -> list[str]:
    lines = text.splitlines()
    inside = False
    block: list[str] = []
    for line in lines:
        if line.strip().startswith("```"):
            if inside:
                break
            inside = line.strip().startswith("```yaml")
            continue
        if inside:
            block.append(line)
    return block


def _parse_inline_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [item.strip() for item in value.split(",") if item.strip()]


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


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

            if kind == ICP_KIND:
                if path.parent.name != ICP_COLLECTION or path.parent.parent != root:
                    issues.append(
                        ValidationIssue(
                            path,
                            f"{marker.name} is only valid directly under {ICP_COLLECTION}/ at the graph root",
                        )
                    )
                continue

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

    icps_dir = root / ICP_COLLECTION
    if icps_dir.is_dir():
        for child_dir in sorted(child for child in icps_dir.iterdir() if child.is_dir()):
            if len(marker_files_in(child_dir)) == 0:
                issues.append(ValidationIssue(child_dir, f"missing marker file for node under {ICP_COLLECTION}/"))

    icp_ids = {node_id for node_id in seen_ids if node_id.startswith(f"{ICP_KIND}.")}
    for path in sorted([root, *[p for p in root.rglob("*") if p.is_dir()]]):
        markers = marker_files_in(path)
        if path == root or len(markers) != 1:
            continue
        kind = MARKER_FILES[markers[0].name]
        references = parse_icp_references(markers[0].read_text(encoding="utf-8"))
        if references and kind not in ICP_REFERRING_KINDS:
            allowed = ", ".join(sorted(ICP_REFERRING_KINDS))
            issues.append(ValidationIssue(markers[0], f"{kind} cannot reference ICPs; only {allowed} may"))
            continue
        for reference in references:
            if not reference.startswith(f"{ICP_KIND}."):
                issues.append(ValidationIssue(markers[0], f"icp reference {reference!r} must be an icp id"))
            elif reference not in icp_ids:
                issues.append(ValidationIssue(markers[0], f"icp reference {reference!r} does not resolve to a known ICP"))

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
