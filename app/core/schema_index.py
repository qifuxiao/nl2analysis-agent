'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:13:45
FilePath: /nl2analysis-agent/app/core/schema_index.py
'''
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.schema_loader import load_all_tables_schema
from app.core.config import settings

class SchemaIndex:
    def __init__(self):
        schema = load_all_tables_schema()
        embedding_model = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.EMBEDDING_API_KEY or "dummy-key",
            openai_api_base=settings.EMBEDDING_BASE_URL.rstrip("/") if hasattr(settings, "EMBEDDING_BASE_URL") and settings.EMBEDDING_BASE_URL else None,
            # 建议也加上超时限制，防止卡死
            request_timeout=10 ,
            embedding_ctx_length=512, # 根据 bge-m3 限制设置
            check_embedding_ctx_length=False,
            # 如果网关极其严格，尝试添加这个参数来关闭额外的 OpenAI 默认行为
            default_headers={"Accept": "application/json"},
            # 某些网关不支持额外的参数，可以通过 extra_body 强制置空（如果 SDK 版本支持）
        )
        self.docs = [
            Document(page_content=f"{t}: {', '.join(cols)}", metadata={"table": t})
            for t, cols in schema.items()
        ]
        self.index = FAISS.from_documents(self.docs, embedding_model)

    def retrieve(self, query: str, k: int = 5) -> list[str]:
        docs = self.index.similarity_search(query, k=k)
        return [d.page_content for d in docs]

schema_index = SchemaIndex()
