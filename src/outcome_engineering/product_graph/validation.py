from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from outcome_engineering.product_graph.frontmatter import (
    has_fenced_yaml_metadata,
    parse_flywheel_next,
    parse_frontmatter,
    parse_frontmatter_scalar,
    parse_icp_references,
    strip_frontmatter,
)
from outcome_engineering.product_graph.discovery import (
    flywheel_marker_files_in,
    marker_files_in,
    parent_node_and_relationship,
    relationship_dirs,
    title_from_markdown,
)
from outcome_engineering.product_graph.model import (
    ALLOWED_CHILD_RELATIONSHIPS,
    FLYWHEEL_COLLECTION,
    FLYWHEEL_KIND,
    FLYWHEEL_MARKER_FILE,
    FLYWHEEL_NODE_KIND,
    FLYWHEEL_NODE_MARKER_FILE,
    ICP_COLLECTION,
    ICP_KIND,
    ICP_REFERRING_KINDS,
    MARKER_FILES,
    RELATIONSHIP_TO_CHILD_KIND,
    STRATEGY_COLLECTION,
    STRATEGY_KIND,
    ValidationIssue,
)


@dataclass(frozen=True)
class StrategyPeriod:
    marker: Path
    starts: date
    ends: date


@dataclass
class ValidationContext:
    issues: list[ValidationIssue] = field(default_factory=list)
    seen_ids: dict[str, Path] = field(default_factory=dict)
    strategy_periods: list[StrategyPeriod] = field(default_factory=list)


def validate(root: Path) -> list[ValidationIssue]:
    root = root.resolve()
    path_issue = _path_issue(root)
    if path_issue is not None:
        return [path_issue]

    context = ValidationContext()
    graph_dirs = _graph_dirs(root)
    _validate_markers(root, graph_dirs, context)
    _validate_relationship_directories(graph_dirs, context)
    _validate_collection_markers(root, context)
    _validate_icp_references(root, graph_dirs, context)
    _validate_root_strategy(root, context)
    _validate_strategy_periods_do_not_overlap(context.strategy_periods, context.issues)
    _validate_flywheel(root, context.issues)
    return context.issues


def causal_explanation(text: str) -> bool:
    body = strip_frontmatter(text)
    lines = [line.strip() for line in body.splitlines()]
    content_lines = [line for line in lines if line and not line.startswith("#")]
    return bool(content_lines)


def _path_issue(root: Path) -> ValidationIssue | None:
    if not root.exists():
        return ValidationIssue(root, "path does not exist")
    if not root.is_dir():
        return ValidationIssue(root, "path is not a directory")
    return None


def _graph_dirs(root: Path) -> list[Path]:
    return sorted([root, *[path for path in root.rglob("*") if path.is_dir()]])


def _validate_markers(root: Path, graph_dirs: list[Path], context: ValidationContext) -> None:
    for path in graph_dirs:
        markers = marker_files_in(path)
        if path == root:
            _validate_root_markers(path, markers, context.issues)
            continue
        if len(markers) > 1:
            context.issues.append(ValidationIssue(path, f"node directory has multiple marker files: {', '.join(m.name for m in markers)}"))
            continue
        if len(markers) == 1:
            _validate_node_marker(root, path, markers[0], context)


def _validate_root_markers(path: Path, markers: list[Path], issues: list[ValidationIssue]) -> None:
    root_marker_names = {marker.name for marker in markers}
    unexpected_root_markers = root_marker_names - {"VISION.md", "STRATEGY.md"}
    if unexpected_root_markers:
        issues.append(ValidationIssue(path, f"root has invalid marker files: {', '.join(sorted(unexpected_root_markers))}"))


def _validate_node_marker(root: Path, path: Path, marker: Path, context: ValidationContext) -> None:
    kind = MARKER_FILES[marker.name]
    _validate_metadata_format(marker, context.issues)
    _validate_unique_node_id(path, kind, context)

    if kind == STRATEGY_KIND:
        _validate_strategy_node(root, path, marker, context)
        return
    if kind == ICP_KIND:
        _validate_icp_node(root, path, marker, context.issues)
        return
    _validate_relationship_placement(root, path, marker, kind, context.issues)


