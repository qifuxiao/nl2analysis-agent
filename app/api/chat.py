"""
Chat API Routes.
"""
import json
import logging
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services import chat_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: Optional[float] = Field(default=None, description="Temperature")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens")
    stream: bool = Field(default=False, description="Enable streaming")
    history: Optional[List[Dict]] = Field(default=None, description="Conversation history")
    system_prompt: Optional[str] = Field(default=None, description="Custom system prompt")


class ChatResponse(BaseModel):
    """Chat response model."""
    code: int = 200
    message: str = "success"
    data: Optional[Dict] = None


@router.post("/chat")
async def chat_endpoint(request: ChatRequest) -> Dict:
    """
    General chat endpoint.
    
    POST /chat/chat
    """
    try:
        if request.stream:
            # For streaming, return error (use SSE endpoint instead)
            raise HTTPException(
                status_code=400,
                detail="Use /chat/chat/stream for streaming"
            )
        
        result = await chat_service.chat(
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False,
            history=request.history,
            system_prompt=request.system_prompt
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": {"content": result}
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "code": 500,
            "message": str(e),
            "data": None
        }


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint.
    
    POST /chat/chat/stream
    """
    from fastapi.responses import StreamingResponse
    
    async def event_stream():
        try:
            async for chunk in chat_service.chat(
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                history=request.history,
                system_prompt=request.system_prompt
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# Alias for compatibility
@router.post("")
async def chat_alias(request: ChatRequest) -> Dict:
    """Alias for /chat/chat"""
    return await chat_endpoint(request)
