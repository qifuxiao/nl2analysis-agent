'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:10:45
FilePath: /alexqi/develop/nl2analysis-agent/app/main.py
'''
# app/main.py
from fastapi import FastAPI
from app.router.nl2analysis import router

app = FastAPI(title="NL2Analysis Agent")
app.include_router(router)