def _validate_metadata_format(marker: Path, issues: list[ValidationIssue]) -> None:
    if has_fenced_yaml_metadata(marker.read_text(encoding="utf-8")):
        issues.append(ValidationIssue(marker, "metadata must use frontmatter, not fenced yaml blocks"))


def _validate_unique_node_id(path: Path, kind: str, context: ValidationContext) -> None:
    node_id = f"{kind}.{path.name}"
    if node_id in context.seen_ids:
        context.issues.append(ValidationIssue(path, f"duplicate node id {node_id}; first seen at {context.seen_ids[node_id]}"))
        return
    context.seen_ids[node_id] = path


def _validate_strategy_node(root: Path, path: Path, marker: Path, context: ValidationContext) -> None:
    _validate_strategy_marker(marker, context.issues, context.strategy_periods)
    if path.parent.name != STRATEGY_COLLECTION or path.parent.parent != root:
        context.issues.append(
            ValidationIssue(
                path,
                f"{marker.name} is only valid at the graph root or directly under {STRATEGY_COLLECTION}/ at the graph root",
            )
        )


def _validate_icp_node(root: Path, path: Path, marker: Path, issues: list[ValidationIssue]) -> None:
    if path.parent.name != ICP_COLLECTION or path.parent.parent != root:
        issues.append(
            ValidationIssue(
                path,
                f"{marker.name} is only valid directly under {ICP_COLLECTION}/ at the graph root",
            )
        )


def _validate_relationship_placement(root: Path, path: Path, marker: Path, kind: str, issues: list[ValidationIssue]) -> None:
    parent_info = parent_node_and_relationship(root, path)
    if parent_info is None:
        issues.append(ValidationIssue(path, "node is not inside a valid relationship directory"))
        return

    _parent_path, relationship = parent_info
    expected_kinds = RELATIONSHIP_TO_CHILD_KIND[relationship]
    if kind not in expected_kinds:
        issues.append(
            ValidationIssue(
                path,
                f"{marker.name} is not valid under {relationship}/; expected {', '.join(sorted(expected_kinds))}",
            )
        )


def _validate_relationship_directories(graph_dirs: list[Path], context: ValidationContext) -> None:
    for path in graph_dirs:
        current_kind = _current_kind(path)
        for rel_dir in relationship_dirs(path):
            if rel_dir.name not in ALLOWED_CHILD_RELATIONSHIPS[current_kind]:
                context.issues.append(ValidationIssue(rel_dir, f"{rel_dir.name}/ is not allowed under {current_kind}"))
            _validate_relationship_children(rel_dir, context.issues)


def _current_kind(path: Path) -> str:
    markers = marker_files_in(path)
    if len(markers) == 1:
        return MARKER_FILES[markers[0].name]
    return "root"


def _validate_relationship_children(rel_dir: Path, issues: list[ValidationIssue]) -> None:
    for child_dir in sorted(child for child in rel_dir.iterdir() if child.is_dir()):
        if len(marker_files_in(child_dir)) == 0:
            issues.append(ValidationIssue(child_dir, f"missing marker file for child under {rel_dir.name}/"))


def _validate_collection_markers(root: Path, context: ValidationContext) -> None:
    icps_dir = root / ICP_COLLECTION
    if not icps_dir.is_dir():
        return
    for child_dir in sorted(child for child in icps_dir.iterdir() if child.is_dir()):
        if len(marker_files_in(child_dir)) == 0:
            context.issues.append(ValidationIssue(child_dir, f"missing marker file for node under {ICP_COLLECTION}/"))


def _validate_icp_references(root: Path, graph_dirs: list[Path], context: ValidationContext) -> None:
    icp_ids = {node_id for node_id in context.seen_ids if node_id.startswith(f"{ICP_KIND}.")}
    for path in graph_dirs:
        markers = marker_files_in(path)
        if path == root or len(markers) != 1:
            continue
        _validate_marker_icp_references(markers[0], icp_ids, context.issues)


def _validate_marker_icp_references(marker: Path, icp_ids: set[str], issues: list[ValidationIssue]) -> None:
    kind = MARKER_FILES[marker.name]
    references = parse_icp_references(marker.read_text(encoding="utf-8"))
    if references and kind not in ICP_REFERRING_KINDS:
        allowed = ", ".join(sorted(ICP_REFERRING_KINDS))
        issues.append(ValidationIssue(marker, f"{kind} cannot reference ICPs; only {allowed} may"))
        return

    for reference in references:
        _validate_icp_reference(marker, reference, icp_ids, issues)


