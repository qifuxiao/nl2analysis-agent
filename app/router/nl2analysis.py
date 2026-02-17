'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:09:17
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:31:46
FilePath: /nl2analysis-agent/app/router/nl2analysis.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/router/nl2analysis.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio

from app.graph.graph import app_graph
from app.llm.service import LLMService
from app.utils.sse import sse_pack
from app.schemas.query import QueryReq

router = APIRouter()


@router.post("/nl2analysis/stream")
async def nl2analysis_stream(req: QueryReq):

    async def event_generator():

        inputs = {
            "query": req.query,
            "user_id": req.user_id,
            "session_id": req.session_id,
            "history": []
        }

        llm_service = LLMService(tenant_id=req.tenant_id)

        async for event in app_graph.astream(inputs, stream_mode="updates"):

            for node_name, output in event.items():

                # ===============================
                # 这里开始接管 analysis streaming
                # ===============================
                if node_name == "analysis":

                    prompt = output.get("analysis_prompt")

                    if not prompt:
                        yield sse_pack({
                            "node": "analysis_error",
                            "msg": "analysis_prompt missing"
                        })
                        continue

                    # 👇👇👇 就写在这里
                    yield sse_pack({"node": "analysis_start"})

                    async for token in llm_service.astream(prompt):

                        yield sse_pack({
                            "node": "analysis_token",
                            "content": token
                        })

                    yield sse_pack({"node": "analysis_end"})

                # 其他 graph 节点直接透传
                else:
                    yield sse_pack({
                        "node": node_name,
                        "output": output
                    })

                await asyncio.sleep(0)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        }
    )

