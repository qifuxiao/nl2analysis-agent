"""
Python SDK for LangGraph Agent.

Usage:
    from agent import AgentClient
    
    # Initialize
    client = AgentClient(base_url="http://localhost:8000")
    
    # Simple chat
    response = client.chat(message="查询销售额")
    
    # Streaming
    for chunk in client.stream_chat(message="分析数据"):
        print(chunk)
"""
import json
import logging
from typing import Optional, Dict, Any, List, Generator, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class AgentException(Exception):
    """Agent SDK exception."""
    pass


class AgentClient:
    """
    Python SDK client for LangGraph Agent API.
    
    Provides synchronous and streaming interfaces for interacting
    with the multi-agent system.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize the client.
        
        Args:
            base_url: API base URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        
        # Setup retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers
        self.headers = {
            "Content-Type": "application/json",
        }
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise AgentException(f"Request failed: {e}")
    
    def chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: str = "default",
        agent_type: Optional[str] = None,
    ) -> "ChatResponse":
        """
        Send a chat message (non-streaming).
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier
            agent_type: Force specific agent type
            
        Returns:
            ChatResponse object
        """
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "stream": False,
        }
        if agent_type:
            payload["agent_type"] = agent_type
        
        response = self._request(
            "POST",
            "/api/v1/agent/chat",
            json=payload
        )
        
        data = response.json()
        return ChatResponse(**data)
    
    def stream_chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: str = "default",
        agent_type: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Send a chat message (streaming).
        
        Args:
            message: User message
            user_id: User identifier
            session_id: Session identifier
            agent_type: Force specific agent type
            
        Yields:
            Response chunks
        """
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "stream": True,
        }
        if agent_type:
            payload["agent_type"] = agent_type
        
        response = self._request(
            "POST",
            "/api/v1/agent/stream",
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if                line = line line:
.decode("utf-8")
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data.get("content", "")
    
    def get_session(
        self,
        user_id: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Get session conversation history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Session data
        """
        response = self._request(
            "GET",
            f"/api/v1/session/{user_id}/{session_id}"
        )
        return response.json()
    
    def clear_session(
        self,
        user_id: str,
        session_id: str,
    ) -> bool:
        """
        Clear session conversation history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if successful
        """
        response = self._request(
            "DELETE",
            f"/api/v1/session/{user_id}/{session_id}"
        )
        return response.status_code == 200
    
    def list_agents(self) -> List[Dict[str, str]]:
        """
        List available agents.
        
        Returns:
            List of available agents
        """
        response = self._request("GET", "/api/v1/agents")
        return response.json().get("agents", [])
    
    def health_check(self) -> bool:
        """
        Check API health.
        
        Returns:
            True if healthy
        """
        try:
            response = self._request("GET", "/health")
            return response.json().get("status") == "healthy"
        except AgentException:
            return False


class ChatResponse:
    """Chat response model."""
    
    def __init__(
        self,
        content: str,
        agent_type: str,
        confidence: float = 0.0,
        session_id: str = "",
        timestamp: str = "",
    ):
        self.content = content
        self.agent_type = agent_type
        self.confidence = confidence
        self.session_id = session_id
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"<ChatResponse agent={self.agent_type} confidence={self.confidence}>"
    
    def __str__(self):
        return self.content


# Async client (requires aiohttp)
class AsyncAgentClient:
    """
    Async Python SDK client for LangGraph Agent API.
    
    Usage:
        async with AsyncAgentClient() as client:
            response = await client.chat(message="Hello")
            async for chunk in client.stream_chat(message="Hello"):
                print(chunk)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 60,
    ):
        import aiohttp
        
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    async def __aenter__(self):
        import aiohttp
        self._session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=self.timeout,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        async with self._session.request(
            method=method,
            url=url,
            **kwargs
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: str = "default",
        agent_type: Optional[str] = None,
    ) -> ChatResponse:
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "stream": False,
        }
        if agent_type:
            payload["agent_type"] = agent_type
        
        data = await self._request("POST", "/api/v1/agent/chat", json=payload)
        return ChatResponse(**data)
    
    async def stream_chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: str = "default",
        agent_type: Optional[str] = None,
    ):
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id,
            "stream": True,
        }
        if agent_type:
            payload["agent_type"] = agent_type
        
        async with self._session.post(
            f"{self.base_url}/api/v1/agent/stream",
            json=payload
        ) as response:
            async for line in response.content:
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        yield data.get("content", "")
    
    async def health_check(self) -> bool:
        try:
            data = await self._request("GET", "/health")
            return data.get("status") == "healthy"
        except Exception:
            return False


# Convenience function
def create_client(
    base_url: str = "http://localhost:8000",
    api_key: Optional[str] = None,
) -> AgentClient:
    """Create a sync agent client."""
    return AgentClient(base_url=base_url, api_key=api_key)
