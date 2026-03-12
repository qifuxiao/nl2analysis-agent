# LangGraph Chat Service

基于 LangGraph 的多Agent对话服务，支持多种对话模式。

## 功能特性

- 🌐 **流式对话** - 支持 SSE 流式输出
- 🤖 **多模型支持** - 兼容 OpenAI 协议的所有模型
- 💾 **知识库** - RAG 知识库问答
- 📊 **Text2SQL** - 自然语言转 SQL
- 🔍 **搜索引擎** -联网搜索问答
- 📁 **文件对话** - 上传文件进行分析
- 🎯 **Agent模式** - Agent 智能体

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API Key
```

### 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 接口

### 对话接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /chat/chat | 普通对话 |
| POST | /chat/knowledge_base_chat | 知识库对话 |
| POST | /chat/search_engine_chat | 搜索引擎对话 |
| POST | /chat/agent_chat | Agent对话 |
| POST | /chat/file_chat | 文件对话 |
| POST | /generate_sql | Text2SQL |

### 知识库接口

| 方法 | 路径 |说明 |
|------|------|------|
| POST | /knowledge_base/create | 创建知识库 |
| GET | /knowledge_base/list | 列出知识库 |
| POST | /knowledge_base/upload | 上传文档 |
| GET | /knowledge_base/list_files | 列出文件 |
| POST | /knowledge_base/delete | 删除文档 |
| GET | /knowledge_base/download | 下载文档 |

### 模型管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /llm_model/list_config | 获取配置模型 |
| GET | /llm_model/list_running | 获取运行模型 |
| POST | /llm_model/change | 切换模型 |

## 请求示例

### 普通对话

```bash
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己",
    "model": "gpt-4o-mini"
  }'
```

### 流式对话

```bash
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "写一首关于春天的诗",
    "stream": true
  }'
```

### 知识库对话

```bash
curl -X POST http://localhost:8000/chat/knowledge_base_chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "关于我们公司的产品",
    "knowledge_base_name": "company_docs"
  }'
```

### Text2SQL

```bash
curl -X POST http://localhost:8000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "message": "查询上个月销售额最高的10个客户",
    "metadata": "select name from customers"
  }'
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| OPENAI_API_KEY | OpenAI API Key | - |
| OPENAI_BASE_URL | API 基础地址 | https://api.openai.com/v1 |
| DEFAULT_MODEL | 默认模型 | gpt-4o-mini |
| TEMPERATURE | 采样温度 | 0.7 |
| MAX_TOKENS | 最大token数 | 4096 |
| EMBEDDING_MODEL | Embedding模型 | text-embedding-3-small |
| CHROMA_PERSIST_DIR | 向量库存储目录 | ./data/chroma |

## 项目结构

```
chat_service/
├── app/
│   ├── api/              # API 路由
│   │   ├── chat.py       # 对话接口
│   │   ├── knowledge.py  # 知识库接口
│   │   └── llm.py        # 模型管理
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   └── llm.py       # LLM 客户端
│   ├── services/         # 业务逻辑
│   │   ├── chat_service.py
│   │   ├── knowledge_service.py
│   │   ├── sql_service.py
│   │   └── search_service.py
│   ├── tools/           # 工具函数
│   └── main.py          # 应用入口
├── tests/               # 测试
├── requirements.txt     # 依赖
└── .env                # 环境变量
```
