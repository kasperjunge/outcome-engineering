from __future__ import annotations


def parse_icp_references(text: str) -> list[str]:
    """Extract the icp ids a node declares it serves from frontmatter.

    Supports both inline (``icps: [icp.a, icp.b]``) and block list form::

        icps:
          - icp.a
          - icp.b
    """
    return parse_frontmatter_references(text, "icps")


def parse_flywheel_next(text: str) -> list[str]:
    return parse_frontmatter_references(text, "next")


def parse_frontmatter_references(text: str, field: str) -> list[str]:
    value = parse_frontmatter_value(text, field)
    if value is None:
        return []
    references = value if isinstance(value, list) else _parse_inline_list(value)
    return [ref for ref in (_strip_quotes(ref) for ref in references) if ref]


def parse_frontmatter_value(text: str, field: str) -> str | list[str] | None:
    return parse_frontmatter(text).get(field)


def parse_frontmatter_scalar(text: str, field: str) -> str | None:
    value = parse_frontmatter_value(text, field)
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(value)
    return _strip_quotes(value)


def parse_frontmatter(text: str) -> dict[str, str | list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    block = _frontmatter_block(lines)
    if block is None:
        return {}

    metadata: dict[str, str | list[str]] = {}
    index = 0
    while index < len(block):
        parsed = _parse_metadata_entry(block, index)
        if parsed is None:
            index += 1
            continue
        key, value, index = parsed
        metadata[key] = value
    return metadata


def has_fenced_yaml_metadata(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            continue
        return stripped == "```yaml"
    return False


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :])
    return text


def _frontmatter_block(lines: list[str]) -> list[str] | None:
    block: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            return block
        block.append(line)
    return None


def _parse_metadata_entry(block: list[str], index: int) -> tuple[str, str | list[str], int] | None:
    stripped = block[index].strip()
    if not stripped or stripped.startswith("#") or ":" not in stripped:
        return None

    key, raw_value = stripped.split(":", 1)
    key = key.strip()
    value = raw_value.strip()
    if value:
        return key, _strip_quotes(value), index + 1

    items: list[str] = []
    index += 1
    while index < len(block) and block[index].strip().startswith("- "):
        items.append(_strip_quotes(block[index].strip()[2:].strip()))
        index += 1
    return key, items, index


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
