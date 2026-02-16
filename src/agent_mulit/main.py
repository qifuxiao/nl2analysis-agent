'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-13 09:28:42
FilePath: /alexqi/develop/Agent/src/agent_mulit/main.py
'''
import os 
api_key = os.getenv("OPENAI_API_KEY")

from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="deepseek-v3-0324",
    
    api_key=api_key,
    base_url="http://10.231.4.6:30109/CIDC-ECSO-109/inference-proxy/792563b5-943d-434e-95f2-b9c94d5719c5/aiops-1421977318167711744/deepseek-v3-0324/service/8080/v1",
)

a=model.invoke("你是谁？能帮我解决什么问题？")
print(f"模型回答：{a}")

from langchain.agents import create_agent
from langchain_community.tools import tool

agent = create_agent(
    model=model,
    tools=[],
    system_prompt="你是一个专业助手"
)

# 背后自动跑在 LangGraph 运行时上
result = agent.invoke({"messages": [{"role": "user", "content": "你好"}]})
print(f"Agent回答：{result}")