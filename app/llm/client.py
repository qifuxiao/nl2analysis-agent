'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:33:55
FilePath: /nl2analysis-agent/app/llm/client.py
'''
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_retries: int = 2,
    request_timeout: int = 120
) -> ChatOpenAI:
    """
    获取 LLM 客户端实例（带完整容错机制）
    
    Args:
        model: 模型名称（优先使用参数，其次配置）
        temperature: 生成温度
        max_retries: 最大重试次数
        request_timeout: 请求超时时间（秒）
    
    Returns:
        ChatOpenAI 实例
    
    Raises:
        ValueError: 关键配置缺失且无法自动修复
    """
    # 1. 确定模型名称（优先级：参数 > 配置 > 默认值）
    model_name = model or settings.LLM_MODEL or "gpt-4o-mini"
    if not model_name.strip():
        raise ValueError("❌ LLM_MODEL 配置为空且未提供 model 参数")
    
    # 2. 处理 API Key（自部署场景容错）
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        # 自部署模型通常不需要真实 Key，但 LangChain 要求非空字符串
        if settings.BASE_URL:
            logger.warning(
                "⚠️  OPENAI_API_KEY 未设置，但检测到 BASE_URL（自部署模式）。"
                "使用占位符 'dummy-key-for-self-hosted' 绕过校验。"
            )
            api_key = "dummy-key-for-self-hosted"
        else:
            raise ValueError(
                "❌ OPENAI_API_KEY 未设置！\n"
                "  • 公有云服务：请设置环境变量 OPENAI_API_KEY\n"
                "  • 自部署模型：请同时设置 BASE_URL 环境变量"
            )
    
    # 3. 构建基础参数
    llm_params = {
        "model": model_name.strip(),
        "api_key": api_key,
        "temperature": temperature,
        "max_retries": max_retries,
        "request_timeout": request_timeout,
        "verbose": settings.DEBUG if hasattr(settings, "DEBUG") else False,
        "base_url": settings.BASE_URL if hasattr(settings, "BASE_URL") and settings.BASE_URL else None
    }
    
    # 4. 添加自部署专属配置（BASE_URL）
    if hasattr(settings, "BASE_URL") and settings.BASE_URL:
        llm_params["base_url"] = settings.BASE_URL.rstrip("/")
        logger.info(f"🔌 使用自部署模型: {settings.BASE_URL} | 模型: {model_name}")
    else:
        logger.info(f"☁️  使用公有云模型: {model_name}")
    
    # 5. 安全初始化（捕获配置错误）
    try:
        llm = ChatOpenAI(**llm_params)
        logger.info(f"✅ LLM 客户端初始化成功 | 模型: {model_name}")
        return llm
    except Exception as e:
        logger.exception("❌ LLM 客户端初始化失败")
        raise RuntimeError(
            f"LLM 初始化失败: {str(e)}\n"
            f"  模型: {model_name}\n"
            f"  Base URL: {llm_params.get('base_url', 'N/A')}\n"
            f"  请检查配置和网络连通性"
        ) from e