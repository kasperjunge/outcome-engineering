from __future__ import annotations

from collections.abc import Callable

from fastapi import HTTPException

from outcome_engineering.product_graph import NodeResolutionError, ProductGraph
from outcome_engineering.product_graph.read import validation_payload


def ensure_valid_graph(graph: ProductGraph) -> None:
    payload = validation_payload(graph)
    if not payload["valid"]:
        raise HTTPException(status_code=503, detail=payload)


def resolve_or_http(fn: Callable[[ProductGraph, str], dict], graph: ProductGraph, selector: str) -> dict:
    try:
        return fn(graph, selector)
    except NodeResolutionError as error:
        status = 409 if error.reason == "ambiguous" else 404
        raise HTTPException(status_code=status, detail={"error": error.reason, "selector": selector}) from error
