'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:19:59
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:33:56
FilePath: /nl2analysis-agent/app/graph/nodes/nl2sql_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.llm.client import get_llm
from app.core.schema_index import schema_index
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.utils.db_tool import extract_pure_sql
from app.memory.models import ChatMessage
from app.core.logger import logger
llm = get_llm()
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
#     state.setdefault("history", [])
#     logger.info(f"{type(clean_sql)=}")
#     state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=clean_sql,
#     additional_kwargs=getattr(clean_sql, "additional_kwargs", {})
# ))
    return {"sql": clean_sql}