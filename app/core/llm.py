"""
LLM Client - OpenAI compatible client for chat service.
Supports any LLM that follows OpenAI API protocol.
"""
import logging
from typing import Optional, Dict, Any, List, Union, AsyncGenerator
from openai import OpenAI
from langchain_openai import ChatOpenAI

from app.core.config import settings, running_models, CONFIGURED_MODELS

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client that supports any OpenAI-compatible API.
    
    Compatible providers:
    - OpenAI (GPT-4, GPT-4o, GPT-3.5)
    - Ollama (local models)
    - vLLM (self-hosted)
    - Azure OpenAI
    - Any OpenAI-compatible API
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        self.model = model or settings.default_model
        self.temperature = temperature or settings.temperature
        self.max_tokens = max_tokens or settings.max_tokens
        
        # Create OpenAI client
        self.client = OpenAI(
            api_key=settings.openai_api_key or "dummy-key",
            base_url=settings.openai_base_url,
        )
        
        logger.info(
            f"LLM Client initialized: model={self.model}, "
            f"base_url={settings.openai_base_url}"
        )
    
    def chat(
        self,
        message: Union[str, List[Dict]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Synchronous chat completion.
        
        Args:
            message: User message or messages list
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Returns:
            Model response as string
        """
        messages = self._build_messages(message, system_prompt)
        
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stream=False,
            **kwargs
        )
        
        return response.choices[0].message.content or ""
    
    def chat_stream(
        self,
        message: Union[str, List[Dict]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat completion.
        
        Args:
            message: User message or messages list
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        messages = self._build_messages(message, system_prompt)
        
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            stream=True,
            **kwargs
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _build_messages(
        self,
        message: Union[str, List[Dict]],
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Build messages list from input."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if isinstance(message, str):
            messages.append({"role": "user", "content": message})
        else:
            messages.extend(message)
        
        return messages


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def get_client(model: Optional[str] = None) -> LLMClient:
    """Get LLM client with optional model override."""
    return LLMClient(model=model)


def list_config_models() -> List[Dict[str, Any]]:
    """Get list of configured models."""
    return CONFIGURED_MODELS


def list_running_models() -> Dict[str, bool]:
    """Get running models status."""
    return running_models.copy()


def switch_model(model_id: str) -> Dict[str, Any]:
    """Switch default model."""
    if model_id not in running_models:
        return {"success": False, "message": f"Model {model_id} not found"}
    
    # Update running status
    for k in running_models:
        running_models[k] = (k == model_id)
    
    running_models["default"] = model_id
    
    return {
        "success": True,
        "message": f"Switched to model {model_id}",
        "current_model": model_id
    }
