import asyncio
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage

from app.memory.backend import save_session
from app.memory.models import SessionMemory, ChatMessage
from app.core.logger import logger
from app.utils.json_utils import safe_json_dumps


async def post_memory_node(state: Dict[str, Any]):
    """
    将 GraphState 保存到 Redis：
    - 自动序列化 history 中的 AIMessage / HumanMessage / ChatMessage
    - 使用统一 safe_json_dumps 处理 Decimal / numpy / datetime
    """

    loop = asyncio.get_event_loop()

    def _save():
        try:
            user_id = state.get("user_id")
            session_id = state.get("session_id")

            if not user_id or not session_id:
                raise ValueError("user_id or session_id missing in state")

            history = state.get("history", [])

            messages = []

            for m in history:

                # 已经是 ChatMessage
                if isinstance(m, ChatMessage):
                    messages.append(m)

                # LangChain 原生消息
                elif isinstance(m, (AIMessage, HumanMessage)):
                    messages.append(
                        ChatMessage(
                            type=m.type,
                            content=m.content,
                            additional_kwargs=getattr(m, "additional_kwargs", {})
                        )
                    )

                # dict 结构
                elif isinstance(m, dict):
                    messages.append(ChatMessage.from_dict(m))

                else:
                    logger.warning(f"[post_memory_node] 未知消息类型忽略: {type(m)}")

            session_memory = SessionMemory(
                user_id=user_id,
                session_id=session_id,
                messages=messages
            )

            # ✅ 使用统一企业级 JSON 序列化
            json_str = safe_json_dumps(session_memory.to_dict())

            logger.info(f"[nl2analysis] serialized session_data: {json_str}")

            # 保存
            save_session(session_memory)

        except Exception as e:
            logger.exception(f"[post_memory_node] save_session error: {e}")

    await loop.run_in_executor(None, _save)

    return {}
