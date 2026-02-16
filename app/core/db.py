'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:12:48
FilePath: /alexqi/develop/nl2analysis-agent/app/core/db.py
'''
from sqlalchemy import create_engine
from app.core.config import settings

def build_db_url():
    if settings.DB_TYPE == "postgres":
        return f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    elif settings.DB_TYPE == "doris":
        return f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    elif settings.DB_TYPE == "clickhouse":
        return f"clickhouse+http://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    else:
        raise ValueError("Unsupported DB_TYPE")

engine = create_engine(build_db_url(), pool_pre_ping=True)
