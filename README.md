<!--
 * @Author: qifuxiao 867225266@qq.com
 * @Date: 2026-02-13 09:16:26
 * @FilePath: /nl2analysis-agent/README.md
-->
# LangGraph
# NL2Analysis Agent Platform

企业级自然语言 BI Agent 后端服务

## 功能
- 多用户隔离
- 会话级 Memory
- NL → SQL → 数据分析 → 可视化
- 多数据库支持
- Docker 一键部署

## 启动
cp .env.example .env
docker compose up -d --build

## 接口
POST /v1/agent/chat

Body:
{
  "session_id": "xxx",
  "query": "最近7天订单金额趋势"
}


# 开发环境运行命令
`poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000`

# 测试命令：
`curl -N -X POST http://localhost:8000/nl2analysis/stream \
     -H "Content-Type: application/json" \
     -d '{"query": "查询学生专业分布", "user_id": "alex", "session_id": "123"}'`