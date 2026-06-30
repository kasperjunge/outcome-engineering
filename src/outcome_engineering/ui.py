from __future__ import annotations

from importlib import resources


READ_ONLY_SENTINEL = "const OE_READ_ONLY = false;"


def graph_page(*, read_only: bool = False) -> str:
    page = (resources.files("outcome_engineering") / "templates" / "graph.html").read_text(encoding="utf-8")
    return page.replace(READ_ONLY_SENTINEL, f"const OE_READ_ONLY = {'true' if read_only else 'false'};")
