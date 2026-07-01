from __future__ import annotations

from fastapi import APIRouter

from outcome_engineering.hosted.api.graph import router as graph_router
from outcome_engineering.hosted.api.validation import router as validation_router

router = APIRouter()
router.include_router(validation_router)
router.include_router(graph_router)
