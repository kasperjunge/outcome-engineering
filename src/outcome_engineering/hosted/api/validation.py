from __future__ import annotations

from fastapi import APIRouter, Depends

from outcome_engineering.hosted.dependencies import graph as graph_dependency
from outcome_engineering.hosted.source import source_dict
from outcome_engineering.product_graph import ProductGraph
from outcome_engineering.product_graph.read import validation_payload

router = APIRouter(tags=["validation"])


@router.get("/system/health")
def health(graph: ProductGraph = Depends(graph_dependency)) -> dict:
    payload = validation_payload(graph)
    return {"ok": payload["valid"], "graphRoot": str(graph.root), "source": source_dict(graph.root)}


@router.get("/api/validate")
def validate_graph(graph: ProductGraph = Depends(graph_dependency)) -> dict:
    return {**validation_payload(graph), "source": source_dict(graph.root)}
