# app/graph/nodes/alert_rule_node.py

import time
import base64
import os
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# 导入你的 GraphState，根据实际路径调整
from app.graph.state import GraphState

# ========== 配置常量（建议移至环境变量）==========
SSO_APP_ID = os.getenv("SSO_APP_ID", "sso20251001")
SSO_SECRET_KEY = os.getenv("SSO_SECRET_KEY", "C0HJU0La2o6qtgJ4ZvLk")
API_DOMAIN = os.getenv("API_DOMAIN", "https://192.168.101.54:8888")


def send_post_request(url: str, payload: dict, headers: Optional[Dict] = None) -> Optional[requests.Response]:
    """发送POST请求的公共方法"""
    headers = headers or {"Content-Type": "application/json"}
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=50,
            verify=False  # ⚠️ 生产环境请配置有效SSL证书
        )
        print('***************')
        print(response.text)
        print('***************')
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求错误 [{url}]: {e}")
        return None


def generate_signature() -> str:
    """生成签名密钥"""
    timestamp = int(time.time())
    encode_str = f"{SSO_APP_ID}{SSO_SECRET_KEY[:3]}{SSO_SECRET_KEY[-3:]}{timestamp}"
    return base64.b64encode(encode_str.encode()).decode()


def data_group(out: Dict) -> Any:
    """对查询结果进行分组聚合处理"""
    try:
        data = out.get('data', {}).get('dataList', [])
        if not data:
            return out
        
        df = pd.DataFrame(data)
        if len(df) > 0:
            df = df.groupby([
                'gid', 'fix_source_type', 'event_threat_type', 
                'event_mitre_att_ck_technique', 'event_source_ip', 
                'event_signature', 'event_destination_ip', 
                'event_mitre_att_ck_tactic', 'event_threat_name', 'event_hostname'
            ]).agg(
                threat_count=('event_date_time', 'count'),
                time_range=('event_date_time', lambda x: sorted(list(set(x.tolist()))))
            ).reset_index()
            return df.to_dict("records")
        return out
    except Exception as e:
        print(f"[data_group] 处理异常: {e}")
        return out


def _normalize_time(time_str: Optional[str], is_end: bool = False) -> str:
    """统一时间格式：开始时间→00:00:00，结束时间→23:59:59"""
    if not time_str:
        now = datetime.now()
        return now.strftime('%Y-%m-%d 00:00:00') if not is_end else now.strftime('%Y-%m-%d %H:%M:%S')
    
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime('%Y-%m-%d 23:59:59' if is_end else '%Y-%m-%d 00:00:00')
        except ValueError:
            continue
    # 解析失败时返回默认值
    return _normalize_time(None, is_end)


def _query_alert_rule_api(gid: Optional[str], start_time: str, end_time: str) -> Any:
    """执行实际的API查询逻辑（纯函数，便于测试）"""
    table_name = "alarm_result"
    sign_key = generate_signature()
    
    print(f"\n[API] 查询告警规则 | 表:{table_name} GID:{gid} 时间:{start_time} ~ {end_time}")
    
    url = f"{API_DOMAIN}/admin/sdk/alert-rule-result"
    payload = {
        "sdkReq": {"appId": SSO_APP_ID, "signKey": sign_key},
        "gid": gid or "",
        "tableName": table_name,
        "createTime": [start_time, end_time],
        "pageNo": 1,
        "pageSize": 500
    }

    response = send_post_request(url, payload)
    if response:
        out = response.json()
        return data_group(out)
    else:
        return {"error": "告警查询失败", "query_params": {"gid": gid, "start_time": start_time, "end_time": end_time}}


# ============ 🔑 LangGraph 节点入口函数 ============
def alert_rule_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph 节点：查询告警规则结果
    
    📥 从 state 读取:
    - gid / alert_gid: 客户唯一标识 (可选)
    - start_time / alert_start_time: 开始时间 (可选)
    - end_time / alert_end_time: 结束时间 (可选)
    
    📤 返回更新到 state:
    - alert_rule_data: 查询结果
    - alert_rule_query_params: 实际查询参数(便于调试)
    - alert_rule_status: "success" | "failed"
    """
    # 1️⃣ 从 state 提取参数（支持多种键名兼容）
    gid = state.get("gid") or state.get("alert_gid")
    start_time = state.get("start_time") or state.get("alert_start_time")
    end_time = state.get("end_time") or state.get("alert_end_time")
    
    # 2️⃣ 参数预处理
    start_norm = _normalize_time(start_time, is_end=False)
    end_norm = _normalize_time(end_time, is_end=True)
    
    print(f"[alert_rule_node] 执行: gid={gid}, {start_norm} → {end_norm}")
    
    try:
        # 3️⃣ 执行查询
        result = _query_alert_rule_api(gid, start_norm, end_norm)
        
        # 4️⃣ 返回 state 更新内容
        return {
            "alert_rule_data": result,
            "alert_rule_query_params": {
                "gid": gid, "start_time": start_norm, "end_time": end_norm
            },
            "alert_rule_status": "success"
        }
        
    except Exception as e:
        print(f"[alert_rule_node] 执行异常: {e}")
        return {
            "alert_rule_data": {"error": str(e)},
            "alert_rule_status": "failed"
        }


# ============ 🔁 兼容原有调用方式（非Graph场景） ============
def alert_rule_request(
    gid: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> Any:
    """兼容函数：直接调用查询，不依赖 state"""
    start_norm = _normalize_time(start_time, is_end=False)
    end_norm = _normalize_time(end_time, is_end=True)
    return _query_alert_rule_api(gid, start_norm, end_norm)


class AlertRuleInput(BaseModel):
    """参数校验模型（可用于前置节点输出校验）"""
    gid: Optional[str] = Field(default=None, description="客户gid，不指定则查询全部")
    start_time: Optional[str] = Field(default=None, description="开始时间，默认当天0点")
    end_time: Optional[str] = Field(default=None, description="结束时间，默认当前时间")