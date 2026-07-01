from __future__ import annotations

from pathlib import Path

from fastapi import Request

from outcome_engineering.product_graph import ProductGraph


def graph_root(request: Request) -> Path:
    return request.app.state.graph_root


def graph(request: Request) -> ProductGraph:
    return ProductGraph(graph_root(request))
