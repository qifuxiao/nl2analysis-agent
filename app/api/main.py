"""
FastAPI application - API endpoints for the multi-agent system.
"""
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sse_starlette import EventSourceResponse

from app.core.config import settings
from app.graph.workflow import run_agent
from app.memory.backend import get_memory, ChatMessage
from app.llm.client import get_llm
from app.agents.general import GeneralChatAgent

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent System based on LangGraph",
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    user_id: str = Field(default="default", description="User identifier")
    session_id: str = Field(default="default", description="Session identifier")
    stream: bool = Field(default=False, description="Enable streaming response")
    agent_type: Optional[str] = Field(default=None, description="Force specific agent type")


class ChatResponse(BaseModel):
    """Chat response model."""
    content: str
    agent_type: str
    confidence: float = 0.0
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class StreamChunk(BaseModel):
    """Streaming chunk model."""
    content: str
    agent_type: str
    done: bool = False


# ============================================================================
# Authentication
# ============================================================================

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key if configured."""
    if settings.API_KEY:
        if not x_api_key:
            raise HTTPException(status_code=401, detail="API key required")
        if x_api_key != settings.API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API key")
    return "ok"


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/v1/agent/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    auth: str = Depends(verify_api_key),
):
    """
    Main chat endpoint.
    
    Processes user messages through the multi-agent system,
    automatically routing to appropriate agents based on intent.
    """
    try:
        # Get memory
        memory = get_memory()
        
        # Load conversation history
        history = memory.get_history_for_llm(
            request.user_id,
            request.session_id,
            limit=10
        )
        
        # Run agent
        result = await run_agent(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            history=history,
        )
        
        # Extract response
        agent_response = result.get("agent_response", "")
        selected_agent = result.get("selected_agent", {})
        agent_type = selected_agent.value if hasattr(selected_agent, 'value') else str(selected_agent)
        
        # Try to parse JSON response
        try:
            response_data = json.loads(agent_response)
            content = response_data.get("content", agent_response)
        except (json.JSONDecodeError, TypeError):
            content = agent_response
        
        # Get confidence from intent
        intent = result.get("intent", {})
        confidence = intent.get("confidence", 0.0) if isinstance(intent, dict) else 0.0
        
        return ChatResponse(
            content=content,
            agent_type=agent_type,
            confidence=confidence,
            session_id=request.session_id,
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agent/stream")
async def stream_chat(
    request: ChatRequest,
    auth: str = Depends(verify_api_key),
):
    """
    Streaming chat endpoint.
    
    Returns response as Server-Sent Events (SSE) for real-time streaming.
    """
    async def event_generator():
        try:
            # Get memory
            memory = get_memory()
            
            # Load conversation history
            history = memory.get_history_for_llm(
                request.user_id,
                request.session_id,
                limit=10
            )
            
            # Determine agent type
            if request.agent_type:
                # Force specific agent
                from app.graph.state import AgentType
                try:
                    agent_type = AgentType(request.agent_type.lower())
                except ValueError:
                    agent_type = AgentType.GENERAL
                
                # Run specific agent
                if agent_type == AgentType.GENERAL:
                    agent = GeneralChatAgent()
                    async for chunk in agent.stream(
                        message=request.message,
                        user_id=request.user_id,
                        session_id=request.session_id,
                        history=history,
                    ):
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                else:
                    # Run through workflow
                    result = await run_agent(
                        message=request.message,
                        user_id=request.user_id,
                        session_id=request.session_id,
                        history=history,
                    )
                    content = result.get("agent_response", "")
                    yield f"data: {json.dumps({'content': content, 'done': True})}\n\n"
            else:
                # Run full workflow
                result = await run_agent(
                    message=request.message,
                    user_id=request.user_id,
                    session_id=request.session_id,
                    history=history,
                )
                content = result.get("agent_response", "")
                
                # For now, send as single chunk
                # Can be extended to token-level streaming per agent
                yield f"data: {json.dumps({'content': content, 'done': True})}\n\n"
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/v1/session/{user_id}/{session_id}")
async def get_session(
    user_id: str,
    session_id: str,
    auth: str = Depends(verify_api_key),
):
    """Get session conversation history."""
    memory = get_memory()
    messages = memory.load(user_id, session_id)
    
    return {
        "user_id": user_id,
        "session_id": session_id,
        "messages": [msg.to_dict() for msg in messages],
    }


@app.delete("/api/v1/session/{user_id}/{session_id}")
async def clear_session(
    user_id: str,
    session_id: str,
    auth: str = Depends(verify_api_key),
):
    """Clear session conversation history."""
    memory = get_memory()
    memory.clear(user_id, session_id)
    
    return {"status": "cleared", "session_id": session_id}


@app.get("/api/v1/agents")
async def list_agents(auth: str = Depends(verify_api_key)):
    """List available agents."""
    from app.graph.state import AgentType
    
    return {
        "agents": [
            {
                "name": agent.value,
                "description": description,
            }
            for agent, description in [
                (AgentType.NL2SQL, "Natural language to SQL"),
                (AgentType.ANALYSIS, "Data analysis and visualization"),
                (AgentType.FILE, "File operations"),
                (AgentType.SEARCH, "Web search"),
                (AgentType.GENERAL, "General chat (fallback)"),
            ]
        ]
    }


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
