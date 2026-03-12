# Multi-Agent System based on LangGraph

## Project Overview

A powerful multi-agent orchestration system built on LangChain + LangGraph, featuring automatic intent detection and routing to specialized agent workflows.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Query                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Intent Router Agent                          │
│  - Analyzes user intent                                         │
│  - Routes to appropriate agent                                 │
│  - Falls back to General Chat if no agent matched              │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌──────────┬──────────┬──────────┬──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼          │
┌─────────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
│  NL2SQL     │ │ Analysis │ │  File  │ │  Web    │ │ General │
│  Agent      │ │  Agent   │ │ Agent  │ │ Search  │ │  Chat   │
└─────────────┘ └──────────┘ └────────┘ └─────────┘ └─────────┘
        │          │          │          │          │
        └──────────┴──────────┴──────────┴──────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │   Memory    │
                         │  (Redis)    │
                         └─────────────┘
```

### Supported Agents

| Agent | Intent Keywords | Capabilities |
|-------|-----------------|--------------|
| NL2SQL | "查询", "多少", "统计", "SELECT", "数据库" | Natural language to SQL, DB query |
| Analysis | "分析", "图表", "趋势", "对比" | Data analysis, visualization |
| File | "读取", "写入", "上传", "下载", "文件" | File operations |
| Web Search | "搜索", "查找", "最新", "新闻" | Real-time web search |
| General Chat | (fallback) | General knowledge via LLM |

## Quick Start

### API Service

```bash
# Start API server
uvicorn app.api.main:app --reload --port 8000

# Test endpoint
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "session_id": "sess001",
    "message": "查询上个月的销售额"
  }'
```

### SDK Usage

```python
from agent import AgentClient

# Initialize client
client = AgentClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Simple chat
response = client.chat(
    message="帮我分析本月销售趋势",
    user_id="user123",
    session_id="sess001"
)

print(response.content)

# Streaming chat
for chunk in client.stream_chat(
    message="查询用户数量",
    user_id="user123",
    session_id="sess001"
):
    print(chunk.content, end="")
```

## Configuration

Set environment variables:

```bash
# LLM Configuration
LLM_PROVIDER=openai  # or: deepseek, vllm, anthropic
OPENAI_API_KEY=sk-xxx
BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small

# Memory (Redis)
REDIS_HOST=localhost
REDIS_PORT=6379

# Database (for NL2SQL)
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=demo
DB_USER=demo
DB_PASSWORD=xxx

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secret-key
```

## Development

### Project Structure

```
agent/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── agents/           # Agent definitions
│   │   ├── router.py     # Intent router
│   │   ├── nl2sql.py     # NL2SQL agent
│   │   ├── analysis.py  # Analysis agent
│   │   ├── file.py       # File agent
│   │   ├── search.py    # Web search agent
│   │   └── general.py    # General chat agent
│   ├── graph/            # LangGraph workflow
│   ├── tools/            # Tool definitions
│   ├── memory/           # Conversation memory
│   ├── llm/              # LLM providers
│   └── utils/            # Utilities
├── sdk/                  # Python SDK
├── tests/                # Tests
└── pyproject.toml
```

### Add Custom Agent

1. Create agent in `app/agents/`
2. Define tools in `app/tools/`
3. Register in router's intent patterns
4. Add to LangGraph workflow

## License

MIT
