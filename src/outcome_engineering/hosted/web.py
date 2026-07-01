from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from outcome_engineering.local_ui.server import graph_page

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def page() -> str:
    return graph_page(read_only=True)
