'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:31:11
FilePath: /alexqi/develop/nl2analysis-agent/app/api/nl2analysis.py
'''
# app/api/nl2analysis.py
import json
import asyncio
import math
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from app.agent.graph import app_graph
from app.tools.db_tool import clean_nans
router = APIRouter()

class QueryReq(BaseModel):
    query: str
    user_id: str = "default_user"     # 添加默认值，防止旧客户端报错
    session_id: str = "default_session"

@router.post("/nl2analysis")
def nl2analysis(req: QueryReq):
    # 将接收到的参数全部塞进 Graph 的初始输入中
    result= app_graph.invoke({
        "query": req.query, 
        "history": [],
        "user_id": req.user_id,
        "session_id": req.session_id
    })

    return clean_nans(jsonable_encoder(result))
def safe_json_dumps(obj):
    """处理 NaN/Inf 并序列化"""
    def _clean(o):
        if isinstance(o, float):
            return None if math.isnan(o) or math.isinf(o) else o
        if isinstance(o, dict): return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, list): return [_clean(x) for x in o]
        return o
    return json.dumps(_clean(jsonable_encoder(obj)), ensure_ascii=False)

@router.post("/nl2analysis/stream")
async def nl2analysis_stream(req: QueryReq):
    async def event_generator():
        inputs = {"query": req.query, "user_id": req.user_id, "session_id": req.session_id, "history": []}
        try:
            # 使用 updates 模式查看节点产出
            async for event in app_graph.astream(inputs, stream_mode="updates"):
                for node_name, output in event.items():
                    payload = {"node": node_name, "output": output}
                    yield f"data: {safe_json_dumps(payload)}\n\n"
                    
                    # 关键修复：强制让出 CPU，给 FastAPI 发送 buffer 的机会
                    await asyncio.sleep(0.01) 
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform", # 禁止代理压缩
            "X-Accel-Buffering": "no",                # 专门针对 Nginx
        }
    )
@router.get("/test-stream")
async def test_stream():
    async def generate():
        for i in range(5):
            yield f"data: ping {i}\n\n"
            await asyncio.sleep(1) # 每秒发一次
    return StreamingResponse(generate(), media_type="text/event-stream")