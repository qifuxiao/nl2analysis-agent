'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:28:32
LastEditors: Please set LastEditors
LastEditTime: 2026-02-25 07:44:52
FilePath: /nl2analysis-agent/app/schemas/query.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/schemas/query.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class QueryReq(BaseModel):
    """
    NL2Analysis 请求模型
    """

    query: str = Field(
        ...,
        description="用户自然语言问题"
    )

    user_id: str = Field(
        ...,
        description="用户ID（可用于多租户模型选择）"
    )

    session_id: str = Field(
        ...,
        description="会话ID（用于会话级记忆或日志追踪）"
    )
    tenant_id: Optional[str] = Field(
        "default",
        description="租户ID（用于区分不同的LLM提供商配置，默认值为 'default'）"
    )
    
