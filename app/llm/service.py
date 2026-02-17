from app.core.config import settings
from app.llm.factory import LLMProviderFactory


class LLMService:

    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.provider = self._load_provider()

    def _load_provider(self):

        # 默认租户
        if self.tenant_id == "default":

            provider = settings.LLM_PROVIDER
            config = {
                "api_key": settings.OPENAI_API_KEY,
                "base_url": settings.BASE_URL,
                "model": settings.LLM_MODEL,
            }

        # BI 租户
        elif self.tenant_id == "tenant_bi":

            provider = settings.TENANT_BI_PROVIDER
            config = {
                "api_key": settings.TENANT_BI_API_KEY,
                "base_url": settings.TENANT_BI_BASE_URL,
                "model": settings.TENANT_BI_MODEL,
            }

        else:
            raise ValueError(f"Unknown tenant_id: {self.tenant_id}")

        return LLMProviderFactory.create(provider, config)

    async def astream(self, prompt: str):
        async for token in self.provider.astream(prompt):
            yield token

    async def ainvoke(self, prompt: str):
        return await self.provider.ainvoke(prompt)
