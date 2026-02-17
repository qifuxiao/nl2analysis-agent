'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:28:32
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:28:39
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
        default="default",
        description="租户ID，用于选择不同LLM配置"
    )

    debug: Optional[bool] = Field(
        default=False,
        description="是否开启调试模式"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="扩展字段，可用于透传前端参数"
    )
