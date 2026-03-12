"""
LLM client factory and provider management.
"""
import logging
from typing import Optional, Dict, Any, Union
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from app.core.config import settings, get_llm_config

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client supporting multiple providers.
    
    Supported providers:
    - OpenAI (GPT-4, GPT-4o, GPT-4o-mini)
    - Anthropic (Claude 3)
    - Self-hosted models (via OpenAI-compatible API)
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        provider: Optional[str] = None,
    ):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.model = model or settings.LLM_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client: Optional[Union[ChatOpenAI, ChatAnthropic]] = None
        
    def _get_client(self) -> Union[ChatOpenAI, ChatAnthropic]:
        """Get or create the LLM client instance."""
        if self._client is not None:
            return self._client
            
        if self.provider == "openai" or self.provider not in ("anthropic",):
            # Default to OpenAI-compatible client
            config = get_llm_config()
            self._client = ChatOpenAI(
                model=config.get("model", self.model),
                api_key=config.get("api_key", settings.OPENAI_API_KEY),
                base_url=config.get("base_url"),
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        elif self.provider == "anthropic":
            self._client = ChatAnthropic(
                model=self.model,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
            
        logger.info(f"Initialized LLM client: {self.provider}/{self.model}")
        return self._client
    
    def invoke(
        self,
        message: Union[str, List[BaseMessage]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Synchronous invocation.
        
        Args:
            message: User message (string or messages list)
            system_prompt: Optional system prompt
            
        Returns:
            Model response as string
        """
        client = self._get_client()
        
        # Build messages
        if isinstance(message, str):
            if system_prompt:
                messages = [
                    {"type": "system", "content": system_prompt},
                    {"type": "human", "content": message},
                ]
            else:
                messages = [{"type": "human", "content": message}]
        else:
            messages = message
            
        response = client.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    
    async def ainvoke(
        self,
        message: Union[str, List[BaseMessage]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Asynchronous invocation.
        
        Args:
            message: User message (string or messages list)
            system_prompt: Optional system prompt
            
        Returns:
            Model response as string
        """
        client = self._get_client()
        
        # Build messages
        if isinstance(message, str):
            if system_prompt:
                messages = [
                    {"type": "system", "content": system_prompt},
                    {"type": "human", "content": message},
                ]
            else:
                messages = [{"type": "human", "content": message}]
        else:
            messages = message
            
        response = await client.ainvoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    
    async def astream(
        self,
        message: Union[str, List[BaseMessage]],
        system_prompt: Optional[str] = None,
    ):
        """
        Asynchronous streaming invocation.
        
        Args:
            message: User message (string or messages list)
            system_prompt: Optional system prompt
            
        Yields:
            Response chunks
        """
        client = self._get_client()
        
        # Build messages
        if isinstance(message, str):
            if system_prompt:
                messages = [
                    {"type": "system", "content": system_prompt},
                    {"type": "human", "content": message},
                ]
            else:
                messages = [{"type": "human", "content": message}]
        else:
            messages = message
            
        async for chunk in client.astream(messages):
            yield chunk.content if hasattr(chunk, "content") else str(chunk)


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> LLMClient:
    """
    Get a configured LLM client.
    
    Args:
        model: Model name (defaults to settings.LLM_MODEL)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        LLMClient instance
    """
    return LLMClient(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
