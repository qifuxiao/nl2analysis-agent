'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:33:01
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:33:07
FilePath: /nl2analysis-agent/app/llm/base.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMProvider(ABC):

    @abstractmethod
    async def astream(self, prompt: str) -> AsyncGenerator[str, None]:
        """流式输出"""
        pass

    @abstractmethod
    async def ainvoke(self, prompt: str) -> str:
        """非流式调用"""
        pass
