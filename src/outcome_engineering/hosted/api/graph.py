from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from outcome_engineering.hosted.dependencies import graph as graph_dependency
from outcome_engineering.hosted.errors import ensure_valid_graph, resolve_or_http
from outcome_engineering.hosted.source import source_dict
from outcome_engineering.product_graph import ProductGraph
from outcome_engineering.product_graph.read import build_graph_payload, context_node, list_nodes, show_node, trace_node

router = APIRouter(prefix="/api", tags=["graph"])


@router.get("/graph")
def graph_payload(graph: ProductGraph = Depends(graph_dependency)) -> dict:
    ensure_valid_graph(graph)
    return with_source(build_graph_payload(graph, read_only=True), graph)


@router.get("/nodes")
def nodes(
    kind: Annotated[str | None, Query(description="Optional graph node kind filter.")] = None,
    graph: ProductGraph = Depends(graph_dependency),
) -> dict:
    ensure_valid_graph(graph)
    return with_source(list_nodes(graph, normalize_kind(kind)), graph)


@router.get("/nodes/{selector}/trace")
def trace(selector: str, graph: ProductGraph = Depends(graph_dependency)) -> dict:
    ensure_valid_graph(graph)
    return with_source(resolve_or_http(trace_node, graph, selector), graph)


@router.get("/nodes/{selector}/context")
def context(selector: str, graph: ProductGraph = Depends(graph_dependency)) -> dict:
    ensure_valid_graph(graph)
    return with_source(resolve_or_http(context_node, graph, selector), graph)


@router.get("/nodes/{selector}")
def node(selector: str, graph: ProductGraph = Depends(graph_dependency)) -> dict:
    ensure_valid_graph(graph)
    return with_source(resolve_or_http(show_node, graph, selector), graph)


def with_source(payload: dict, graph: ProductGraph) -> dict:
    return {**payload, "source": source_dict(graph.root)}


def normalize_kind(kind: str | None) -> str | None:
    if kind is None:
        return None
    normalized = kind[:-1] if kind.endswith("s") else kind
    if normalized not in ProductGraph.kinds() and normalized not in {"vision"}:
        supported = ", ".join(sorted([*ProductGraph.kinds(), "vision"]))
        raise HTTPException(status_code=400, detail=f"unsupported node kind {kind!r}; expected one of: {supported}")
    return normalized
