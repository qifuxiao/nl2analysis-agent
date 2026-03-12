"""
Basic tests for the agent system.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestIntentRouter:
    """Test intent router."""
    
    def test_rule_based_nl2sql_detection(self):
        """Test rule-based NL2SQL detection."""
        from app.agents.router import IntentRouter
        from app.graph.state import AgentType
        
        router = IntentRouter()
        result = router._rule_based_detect("查询销售额有多少")
        
        assert result is not None
        assert result.agent_type == AgentType.NL2SQL
    
    def test_rule_based_analysis_detection(self):
        """Test rule-based analysis detection."""
        from app.agents.router import IntentRouter
        from app.graph.state import AgentType
        
        router = IntentRouter()
        result = router._rule_based_detect("分析本月销售趋势")
        
        assert result is not None
        assert result.agent_type == AgentType.ANALYSIS
    
    def test_rule_based_file_detection(self):
        """Test rule-based file detection."""
        from app.agents.router import IntentRouter
        from app.graph.state import AgentType
        
        router = IntentRouter()
        result = router._rule_based_detect("读取文件内容")
        
        assert result is not None
        assert result.agent_type == AgentType.FILE
    
    def test_rule_based_search_detection(self):
        """Test rule-based search detection."""
        from app.agents.router import IntentRouter
        from app.graph.state import AgentType
        
        router = IntentRouter()
        result = router._rule_based_detect("搜索最新新闻")
        
        assert result is not None
        assert result.agent_type == AgentType.SEARCH


class TestMemoryBackend:
    """Test memory backend."""
    
    def test_in_memory_storage(self):
        """Test in-memory storage."""
        from app.memory.backend import MemoryBackend, ChatMessage
        
        backend = MemoryBackend(use_redis=False)
        
        # Save message
        msg = ChatMessage(role="user", content="Hello")
        backend.save("user1", "session1", msg)
        
        # Load messages
        messages = backend.load("user1", "session1")
        
        assert len(messages) == 1
        assert messages[0].content == "Hello"
        assert messages[0].role == "user"
    
    def test_get_history_for_llm(self):
        """Test history formatting for LLM."""
        from app.memory.backend import MemoryBackend, ChatMessage
        
        backend = MemoryBackend(use_redis=False)
        
        # Save messages
        backend.save("user1", "session1", ChatMessage(role="user", content="Hi"))
        backend", "session1", ChatMessage(role.save("user1="assistant", content="Hello"))
        
        # Get formatted history
        history = backend.get_history_for_llm("user1", "session1")
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"


class TestLLMClient:
    """Test LLM client."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        from app.llm.client import LLMClient
        
        # Should work even without API key (will fail at runtime)
        client = LLMClient(model="gpt-4o-mini")
        
        assert client.model == "gpt-4o-mini"
        assert client.temperature == 0.7


class TestAgentGraph:
    """Test agent graph."""
    
    def test_graph_creation(self):
        """Test graph can be created."""
        from app.graph.workflow import create_agent_graph
        
        graph = create_agent_graph()
        
        assert graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
