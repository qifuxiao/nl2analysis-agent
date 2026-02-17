'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:34:39
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:53:06
FilePath: /nl2analysis-agent/app/llm/factory.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.llm.providers.openai_provider import OpenAIProvider
from app.llm.providers.vllm_provider import VLLMProvider


class LLMProviderFactory:

    @staticmethod
    def create(provider_name: str, config: dict):

        if provider_name == "openai":
            return OpenAIProvider(**config)

        elif provider_name == "deepseek":
            return DeepSeekProvider(**config)

        elif provider_name == "vllm":
            return VLLMProvider(**config)

        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