def _validate_icp_reference(marker: Path, reference: str, icp_ids: set[str], issues: list[ValidationIssue]) -> None:
    if not reference.startswith(f"{ICP_KIND}."):
        issues.append(ValidationIssue(marker, f"icp reference {reference!r} must be an icp id"))
    elif reference not in icp_ids:
        issues.append(ValidationIssue(marker, f"icp reference {reference!r} does not resolve to a known ICP"))


def _validate_root_strategy(root: Path, context: ValidationContext) -> None:
    root_strategy = root / "STRATEGY.md"
    if not root_strategy.is_file():
        return
    _validate_metadata_format(root_strategy, context.issues)
    _validate_strategy_marker(root_strategy, context.issues, context.strategy_periods)


def _validate_flywheel(root: Path, issues: list[ValidationIssue]) -> None:
    flywheels_dir = root / FLYWHEEL_COLLECTION
    if not flywheels_dir.exists():
        return
    if not flywheels_dir.is_dir():
        issues.append(ValidationIssue(flywheels_dir, f"{FLYWHEEL_COLLECTION} must be a directory"))
        return

    flywheel_dirs = sorted(child for child in flywheels_dir.iterdir() if child.is_dir())
    if len(flywheel_dirs) > 1:
        issues.append(ValidationIssue(flywheels_dir, "only one experimental flywheel is supported"))
    for flywheel_dir in flywheel_dirs:
        _validate_flywheel_dir(flywheel_dir, issues)


def _validate_flywheel_dir(flywheel_dir: Path, issues: list[ValidationIssue]) -> None:
    markers = flywheel_marker_files_in(flywheel_dir)
    if markers != [flywheel_dir / FLYWHEEL_MARKER_FILE]:
        issues.append(ValidationIssue(flywheel_dir, f"flywheel directory must contain exactly {FLYWHEEL_MARKER_FILE}"))
        return

    content = markers[0].read_text(encoding="utf-8")
    _validate_flywheel_marker(markers[0], content, FLYWHEEL_KIND, f"{FLYWHEEL_KIND}.{flywheel_dir.name}", issues)
    _validate_flywheel_nodes_dir(flywheel_dir, issues)


def _validate_flywheel_nodes_dir(flywheel_dir: Path, issues: list[ValidationIssue]) -> None:
    nodes_dir = flywheel_dir / "nodes"
    if not nodes_dir.exists():
        issues.append(ValidationIssue(flywheel_dir, "flywheel must contain nodes/"))
        return
    if not nodes_dir.is_dir():
        issues.append(ValidationIssue(nodes_dir, "flywheel nodes must live in a nodes/ directory"))
        return

    node_ids, node_next = _validate_flywheel_nodes(nodes_dir, issues)
    _validate_flywheel_next_references(node_next, node_ids, issues)


def _validate_flywheel_nodes(nodes_dir: Path, issues: list[ValidationIssue]) -> tuple[set[str], dict[Path, list[str]]]:
    node_ids: set[str] = set()
    node_next: dict[Path, list[str]] = {}
    for node_dir in sorted(child for child in nodes_dir.iterdir() if child.is_dir()):
        _validate_flywheel_node_dir(node_dir, node_ids, node_next, issues)
    return node_ids, node_next


def _validate_flywheel_node_dir(
    node_dir: Path,
    node_ids: set[str],
    node_next: dict[Path, list[str]],
    issues: list[ValidationIssue],
) -> None:
    node_markers = flywheel_marker_files_in(node_dir)
    if node_markers != [node_dir / FLYWHEEL_NODE_MARKER_FILE]:
        issues.append(ValidationIssue(node_dir, f"flywheel node directory must contain exactly {FLYWHEEL_NODE_MARKER_FILE}"))
        return

    node_id = f"{FLYWHEEL_NODE_KIND}.{node_dir.name}"
    node_ids.add(node_id)
    node_content = node_markers[0].read_text(encoding="utf-8")
    _validate_flywheel_marker(node_markers[0], node_content, FLYWHEEL_NODE_KIND, node_id, issues)
    next_ids = parse_flywheel_next(node_content)
    if not next_ids:
        issues.append(ValidationIssue(node_markers[0], "flywheel node must declare at least one next flywheel-node id"))
    if not causal_explanation(node_content):
        issues.append(ValidationIssue(node_markers[0], "flywheel node must explain why it creates the next step"))
    node_next[node_markers[0]] = next_ids


