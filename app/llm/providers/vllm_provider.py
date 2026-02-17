'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:34:04
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:34:13
FilePath: /nl2analysis-agent/app/llm/providers/vllm_provider.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import httpx
from app.llm.base import BaseLLMProvider


class VLLMProvider(BaseLLMProvider):

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    async def astream(self, prompt: str):
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True
                }
            ) as resp:

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        yield line[6:]
