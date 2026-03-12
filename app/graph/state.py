"""
LangGraph state definitions for the multi-agent system.
"""
from typing import TypedDict, List, Dict, Any, Optional
from enum import Enum


class AgentType(str, Enum):
    """Supported agent types."""
    NL2SQL = "nl2sql"
    ANALYSIS = "analysis"
    FILE = "file"
    SEARCH = "search"
    GENERAL = "general"
    UNKNOWN = "unknown"


class IntentResult(TypedDict):
    """Intent detection result."""
    agent_type: AgentType
    confidence: float
    reasoning: str
    extracted_params: Dict[str, Any]


class AgentState(TypedDict):
    """
    Main state for the multi-agent system.
    
    This state is passed through the LangGraph workflow,
    carrying all necessary information between nodes.
    """
    # User identification
    user_id: str
    session_id: str
    
    # Current message
    message: str
    history: List[Dict[str, Any]]
    
    # Intent detection
    intent: Optional[IntentResult]
    
    # Agent routing
    selected_agent: Optional[AgentType]
    agent_response: Optional[str]
    
    # NL2SQL specific
    sql_query: Optional[str]
    sql_result: Optional[List[Dict[str, Any]]]
    sql_error: Optional[str]
    
    # Analysis specific
    analysis_result: Optional[str]
    visualization_config: Optional[Dict[str, Any]]
    
    # File operations
    file_operation: Optional[str]
    file_path: Optional[str]
    file_content: Optional[str]
    
    # Search results
    search_results: Optional[List[Dict[str, str]]]
    
    # General chat
    general_response: Optional[str]
    
    # Error handling
    error: Optional[str]
    error_agent: Optional[AgentType]
    
    # Metadata
    tokens_used: Optional[int]
    processing_time: Optional[float]


class RouterState(TypedDict):
    """
    State for the intent router node.
    Used to determine which agent should handle the request.
    """
    user_id: str
    session_id: str
    message: str
    history: List[Dict[str, Any]]
    intent: Optional[IntentResult]
    selected_agent: Optional[AgentType]


class AgentExecutionState(TypedDict):
    """
    State for individual agent execution.
    """
    user_id: str
    session_id: str
    message: str
    history: List[Dict[str, Any]]
    intent: IntentResult
    result: Optional[str]
    error: Optional[str]
