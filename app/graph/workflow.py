"""
LangGraph workflow for the multi-agent system.

This module defines the main graph that orchestrates all agents,
including intent routing, agent execution, and response handling.
"""
import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import AgentState, AgentType, RouterState
from app.agents.router import router_node, should_route_to_agent
from app.agents.nl2sql import nl2sql_agent_node
from app.agents.analysis import analysis_agent_node
from app.agents.file import file_agent_node
from app.agents.search import search_agent_node
from app.agents.general import general_agent_node

logger = logging.getLogger(__name__)


# Build the LangGraph workflow
def create_agent_graph() -> StateGraph:
    """
    Create and compile the main agent workflow.
    
    The graph flow:
    1. Router node - analyzes intent
    2. Conditional edge - routes to appropriate agent
    3. Agent execution nodes (nl2sql/analysis/file/search/general)
    4. Response node - formats final response
    """
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("nl2sql_agent", nl2sql_agent_node)
    workflow.add_node("analysis_agent", analysis_agent_node)
    workflow.add_node("file_agent", file_agent_node)
    workflow.add_node("search_agent", search_agent_node)
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("response", response_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional routing from router
    workflow.add_conditional_edges(
        "router",
        should_route_to_agent,
        {
            "nl2sql": "nl2sql_agent",
            "analysis": "analysis_agent",
            "file": "file_agent",
            "search": "search_agent",
            "general": "general_agent",
        }
    )
    
    # All agents flow to response node
    workflow.add_edge("nl2sql_agent", "response")
    workflow.add_edge("analysis_agent", "response")
    workflow.add_edge("file_agent", "response")
    workflow.add_edge("search_agent", "response")
    workflow.add_edge("general_agent", "response")
    
    # End at response
    workflow.add_edge("response", END)
    
    # Compile with checkpointing for memory
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


async def response_node(state: AgentState) -> AgentState:
    """
    Response node - formats the final response.
    
    This node is called after any agent completes execution.
    It formats the agent's response and adds metadata.
    """
    selected_agent = state.get("selected_agent", AgentType.GENERAL)
    result = state.get("result", "")
    
    # Format response based on agent type
    response = {
        "content": result,
        "agent_type": selected_agent.value if selected_agent else "general",
        "intent_confidence": state.get("intent", {}).get("confidence", 0),
    }
    
    # Add visualization config if present
    if state.get("visualization_config"):
        response["visualization_config"] = state["visualization_config"]
    
    # Add SQL info if NL2SQL agent
    if selected_agent == AgentType.NL2SQL:
        if state.get("sql_query"):
            response["sql_query"] = state["sql_query"]
        if state.get("sql_result"):
            response["data"] = state["sql_result"]
    
    state["agent_response"] = str(response)
    
    return state


# Singleton graph instance
_agent_graph = None


def get_agent_graph() -> StateGraph:
    """
    Get the compiled agent graph (singleton).
    """
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = create_agent_graph()
        logger.info("Agent graph compiled successfully")
    return _agent_graph


async def run_agent(
    message: str,
    user_id: str = "default",
    session_id: str = "default",
    history: list = None,
) -> Dict[str, Any]:
    """
    Run the agent with a user message.
    
    Args:
        message: User's input message
        user_id: User identifier
        session_id: Session identifier
        history: Conversation history
        
    Returns:
        Agent response with metadata
    """
    graph = get_agent_graph()
    
    # Prepare initial state
    initial_state = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message,
        "history": history or [],
        "selected_agent": AgentType.GENERAL,
    }
    
    # Run the graph
    try:
        result = await graph.ainvoke(initial_state)
        return result
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return {
            "error": str(e),
            "selected_agent": AgentType.GENERAL,
            "agent_response": "抱歉，处理您的请求时出现错误。",
        }
