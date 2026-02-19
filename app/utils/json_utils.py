'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:29:44
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:30:43
FilePath: /nl2analysis-agent/app/utils/json_utils.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/utils/json_utils.py

import json
import datetime
import decimal
import numpy as np
from typing import Any




def _default_serializer(obj: Any):
    """
    统一处理不可序列化对象
    """

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    if isinstance(obj, decimal.Decimal):
        return float(obj)

    if isinstance(obj, (np.integer,)):
        return int(obj)

    if isinstance(obj, (np.floating,)):
        return float(obj)

    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()

    return str(obj)


def safe_json_dumps(data: Any) -> str:
    """
    企业级安全 JSON 序列化

    - 兼容 numpy
    - 兼容 datetime
    - 支持中文
    - 避免 NaN 报错
    """

    return json.dumps(
        data,
        default=_default_serializer,
        ensure_ascii=False,
        allow_nan=False
    )
