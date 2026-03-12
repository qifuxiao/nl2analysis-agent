"""
Knowledge Base API Routes.
"""
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.services import knowledge_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge_base", tags=["Knowledge Base"])


# Request Models
class CreateKnowledgeBaseRequest(BaseModel):
    """Create knowledge base request."""
    name: str = Field(..., description="Knowledge base name")
    description: str = Field(default="", description="Description")


class DeleteDocsRequest(BaseModel):
    """Delete documents request."""
    knowledge_base_name: str = Field(..., description="Knowledge base name")
    file_names: List[str] = Field(..., description="File names to delete")


class KnowledgeBaseChatRequest(BaseModel):
    """Knowledge base chat request."""
    message: str = Field(..., description="User message")
    knowledge_base_name: str = Field(..., description="Knowledge base name")
    model: Optional[str] = Field(default=None, description="Model name")
    stream: bool = Field(default=False, description="Enable streaming")


@router.post("/create_knowledge_base")
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """
    Create a new knowledge base.
    
    POST /knowledge_base/create_knowledge_base
    """
    result = await knowledge_service.create_knowledge_base(
        name=request.name,
        description=request.description
    )
    return result


@router.get("/list_knowledge_bases")
async def list_knowledge_bases():
    """
    List all knowledge bases.
    
    GET /knowledge_base/list_knowledge_bases
    """
    bases = await knowledge_service.list_knowledge_bases()
    return {"code": 200, "data": bases}


@router.post("/delete_knowledge_base")
async def delete_knowledge_base(name: str = Form(...)):
    """
    Delete a knowledge base.
    
    POST /knowledge_base/delete_knowledge_base
    """
    result = await knowledge_service.delete_knowledge_base(name)
    return result


@router.post("/upload_docs")
async def upload_docs(
    knowledge_base_name: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Upload documents to knowledge base.
    
    POST /knowledge_base/upload_docs
    """
    # Read file content
    content = await file.read()
    content = content.decode("utf-8")
    
    result = await knowledge_service.upload_documents(
        knowledge_base_name=knowledge_base_name,
        documents=[{
            "content": content,
            "metadata": {
                "file_name": file.filename,
                "content_type": file.content_type
            }
        }]
    )
    
    return result


@router.get("/list_files")
async def list_files(knowledge_base_name: str = Query(...)):
    """
    List files in knowledge base.
    
    GET /knowledge_base/list_files
    """
    files = await knowledge_service.list_files(knowledge_base_name)
    return {"code": 200, "data": files}


@router.post("/delete_docs")
async def delete_docs(request: DeleteDocsRequest):
    """
    Delete documents from knowledge base.
    
    POST /knowledge_base/delete_docs
    """
    result = await knowledge_service.delete_documents(
        knowledge_base_name=request.knowledge_base_name,
        file_names=request.file_names
    )
    return result


@router.get("/download_doc")
async def download_doc(
    knowledge_base_name: str = Query(...),
    file_name: str = Query(...)
):
    """
    Download document from knowledge base.
    
    GET /knowledge_base/download_doc
    """
    doc = await knowledge_service.download_document(knowledge_base_name, file_name)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "code": 200,
        "data": {
            "content": doc.get("content"),
            "metadata": doc.get("metadata")
        }
    }


@router.post("/knowledge_base_chat")
async def knowledge_base_chat(request: KnowledgeBaseChatRequest):
    """
    Chat with knowledge base.
    
    POST /chat/knowledge_base_chat
    """
    from app.services import chat_service
    
    try:
        result = await chat_service.knowledge_base_chat(
            message=request.message,
            knowledge_base_name=request.knowledge_base_name,
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
        logger.error(f"Knowledge base chat error: {e}")
        return {"code": 500, "message": str(e)}
