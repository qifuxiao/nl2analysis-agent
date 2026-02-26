# app/graph/nodes/risk_scoring_node.py

from typing import Dict, Any
from app.core.logger import logger
from app.graph.state import GraphState


# MITRE Tactic 权重（企业可调整）
MITRE_TACTIC_WEIGHT = {
    "Credential Access": 30,
    "Lateral Movement": 40,
    "Persistence": 35,
    "Privilege Escalation": 45,
    "Execution": 30,
    "Discovery": 20,
}


def _calculate_risk_score(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    确定性风险评分引擎
    """

    score = 0

    total_events = features.get("total_events", 0)
    unique_source_ip = features.get("unique_source_ip", 0)
    is_single_source_attack = features.get("is_single_source_attack", False)
    is_multi_target_attack = features.get("is_multi_target_attack", False)
    mitre_distribution = features.get("mitre_tactic_distribution", {})

    # 1️⃣ 事件数量权重
    if total_events > 200:
        score += 30
    elif total_events > 50:
        score += 20
    elif total_events > 10:
        score += 10

    # 2️⃣ 攻击集中度
    if is_single_source_attack:
        score += 20

    # 3️⃣ 横向扩散
    if is_multi_target_attack:
        score += 20

    # 4️⃣ 多源IP攻击
    if unique_source_ip > 5:
        score += 20

    # 5️⃣ MITRE 战术权重
    for tactic, count in mitre_distribution.items():
        weight = MITRE_TACTIC_WEIGHT.get(tactic, 10)
        score += min(weight, 40)  # 防止极端累加

    # 6️⃣ 风险等级划分
    if score >= 80:
        level = "高"
    elif score >= 40:
        level = "中"
    else:
        level = "低"

    return {
        "risk_score": score,
        "risk_level": level
    }


def risk_scoring_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node

    输入：
        state["attack_features"]

    输出：
        state["risk_assessment"]
        state["risk_status"]
    """

    logger.info("risk_scoring_node 开始执行")

    features = state.get("attack_features")

    if not features:
        logger.warning("attack_features 为空")
        return {
            "risk_assessment": {},
            "risk_status": "failed"
        }

    try:
        risk_result = _calculate_risk_score(features)

        logger.info(
            f"risk_scoring_node 完成 | score={risk_result['risk_score']} "
            f"level={risk_result['risk_level']}"
        )

        return {
            "risk_assessment": risk_result,
            "risk_status": "success"
        }

    except Exception as e:
        logger.exception(f"risk_scoring_node 异常: {e}")
        return {
            "risk_assessment": {},
            "risk_status": "failed"
        }