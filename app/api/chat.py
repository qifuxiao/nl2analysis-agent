'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:15:46
FilePath: /alexqi/develop/nl2analysis-agent/app/api/chat.py
'''
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.agent.graph import app_graph

router = APIRouter()

class ChatReq(BaseModel):
    session_id: str
    query: str

def get_current_user():
    return "user_001"  # TODO: 接 JWT / API Key

@router.post("/v1/agent/chat")
def chat(req: ChatReq, user_id: str = Depends(get_current_user)):
    state = {
        "user_id": user_id,
        "session_id": req.session_id,
        "query": req.query,
        "history": []
    }
    return app_graph.invoke(state)
