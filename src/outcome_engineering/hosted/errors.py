from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import HTTPException

from outcome_engineering.product_graph.core import NodeResolutionError
from outcome_engineering.product_graph.read import validation_payload


def ensure_valid_graph(root: Path) -> None:
    payload = validation_payload(root)
    if not payload["valid"]:
        raise HTTPException(status_code=503, detail=payload)


def resolve_or_http(fn: Callable[[Path, str], dict], root: Path, selector: str) -> dict:
    try:
        return fn(root, selector)
    except NodeResolutionError as error:
        status = 409 if error.reason == "ambiguous" else 404
        raise HTTPException(status_code=status, detail={"error": error.reason, "selector": selector}) from error
