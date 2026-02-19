'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:09:17
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:49:54
FilePath: /nl2analysis-agent/app/router/nl2analysis.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/router/nl2analysis.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from app.memory.backend import load_session
from app.graph.nodes import post_memory_node

from app.graph.graph import app_graph
from app.llm.service import LLMService
from app.utils.sse import sse_pack
from app.schemas.query import QueryReq
from app.core.logger import logger
router = APIRouter()


@router.post("/nl2analysis/stream")
async def nl2analysis_stream(req: QueryReq):

    async def event_generator():
        # ⚡ 读取历史
        session_mem = load_session(req.user_id, req.session_id)
        from dataclasses import asdict

        history = [asdict(m) for m in session_mem.messages]

        inputs = {
            "query": req.query,
            "user_id": req.user_id,
            "session_id": req.session_id,
            "history": history
        }

        llm_service = LLMService(tenant_id=req.tenant_id)

        async for event in app_graph.astream(inputs, stream_mode="updates"):

            for node_name, output in event.items():

                try:
                    # ===============================
                    # 🔥 接管 analysis_prompt 流式输出
                    # ===============================
                    if node_name == "analysis_prompt":

                        prompt = output.get("analysis_prompt")

                        if not prompt:
                            logger.error(
                                f"[Session {req.session_id}] analysis_prompt missing. Event: {output}"
                            )
                            yield sse_pack({
                                "node": "analysis_error",
                                "msg": "analysis_prompt missing"
                            })
                            continue

                        yield sse_pack({"node": "analysis_start"})

                        full_text = ""

                        # 🔥 真正流式
                        async for token in llm_service.astream(prompt):

                            if token:
                                full_text += token

                                yield sse_pack({
                                    "node": "analysis_token",
                                    "content": token
                                })

                        # 🔥 流式结束后写回 history
                        inputs.setdefault("history", [])
                        inputs["history"].append({
                            "type": "AIMessage",
                            "content": full_text,
                            "additional_kwargs": {}
                        })

                        yield sse_pack({"node": "analysis_end"})

                        # ===============================
                        # 🔥 在这里保存 memory
                        # ===============================
                        try:
                            await post_memory_node({
                                "user_id": req.user_id,
                                "session_id": req.session_id,
                                "history": inputs["history"]
                            })
                        except Exception:
                            logger.exception(f"[Session {req.session_id}] memory save failed")
                    # ===============================
                    # 其他节点透传
                    # ===============================
                    else:
                        yield sse_pack({
                            "node": node_name,
                            "output": output
                        })

                    await asyncio.sleep(0)

                except Exception:
                    logger.exception(
                        f"[Session {req.session_id}] Error processing node {node_name}"
                    )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        }
    )
