"""
LLM Model API Routes.
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from app.core.llm import (
    list_config_models,
    list_running_models,
    switch_model,
    get_llm_client
)
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm_model", tags=["LLM Model"])


class ChangeModelRequest(BaseModel):
    """Change model request."""
    model: str = Field(..., description="Model ID to switch to")


@router.get("/list_config_models")
async def list_config():
    """
    Get list of configured models.
    
    GET /llm_model/list_config_models
    """
    models = list_config_models()
    return {
        "code": 200,
        "data": models
    }


@router.get("/list_running_models")
async def list_running():
    """
    Get running models status.
    
    GET /llm_model/list_running_models
    """
    models = list_running_models()
    return {
        "code": 200,
        "data": models
    }


@router.post("/change")
async def change_model(request: ChangeModelRequest):
    """
    Switch default model.
    
    POST /llm_model/change
    """
    result = switch_model(request.model)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return {
        "code": 200,
        "message": result.get("message"),
        "data": {"current_model": result.get("current_model")}
    }
