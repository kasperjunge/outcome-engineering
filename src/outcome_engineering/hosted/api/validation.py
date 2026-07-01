from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends

from outcome_engineering.hosted.dependencies import graph_root
from outcome_engineering.product_graph.read import validation_payload

router = APIRouter(tags=["validation"])


@router.get("/system/health")
def health(root: Path = Depends(graph_root)) -> dict:
    payload = validation_payload(root)
    return {"ok": payload["valid"], "graphRoot": str(root), "source": payload["source"]}


@router.get("/api/validate")
def validate_graph(root: Path = Depends(graph_root)) -> dict:
    return validation_payload(root)
