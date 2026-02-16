'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:34:35
FilePath: /alexqi/develop/nl2analysis-agent/app/tools/db_tool.py
'''
# app/tools/db_tool.py
from sqlalchemy import create_engine, text
from app.core.config import settings
import math
from fastapi.encoders import jsonable_encoder
# 1. 动态构建数据库连接字符串
# 格式: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# 2. 创建全局 Engine 实例
# 建议加上 pool_pre_ping=True 自动检测并处理断开的连接
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def run_sql(sql: str) -> list[dict]:
    """
    执行 SQL 查询并返回结果列表
    """
    with engine.connect() as conn:
        # 使用 mappings() 将每一行转换为字典格式
        result = conn.execute(text(sql))
        # 结果处理：将 RowMapping 对象转为标准的 dict 列表
        return [dict(row) for row in result.mappings()]


def clean_nans(obj):
    """递归将 NaN 和 Inf 转换为 None"""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(x) for x in obj]
    return obj

# 如果你想测试是否连通，可以增加一个简单的测试逻辑
if __name__ == "__main__":
    try:
        test_res = run_sql("SELECT 1 as test")
        print("数据库连接测试成功:", test_res)
    except Exception as e:
        print("数据库连接失败:", str(e))