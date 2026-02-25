'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 13:41:07
LastEditors: Please set LastEditors
LastEditTime: 2026-02-25 09:16:28
FilePath: /nl2analysis-agent/app/graph/nodes/time_prompt.py
Description: 时间参数提取节点：从 query 中解析 gid/start_time/end_time
'''
import json
import re
from app.core.logger import logger
from app.llm.service import LLMService  # 🔥 引入 LLM 服务

async def time_prompt_node(state):
    """
    时间参数提取节点：调用大模型从用户问题中提取 gid/start_time/end_time
    返回: dict with keys: gid, start_time, end_time, time_prompt
    """
    logger.info(f"🔹 time_prompt_node entered | query: {state.get('query', 'MISSING')}")
    
    try:
        # 🔥 1. 安全获取输入
        query = state.get("query", "").strip()
        tenant_id = state.get("tenant_id", "default")  # 🔥 从 state 获取 tenant_id
        user_id = state.get("user_id", "unknown")
        
        if not query:
            logger.warning("⚠️ query is empty, returning default values")
            return {
                "gid": None,
                "start_time": None,
                "end_time": None,
                "time_prompt": "用户未提供查询内容"
            }

        

        # 🔥 3. 构造提取 prompt（要求 JSON 输出）
        extract_prompt = (
            "你是一个参数提取专家。请从用户问题中精确提取以下 3 个字段，输出纯 JSON 格式：\n"
            "{\n"
            '  "gid": "字符串或 null",\n'
            '  "start_time": "YYYY-MM-DD 格式或 null",\n'
            '  "end_time": "YYYY-MM-DD 格式或 null"\n'
            "}\n"
            "【规则】\n"
            "1. 如果字段未提及，值设为 null（不是字符串 'null'）\n"
            "2. 时间格式统一为 YYYY-MM-DD，如 '2026-01-01'\n"
            "3. 严禁输出 Markdown、解释文字或其他内容，只输出 JSON\n"
            "4. gid 通常是数字字符串，如 '4715'\n\n"
            f"【用户问题】{query}\n"
            
        )

        # 🔥 4. 调用大模型提取（同步 invoke，避免流式复杂性）
        llm_service = LLMService(tenant_id=tenant_id)
        logger.info(f"🤖 Calling LLM for parameter extraction | tenant_id: {tenant_id}")
        
        llm_response = await llm_service.ainvoke(extract_prompt)  # 🔥 使用 async invoke
        logger.debug(f"📝 LLM raw response: {llm_response[:200]}...")

        # 🔥 5. 解析 JSON 结果（兼容多种格式）
        extracted = _parse_llm_json(llm_response)
        logger.info(f"📦 Parsed extraction result: {extracted}")

        # 🔥 6. 提取三个目标字段（带默认值 None）
        gid = extracted.get("gid")
        start_time = extracted.get("start_time")
        end_time = extracted.get("end_time")

        # 🔥 7. 可选：简单校验时间格式（非强制）
        if start_time and not _is_valid_date(start_time):
            logger.warning(f"⚠️ Invalid start_time format: {start_time}")
        if end_time and not _is_valid_date(end_time):
            logger.warning(f"⚠️ Invalid end_time format: {end_time}")

        # 🔥 8. 构造 time_prompt 供下游使用（可选）
        time_prompt = (
            f"提取参数 → gid: {gid}, start_time: {start_time}, end_time: {end_time}\n"
            f"原始问题: {query}"
        )

        logger.info(
            f"✅ time_prompt_node success | "
            f"gid={gid}, start_time={start_time}, end_time={end_time}"
        )

        # ✅ 返回 state 更新（关键：必须是 dict）
        return {
            "gid": gid,
            "start_time": start_time,
            "end_time": end_time,
            "time_prompt": time_prompt,
            "extraction_raw": extracted  # 🔥 调试用，可保留原始解析结果
        }

    except Exception as e:
        logger.exception(f"❌ time_prompt_node failed: {e}")
        # ✅ 异常时返回默认值，避免中断图执行
        return {
            "gid": None,
            "start_time": None,
            "end_time": None,
            "time_prompt": f"参数提取异常: {str(e)}",
            "error": str(e)
        }


# 🔧 辅助函数：解析 LLM 返回的 JSON（增强鲁棒性）
def _parse_llm_json(text: str) -> dict:
    """
    从 LLM 响应中提取 JSON，兼容：
    - 纯 JSON: {"gid": "4715"}
    - Markdown 包裹: ```json {...} ```
    - 带解释文字: "结果是 {...}"
    """
    if not text:
        return {}
    
    # 1. 尝试直接解析
    try:
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    
    # 2. 尝试提取 ```json ... ``` 包裹的内容
    match = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    # 3. 尝试提取第一个 { ... } 块
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0).strip())
        except json.JSONDecodeError:
            pass
    
    # 4. 降级：尝试用正则提取单个字段（兜底）
    result = {}
    gid_match = re.search(r'"?gid"?\s*[:=]\s*["\']?(\w+)["\']?', text, re.I)
    if gid_match:
        result["gid"] = gid_match.group(1)
    
    for field in ["start_time", "end_time"]:
        # 匹配 YYYY-MM-DD 格式
        date_match = re.search(rf'"{field}"\s*[:=]\s*["\']?(\d{{4}}-\d{{2}}-\d{{2}})["\']?', text)
        if date_match:
            result[field] = date_match.group(1)
    
    logger.warning(f"⚠️ JSON parse fallback, result: {result}")
    return result


# 🔧 辅助函数：校验日期格式
def _is_valid_date(date_str: str) -> bool:
    """检查是否为 YYYY-MM-DD 格式"""
    if not date_str:
        return False
    try:
        from datetime import datetime
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False