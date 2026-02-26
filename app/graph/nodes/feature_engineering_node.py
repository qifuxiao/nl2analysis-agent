# app/graph/nodes/feature_engineering_node.py

from typing import Dict, Any
import pandas as pd
from app.core.logger import logger
from app.graph.state import GraphState


def _build_attack_features(df: pd.DataFrame) -> Dict[str, Any]:
    """
    构建攻击统计特征（不涉及风险判断）
    """

    if df.empty:
        return {
            "total_events": 0,
            "unique_source_ip": 0,
            "unique_destination_ip": 0,
            "unique_devices": 0,
            "top_source_ip": {},
            "top_destination_ip": {},
            "threat_type_distribution": {},
            "mitre_tactic_distribution": {},
            "is_single_source_attack": False,
            "is_multi_target_attack": False,
        }

    total_events = int(df["threat_count"].sum())

    source_stats = (
        df.groupby("event_source_ip")["threat_count"]
        .sum()
        .sort_values(ascending=False)
    )

    destination_stats = (
        df.groupby("event_destination_ip")["threat_count"]
        .sum()
        .sort_values(ascending=False)
    )

    threat_type_distribution = (
        df.groupby("event_threat_type")["threat_count"]
        .sum()
        .to_dict()
    )

    mitre_tactic_distribution = (
        df.groupby("event_mitre_att_ck_tactic")["threat_count"]
        .sum()
        .to_dict()
    )

    return {
        "total_events": total_events,
        "unique_source_ip": int(df["event_source_ip"].nunique()),
        "unique_destination_ip": int(df["event_destination_ip"].nunique()),
        "unique_devices": int(df["event_hostname"].nunique()),
        "top_source_ip": source_stats.head(5).to_dict(),
        "top_destination_ip": destination_stats.head(5).to_dict(),
        "threat_type_distribution": threat_type_distribution,
        "mitre_tactic_distribution": mitre_tactic_distribution,
        "is_single_source_attack": (
            source_stats.iloc[0] / total_events > 0.6
            if total_events > 0 else False
        ),
        "is_multi_target_attack": len(destination_stats) > 3,
    }


def feature_engineering_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node
    输入：
        state["alert_rule_data"]

    输出：
        state["attack_features"]
        state["feature_status"]
    """

    logger.info("feature_engineering_node 开始执行")

    raw_data = state.get("alert_rule_data")

    if not raw_data or not isinstance(raw_data, list):
        logger.warning("alert_rule_data 为空或格式异常")
        return {
            "attack_features": {},
            "feature_status": "failed"
        }

    try:
        df = pd.DataFrame(raw_data)

        if "threat_count" not in df.columns:
            logger.error("缺少 threat_count 字段")
            return {
                "attack_features": {},
                "feature_status": "failed"
            }

        features = _build_attack_features(df)

        logger.info(f"feature_engineering_node 完成 | total_events={features['total_events']}")

        return {
            "attack_features": features,
            "feature_status": "success"
        }

    except Exception as e:
        logger.exception(f"feature_engineering_node 异常: {e}")
        return {
            "attack_features": {},
            "feature_status": "failed"
        }