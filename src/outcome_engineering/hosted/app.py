from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from outcome_engineering.hosted.api.routes import router as api_router
from outcome_engineering.hosted.web import router as web_router


def graph_root_from_env() -> Path:
    return Path(os.environ.get("OE_GRAPH_ROOT", "product")).expanduser().resolve()


def create_app(root: Path | None = None) -> FastAPI:
    graph_root = (root or graph_root_from_env()).resolve()
    app = FastAPI(
        title="Outcome Engineering hosted graph",
        description="Read-only HTTP access to one Outcome Engineering product graph.",
        version="0.1.0",
    )
    app.state.graph_root = graph_root
    app.include_router(web_router)
    app.include_router(api_router)
    return app


app = create_app()
