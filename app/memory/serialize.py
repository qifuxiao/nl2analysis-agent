# app/memory/serialize.py
from langchain.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


def serialize_object(obj):
    """
    递归安全序列化对象为 JSON 可存储形式
    支持 AIMessage、HumanMessage、SystemMessage
    """
    if isinstance(obj, (AIMessage, HumanMessage, SystemMessage)):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content,
            "additional_kwargs": getattr(obj, "additional_kwargs", {})
        }
    elif isinstance(obj, list):
        return [serialize_object(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: serialize_object(v) for k, v in obj.items()}
    else:
        return obj
