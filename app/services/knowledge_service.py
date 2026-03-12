"""
Knowledge Base Service - RAG functionality.
"""
import os
import json
import logging
from typing import Optional, List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

# In-memory knowledge base storage (for demo)
# In production, use ChromaDB or other vector database
_knowledge_bases: Dict[str, Dict] = {}


async def create_knowledge_base(name: str, description: str = "") -> Dict:
    """
    Create a new knowledge base.
    
    Args:
        name: Knowledge base name
        description: Description
        
    Returns:
        Creation result
    """
    if name in _knowledge_bases:
        return {"success": False, "message": f"Knowledge base '{name}' already exists"}
    
    _knowledge_bases[name] = {
        "name": name,
        "description": description,
        "files": [],
        "documents": []
    }
    
    logger.info(f"Created knowledge base: {name}")
    
    return {
        "success": True,
        "message": f"Knowledge base '{name}' created",
        "data": {"name": name, "description": description}
    }


async def list_knowledge_bases() -> List[Dict]:
    """
    List all knowledge bases.
    
    Returns:
        List of knowledge bases
    """
    return [
        {"name": kb["name"], "description": kb["description"]}
        for kb in _knowledge_bases.values()
    ]


async def delete_knowledge_base(name: str) -> Dict:
    """
    Delete a knowledge base.
    
    Args:
        name: Knowledge base name
        
    Returns:
        Deletion result
    """
    if name not in _knowledge_bases:
        return {"success": False, "message": f"Knowledge base '{name}' not found"}
    
    del _knowledge_bases[name]
    
    return {"success": True, "message": f"Knowledge base '{name}' deleted"}


async def upload_documents(
    knowledge_base_name: str,
    documents: List[Dict]
) -> Dict:
    """
    Upload documents to knowledge base.
    
    Args:
        knowledge_base_name: Knowledge base name
        documents: List of documents
        
    Returns:
        Upload result
    """
    if knowledge_base_name not in _knowledge_bases:
        return {"success": False, "message": f"Knowledge base '{knowledge_base_name}' not found"}
    
    kb = _knowledge_bases[knowledge_base_name]
    
    for doc in documents:
        kb["documents"].append({
            "content": doc.get("content", ""),
            "metadata": doc.get("metadata", {})
        })
    
    logger.info(f"Uploaded {len(documents)} documents to {knowledge_base_name}")
    
    return {
        "success": True,
        "message": f"Uploaded {len(documents)} documents"
    }


async def list_files(knowledge_base_name: str) -> List[Dict]:
    """
    List files in knowledge base.
    
    Args:
        knowledge_base_name: Knowledge base name
        
    Returns:
        List of files
    """
    if knowledge_base_name not in _knowledge_bases:
        return []
    
    kb = _knowledge_bases[knowledge_base_name]
    return kb.get("files", [])


async def delete_documents(
    knowledge_base_name: str,
    file_names: List[str]
) -> Dict:
    """
    Delete documents from knowledge base.
    
    Args:
        knowledge_base_name: Knowledge base name
        file_names: File names to delete
        
    Returns:
        Deletion result
    """
    if knowledge_base_name not in _knowledge_bases:
        return {"success": False, "message": f"Knowledge base '{knowledge_base_name}' not found"}
    
    kb = _knowledge_bases[knowledge_base_name]
    
    # Filter out deleted files
    original_count = len(kb["documents"])
    kb["documents"] = [
        d for d in kb["documents"]
        if d.get("metadata", {}).get("file_name") not in file_names
    ]
    
    deleted_count = original_count - len(kb["documents"])
    
    return {
        "success": True,
        "message": f"Deleted {deleted_count} documents"
    }


async def search_knowledge(
    knowledge_base_name: str,
    query: str,
    top_k: int = 3
) -> str:
    """
    Search knowledge base for relevant context.
    
    This is a simple implementation. In production, use:
    - ChromaDB with embeddings
    - FAISS
    - Weaviate
    
    Args:
        knowledge_base_name: Knowledge base name
        query: Search query
        top_k: Number of results
        
    Returns:
        Relevant context as string
    """
    if knowledge_base_name not in _knowledge_bases:
        return ""
    
    kb = _knowledge_bases[knowledge_base_name]
    documents = kb.get("documents", [])
    
    if not documents:
        return "知识库为空"
    
    # Simple keyword matching (replace with embeddings in production)
    query_lower = query.lower()
    results = []
    
    for i, doc in enumerate(documents):
        content = doc.get("content", "")
        # Simple relevance score based on keyword overlap
        query_words = set(query_lower.split())
        content_words = set(content.lower().split())
        score = len(query_words & content_words)
        
        if score > 0:
            results.append({
                "index": i,
                "content": content,
                "score": score
            })
    
    # Sort by score and take top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_k]
    
    if not results:
        return "没有找到相关内容"
    
    # Format context
    context = "\n\n---\n\n".join([
        f"【相关文档 {i+1}】\n{r['content'][:1000]}"
        for i, r in enumerate(results)
    ])
    
    return context


async def download_document(
    knowledge_base_name: str,
    file_name: str
) -> Optional[Dict]:
    """
    Download a document from knowledge base.
    
    Args:
        knowledge_base_name: Knowledge base name
        file_name: File name
        
    Returns:
        Document data or None
    """
    if knowledge_base_name not in _knowledge_bases:
        return None
    
    kb = _knowledge_bases[knowledge_base_name]
    
    for doc in kb.get("documents", []):
        if doc.get("metadata", {}).get("file_name") == file_name:
            return doc
    
    return None
