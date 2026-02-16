from app.llm.client import get_llm
from app.tools.db_tool import run_sql
from app.analysis.analyzer import analyze_data
from app.core.schema_index import schema_index
from app.memory.backend import load_session, save_session
from app.analysis.chart import generate_chart_html
from app.memory.models import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
import re

llm = get_llm()

def extract_pure_sql(text: str) -> str:
    text = re.sub(r"```sql\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\n?", "", text)
    if ";" in text:
        text = text.split(";")[0] + ";"
    return text.strip()

async def pre_memory_node(state):
    # 异步包装同步 IO
    loop = asyncio.get_event_loop()
    memory = await loop.run_in_executor(None, load_session, state["user_id"], state["session_id"])
    return {"history": [m.__dict__ for m in memory.messages]}

async def nl2sql_node(state):
    tables = schema_index.retrieve(state["query"], k=5)
    tables_schema = "\n".join(tables)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的 SQL 生成专家。请根据表结构生成 SELECT 语句。严禁 Markdown 标签。\n\n【表结构】\n{schema}"),
        ("human", "{question}")
    ])

    sql_chain = prompt | llm | StrOutputParser()
    # 使用 ainvoke 异步调用
    raw_sql = await sql_chain.ainvoke({
        "schema": tables_schema,
        "question": state["query"]
    })

    clean_sql = extract_pure_sql(raw_sql)
    print(f"--- Generated SQL ---\n{clean_sql}\n---------------------")
    return {"sql": clean_sql}

async def db_query_node(state):
    try:
        # 使用 run_in_executor 避免 SQL 查询阻塞事件循环
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, run_sql, state["sql"])
        if not data:
            return {"error": "查询结果为空", "raw_data": []}
        return {"raw_data": data}
    except Exception as e:
        return {"error": str(e)}

async def analysis_node(state):
    # analyze_data 已经是异步的了
    result = await analyze_data(state["raw_data"], state["query"])
    return {"analysis": result}

async def clarification_node(state):
    prompt = f"用户问题：{state['query']}\n错误信息：{state.get('error')}\n请生成一句澄清问题。"
    # 使用 ainvoke
    res = await llm.ainvoke(prompt)
    question = res.content.strip()
    return {"analysis": {"need_clarification": True, "question": question}}

async def post_memory_node(state):
    loop = asyncio.get_event_loop()
    def _save():
        memory = load_session(state["user_id"], state["session_id"])
        memory.messages.append(ChatMessage(role="user", content=state["query"]))
        memory.messages.append(ChatMessage(role="assistant", content=state["analysis"].get("summary", "")))
        save_session(memory)
    await loop.run_in_executor(None, _save)
    return {}
async def chart_node(state):
    """
    异步图表生成节点
    """
    # 检查是否有数据可供绘图
    if not state.get("raw_data"):
        return {"analysis": state.get("analysis", {})}

    # 将同步的图表生成逻辑放入线程池执行，防止阻塞 SSE 流
    loop = asyncio.get_event_loop()
    html = await loop.run_in_executor(
        None, 
        generate_chart_html, 
        state["raw_data"], 
        state["query"]
    )
    
    # 更新状态中的 analysis 字典
    current_analysis = state.get("analysis", {})
    current_analysis["chart_html"] = html
    
    return {"analysis": current_analysis}