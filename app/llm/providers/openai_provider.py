'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:33:31
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:33:48
FilePath: /nl2analysis-agent/app/llm/providers/openai_provider.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from openai import AsyncOpenAI
from app.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):

    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model

    async def astream(self, prompt: str):
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def ainvoke(self, prompt: str):
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
