"""
Chat Service - Core chat functionality.
"""
import json
import logging
from typing import Optional, Dict, Any, List, AsyncGenerator
from app.core.llm import get_llm_client, get_client
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompts for different chat modes
SYSTEM_PROMPTS = {
    "default": """你是一个专业的AI助手，请用中文回答用户的问题。
    - 回答要准确、简洁、有帮助
    - 如果不确定某事，请诚实说明
    - 适当使用格式化使回答更清晰""",
    
    "knowledge_base": """你是一个知识库问答助手。请根据提供的知识库内容回答用户的问题。
    - 只根据提供的上下文回答，不要编造信息
    - 如果上下文中没有相关信息，请说明"抱歉，我在知识库中没有找到相关信息"
    - 引用相关来源""",
    
    "search": """你是一个搜索助手。请根据搜索结果回答用户的问题。
    - 基于搜索到的信息进行回答
    - 引用信息来源
    - 如果搜索结果不足，请说明""",
    
    "agent": """你是一个智能Agent助手。你可以调用各种工具来完成任务。
    - 分析用户需求，选择合适的工具
    - 按步骤执行任务
    - 返回结果""",
    
    "file": """你是一个文档分析助手。请分析用户上传的文档内容并回答问题。
    - 仔细阅读文档内容
    - 只基于文档内容回答问题
    - 如果文档中没有相关信息，请说明""",
}


async def chat(
    message: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    history: Optional[List[Dict]] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> Union[str, AsyncGenerator[str, None]]:
    """
    General chat function.
    
    Args:
        message: User message
        model: Model name (optional)
        temperature: Temperature (optional)
        max_tokens: Max tokens (optional)
        stream: Enable streaming
        history: Conversation history
        system_prompt: Custom system prompt
        **kwargs: Additional parameters
        
    Returns:
        Response string or stream
    """
    client = get_client(model) if model else get_llm_client()
    
    # Build messages with history
    messages = []
    if history:
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": content})
    
    messages.append({"role": "user", "content": message})
    
    if stream:
        return client.chat_stream(
            message=messages,
            system_prompt=system_prompt or SYSTEM_PROMPTS["default"],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    else:
        return client.chat(
            message=messages,
            system_prompt=system_prompt or SYSTEM_PROMPTS["default"],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )


async def knowledge_base_chat(
    message: str,
    knowledge_base_name: str,
    model: Optional[str] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Knowledge base chat function.
    
    Args:
        message: User message
        knowledge_base_name: Knowledge base name
        model: Model name
        stream: Enable streaming
        **kwargs: Additional parameters
        
    Returns:
        Response string or stream
    """
    # Import here to avoid circular import
    from app.services.knowledge_service import search_knowledge
    
    # Search relevant context from knowledge base
    context = await search_knowledge(knowledge_base_name, message)
    
    # Build system prompt with context
    system_prompt = f"""你是一个知识库问答助手。请根据以下知识库内容回答用户的问题。

知识库: {knowledge_base_name}

相关上下文:
{context}

请根据以上上下文回答用户的问题。如果上下文中没有相关信息，请说明。"""
    
    return await chat(
        message=message,
        model=model,
        stream=stream,
        system_prompt=system_prompt,
        **kwargs
    )


async def search_engine_chat(
    message: str,
    model: Optional[str] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Search engine chat function.
    
    Args:
        message: User message
        model: Model name
        stream: Enable streaming
        **kwargs: Additional parameters
        
    Returns:
        Response string or stream
    """
    # Import here to avoid circular import
    from app.services.search_service import web_search
    
    # Search the web
    search_results = await web_search(message, max_results=5)
    
    # Build system prompt with search results
    system_prompt = f"""你是一个搜索助手。请根据以下搜索结果回答用户的问题。

搜索查询: {message}

搜索结果:
{search_results}

请根据以上搜索结果回答用户的问题，引用相关来源。"""
    
    return await chat(
        message=message,
        model=model,
        stream=stream,
        system_prompt=system_prompt,
        **kwargs
    )


async def agent_chat(
    message: str,
    model: Optional[str] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, AsyncGenerator[str, None]]:
    """
    Agent chat function.
    
    This is a simple agent implementation. For complex tasks,
    you can integrate with LangGraph or other agent frameworks.
    
    Args:
        message: User message
        model: Model name
        stream: Enable streaming
        **kwargs: Additional parameters
        
    Returns:
        Response string or stream
    """
    system_prompt = """你是一个智能Agent助手。你可以分析用户需求并调用合适的工具来完成任务。

可用的工具:
- web_search: 搜索互联网
- knowledge_base_search: 搜索知识库
- sql_query: 查询数据库

请分析用户需求，选择合适的工具或直接回答。"""
    
    return await chat(
        message=message,
        model=model,
        stream=stream,
        system_prompt=system_prompt,
        **kwargs
    )


async def file_chat(
    message: str,
    file_path: Optional[str] = None,
    file_content: Optional[str] = None,
    model: Optional[str] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, AsyncGenerator[str, None]]:
    """
    File chat function.
    
    Args:
        message: User message
        file_path: Path to uploaded file
        file_content: File content (if already read)
        model: Model name
        stream: Enable streaming
        **kwargs: Additional parameters
        
    Returns:
        Response string or stream
    """
    # Read file content if path provided
    if file_path and not file_content:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    if not file_content:
        return "请提供文件内容或文件路径"
    
    # Limit content length
    if len(file_content) > 50000:
        file_content = file_content[:50000] + "\n... (内容已截断)"
    
    system_prompt = f"""你是一个文档分析助手。请根据以下文档内容回答用户的问题。

文档内容:
{file_content}

请根据以上文档内容回答用户的问题。"""
    
    return await chat(
        message=message,
        model=model,
        stream=stream,
        system_prompt=system_prompt,
        **kwargs
    )
