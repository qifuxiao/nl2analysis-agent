'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:13:04
FilePath: /alexqi/develop/nl2analysis-agent/app/core/schema_loader.py
'''
from sqlalchemy import inspect
from app.core.db import engine

def load_all_tables_schema() -> dict:
    inspector = inspect(engine)
    schema = {}
    for table in inspector.get_table_names():
        # 排除掉 alembic 自带的版本控制表，减少干扰
        if table == "alembic_version":
            continue
            
        cols = inspector.get_columns(table)
        formatted_cols = []
        
        for c in cols:
            name = c['name']
            type_str = str(c['type'])
            comment = c.get('comment')  # 关键点：获取注释
            
            # 拼接格式：字段名(类型) - 注释内容
            col_desc = f"{name}({type_str})"
            if comment:
                col_desc += f": {comment}"
            
            formatted_cols.append(col_desc)
            
        schema[table] = formatted_cols
    return schema
