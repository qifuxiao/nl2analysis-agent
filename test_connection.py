'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 07:05:28
FilePath: /nl2analysis-agent/test_connection.py
'''
# test_connection.py
from app.core.db import engine
from app.llm.client import get_llm

try:
    print("正在连接数据库...")
    with engine.connect() as conn:
        print("✅ 数据库连接成功")
    
    print("正在连接LLM...")
    llm = get_llm()
    res = llm.invoke("ping")
    print(f"✅ LLM 响应成功: {res.content}")
except Exception as e:
    print(f"❌ 测试失败: {e}")