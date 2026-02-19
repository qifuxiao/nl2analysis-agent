from locust import HttpUser, task, between
import uuid

class NL2AnalysisUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def stream_query(self):
        # 每个虚拟用户生成唯一 session
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        session_id = uuid.uuid4().hex

        payload = {
            "query": "查询学生专业分布",
            "user_id": user_id,
            "session_id": session_id
        }

        with self.client.post("/nl2analysis/stream", json=payload, stream=True, catch_response=True) as response:
            for line in response.iter_lines():
                if line:
                    # 可以打印或统计每行流式数据
                    print(line.decode())
            response.success()
