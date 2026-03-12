"""
Search and SQL API Routes.
"""
import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import chat_service, search_service, sql_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


# ============== Search Engine Chat ==============

class SearchChatRequest(BaseModel):
    """Search chat request."""
    message: str = Field(..., description="User message")
    model: Optional[str] = Field(default=None, description="Model name")
    stream: bool = Field(default=False, description="Enable streaming")


@router.post("/chat/search_engine_chat")
async def search_engine_chat(request: SearchChatRequest):
    """
    Chat with search engine.
    
    POST /chat/search_engine_chat
    """
    try:
        result = await chat_service.search_engine_chat(
            message=request.message,
            model=request.model,
            stream=request.stream
        )
        
        if request.stream:
            from fastapi.responses import StreamingResponse
            
            async def event_stream():
                async for chunk in result:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream"
            )
        
        return {"code": 200, "data": {"content": result}}
    
    except Exception as e:
        logger.error(f"Search chat error: {e}")
        return {"code": 500, "message": str(e)}


# ============== Agent Chat ==============

class AgentChatRequest(BaseModel):
    """Agent chat request."""
    message: str = Field(..., description="User message")
    model: Optional[str] = Field(default=None, description="Model name")
    stream: bool = Field(default=False, description="Enable streaming")


@router.post("/chat/agent_chat")
async def agent_chat(request: AgentChatRequest):
    """
    Chat with Agent.
    
    POST /chat/agent_chat
    """
    try:
        result = await chat_service.agent_chat(
            message=request.message,
            model=request.model,
            stream=request.stream
        )
        
        if request.stream:
            from fastapi.responses import StreamingResponse
            
            async def event_stream():
                async for chunk in result:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream"
            )
        
        return {"code": 200, "data": {"content": result}}
    
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        return {"code": 500, "message": str(e)}


# ============== File Chat ==============

class FileChatRequest(BaseModel):
    """File chat request."""
    message: str = Field(..., description="User message")
    file_path: Optional[str] = Field(default=None, description="File path")
    file_content: Optional[str] = Field(default=None, description="File content")
    model: Optional[str] = Field(default=None, description="Model name")
    stream: bool = Field(default=False, description="Enable streaming")


@router.post("/chat/file_chat")
async def file_chat(request: FileChatRequest):
    """
    Chat with file.
    
    POST /chat/file_chat
    """
    try:
        result = await chat_service.file_chat(
            message=request.message,
            file_path=request.file_path,
            file_content=request.file_content,
            model=request.model,
            stream=request.stream
        )
        
        if request.stream:
            from fastapi.responses import StreamingResponse
            
            async def event_stream():
                async for chunk in result:
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream"
            )
        
        return {"code": 200, "data": {"content": result}}
    
    except Exception as e:
        logger.error(f"File chat error: {e}")
        return {"code": 500, "message": str(e)}


# ============== Text2SQL ==============

class GenerateSQLRequest(BaseModel):
    """Generate SQL request."""
    message: str = Field(..., description="User question")
    metadata: str = Field(default="", description="Database schema")
    model: Optional[str] = Field(default=None, description="Model name")


@router.post("/generate_sql")
async def generate_sql(request: GenerateSQLRequest):
    """
    Generate SQL from natural language.
    
    POST /generate_sql
    """
    try:
        # Load metadata from file if not provided
        metadata = request.metadata
        if not metadata:
            metadata = await sql_service.load_metadata()
        
        result = await sql_service.generate_sql(
            message=request.message,
            metadata=metadata,
            model=request.model
        )
        
        return {"code": 200, "data": result}
    
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        return {"code": 500, "message": str(e)}


@router.post("/generate_sql2")
async def generate_sql_v2(request: GenerateSQLRequest):
    """
    Generate SQL V2.
    
    POST /generate_sql2
    """
    try:
        metadata = request.metadata
        if not metadata:
            metadata = await sql_service.load_metadata()
        
        result = await sql_service.generate_sql_v2(
            message=request.message,
            metadata=metadata,
            model=request.model
        )
        
        return {"code": 200, "data": result}
    
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        return {"code": 500, "message": str(e)}
