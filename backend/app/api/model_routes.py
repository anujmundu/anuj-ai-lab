from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Any

from app.rag.routing.model_router import (
    dynamic_model_router,
    TaskType,
    ModelRecommendation,
)

router = APIRouter(prefix="/models", tags=["Dynamic Model Routing"])


class ModelRouteRequest(BaseModel):
    query: str = Field(..., description="Query or prompt to route")
    task_type: TaskType | None = Field(default=None, description="Explicit task type if already known")
    has_image: bool = Field(default=False, description="Whether the request involves visual/image analysis")
    user_override_model: str | None = Field(default=None, description="Manual model override")


@router.get("/available", response_model=dict[str, Any])
def get_available_models() -> dict[str, Any]:
    """List all locally installed Ollama models and their assigned tiers."""
    installed = dynamic_model_router.get_installed_models()
    return {
        "installed_models": installed,
        "preferred_tiers": {k.value: v for k, v in dynamic_model_router.preferred_models.items()},
    }


class SetPrimaryTierRequest(BaseModel):
    task_type: TaskType = Field(..., description="Task tier to update")
    model_name: str = Field(..., description="Model name to promote to primary")


@router.post("/tiers/primary", response_model=dict[str, Any])
def set_primary_model_tier(req: SetPrimaryTierRequest) -> dict[str, Any]:
    """Reassign the primary model for a specific task tier."""
    updated = dynamic_model_router.set_primary_model(req.task_type, req.model_name)
    return {
        "status": "success",
        "task_type": req.task_type.value,
        "primary_model": req.model_name,
        "tier_models": updated,
        "preferred_tiers": {k.value: v for k, v in dynamic_model_router.preferred_models.items()},
    }


@router.post("/route", response_model=ModelRecommendation)
def route_model_request(req: ModelRouteRequest) -> ModelRecommendation:
    """Determine the optimal local model for the query."""
    return dynamic_model_router.route_model(
        query=req.query,
        task_type=req.task_type,
        has_image=req.has_image,
        user_override_model=req.user_override_model,
    )
