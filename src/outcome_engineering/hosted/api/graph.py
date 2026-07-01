from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from outcome_engineering.hosted.dependencies import graph_root
from outcome_engineering.hosted.errors import ensure_valid_graph, resolve_or_http
from outcome_engineering.product_graph.model import KIND_TO_RELATIONSHIP
from outcome_engineering.product_graph.read import build_graph_payload, context_node, list_nodes, show_node, trace_node

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/graph")
def graph_payload(root: Path = Depends(graph_root)) -> dict:
    ensure_valid_graph(root)
    return build_graph_payload(root, read_only=True, include_source=True)


@router.get("/nodes")
def nodes(
    kind: Annotated[str | None, Query(description="Optional graph node kind filter.")] = None,
    root: Path = Depends(graph_root),
) -> dict:
    ensure_valid_graph(root)
    return list_nodes(root, normalize_kind(kind))


@router.get("/nodes/{selector}/trace")
def trace(selector: str, root: Path = Depends(graph_root)) -> dict:
    ensure_valid_graph(root)
    return resolve_or_http(trace_node, root, selector)


@router.get("/nodes/{selector}/context")
def context(selector: str, root: Path = Depends(graph_root)) -> dict:
    ensure_valid_graph(root)
    return resolve_or_http(context_node, root, selector)


@router.get("/nodes/{selector}")
def node(selector: str, root: Path = Depends(graph_root)) -> dict:
    ensure_valid_graph(root)
    return resolve_or_http(show_node, root, selector)


def normalize_kind(kind: str | None) -> str | None:
    if kind is None:
        return None
    normalized = kind[:-1] if kind.endswith("s") else kind
    if normalized not in KIND_TO_RELATIONSHIP and normalized not in {"vision"}:
        supported = ", ".join(sorted([*KIND_TO_RELATIONSHIP, "vision"]))
        raise HTTPException(status_code=400, detail=f"unsupported node kind {kind!r}; expected one of: {supported}")
    return normalized