def _validate_flywheel_next_references(node_next: dict[Path, list[str]], node_ids: set[str], issues: list[ValidationIssue]) -> None:
    for marker, next_ids in node_next.items():
        for next_id in next_ids:
            if not next_id.startswith(f"{FLYWHEEL_NODE_KIND}."):
                issues.append(ValidationIssue(marker, f"next reference {next_id!r} must be a flywheel-node id"))
            elif next_id not in node_ids:
                issues.append(ValidationIssue(marker, f"next reference {next_id!r} does not resolve to a flywheel node"))


def _validate_flywheel_marker(marker: Path, content: str, expected_type: str, expected_id: str, issues: list[ValidationIssue]) -> None:
    if has_fenced_yaml_metadata(content):
        issues.append(ValidationIssue(marker, "metadata must use frontmatter, not fenced yaml blocks"))
    metadata = parse_frontmatter(content)
    if metadata.get("type") != expected_type:
        issues.append(ValidationIssue(marker, f"flywheel metadata type must be {expected_type}"))
    if metadata.get("id") != expected_id:
        issues.append(ValidationIssue(marker, f"flywheel metadata id must be {expected_id}"))
    if not title_from_markdown(content, ""):
        issues.append(ValidationIssue(marker, "flywheel marker must include a title"))


def _validate_strategy_marker(marker: Path, issues: list[ValidationIssue], strategy_periods: list[StrategyPeriod]) -> None:
    content = marker.read_text(encoding="utf-8")
    _validate_strategy_required_metadata(marker, content, issues)
    starts_text = parse_frontmatter_scalar(content, "starts")
    ends_text = parse_frontmatter_scalar(content, "ends")
    if starts_text is None or ends_text is None:
        return

    starts = _parse_iso_date(starts_text, marker, "starts", issues)
    ends = _parse_iso_date(ends_text, marker, "ends", issues)
    if starts is None or ends is None:
        return
    if starts > ends:
        issues.append(ValidationIssue(marker, "strategy starts must be on or before ends"))
        return
    strategy_periods.append(StrategyPeriod(marker=marker, starts=starts, ends=ends))


def _validate_strategy_required_metadata(marker: Path, content: str, issues: list[ValidationIssue]) -> None:
    name_text = parse_frontmatter_scalar(content, "name")
    if name_text is None or not name_text.strip():
        issues.append(ValidationIssue(marker, "strategy must declare name"))

    status = parse_frontmatter_scalar(content, "status")
    if status is not None:
        issues.append(ValidationIssue(marker, "strategy status is derived from starts/ends; remove status"))

    if parse_frontmatter_scalar(content, "starts") is None:
        issues.append(ValidationIssue(marker, "strategy must declare starts: YYYY-MM-DD"))
    if parse_frontmatter_scalar(content, "ends") is None:
        issues.append(ValidationIssue(marker, "strategy must declare ends: YYYY-MM-DD"))


def _parse_iso_date(value: str, marker: Path, field: str, issues: list[ValidationIssue]) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        issues.append(ValidationIssue(marker, f"strategy {field} must be a date in YYYY-MM-DD format"))
        return None


def _validate_strategy_periods_do_not_overlap(strategy_periods: list[StrategyPeriod], issues: list[ValidationIssue]) -> None:
    for index, current in enumerate(sorted(strategy_periods, key=lambda period: (period.starts, period.ends, str(period.marker)))):
        for other in strategy_periods[index + 1 :]:
            if current.starts <= other.ends and other.starts <= current.ends:
                issues.append(
                    ValidationIssue(
                        other.marker,
                        f"strategy period overlaps with {current.marker}: {other.starts.isoformat()}..{other.ends.isoformat()} overlaps {current.starts.isoformat()}..{current.ends.isoformat()}",
                    )
                )

