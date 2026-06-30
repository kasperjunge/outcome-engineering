from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from outcome_engineering.model import KIND_TO_RELATIONSHIP
from outcome_engineering.read import (
    GraphReader,
    NodeResolutionError,
)
from outcome_engineering.ui import graph_page


def graph_root_from_env() -> Path:
    return Path(os.environ.get("OE_GRAPH_ROOT", "product")).expanduser().resolve()


def create_app(root: Path | None = None) -> FastAPI:
    reader = GraphReader(root or graph_root_from_env())
    app = FastAPI(
        title="Outcome Engineering hosted graph",
        description="Read-only HTTP access to one Outcome Engineering product graph.",
        version="0.1.0",
    )

    @app.get("/", response_class=HTMLResponse)
    def page() -> str:
        return graph_page(read_only=True)

    @app.get("/system/health")
    def health() -> dict:
        payload = reader.validation_payload()
        return {"ok": payload["valid"], "graphRoot": str(reader.root), "source": payload["source"]}

    @app.get("/api/validate")
    def validate_graph() -> dict:
        return reader.validation_payload()

    @app.get("/api/graph")
    def graph() -> dict:
        ensure_valid_graph(reader)
        return reader.graph_payload(read_only=True, include_source=True)

    @app.get("/api/nodes")
    def nodes(kind: Annotated[str | None, Query(description="Optional graph node kind filter.")] = None) -> dict:
        ensure_valid_graph(reader)
        normalized_kind = normalize_kind(kind)
        return reader.list_nodes(normalized_kind)

    @app.get("/api/nodes/{selector}/trace")
    def trace(selector: str) -> dict:
        ensure_valid_graph(reader)
        return resolve_or_http(reader.trace_node, selector)

    @app.get("/api/nodes/{selector}/context")
    def context(selector: str) -> dict:
        ensure_valid_graph(reader)
        return resolve_or_http(reader.context_node, selector)

    @app.get("/api/nodes/{selector}")
    def node(selector: str) -> dict:
        ensure_valid_graph(reader)
        return resolve_or_http(reader.show_node, selector)

    return app


def ensure_valid_graph(reader: GraphReader) -> None:
    payload = reader.validation_payload()
    if not payload["valid"]:
        raise HTTPException(status_code=503, detail=payload)


def normalize_kind(kind: str | None) -> str | None:
    if kind is None:
        return None
    normalized = kind[:-1] if kind.endswith("s") else kind
    if normalized not in KIND_TO_RELATIONSHIP and normalized not in {"vision"}:
        supported = ", ".join(sorted([*KIND_TO_RELATIONSHIP, "vision"]))
        raise HTTPException(status_code=400, detail=f"unsupported node kind {kind!r}; expected one of: {supported}")
    return normalized


def resolve_or_http(fn, selector: str) -> dict:
    try:
        return fn(selector)
    except NodeResolutionError as error:
        status = 409 if error.reason == "ambiguous" else 404
        raise HTTPException(status_code=status, detail={"error": error.reason, "selector": selector}) from error


app = create_app()
