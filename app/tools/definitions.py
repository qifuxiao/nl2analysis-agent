"""
Tool definitions for the multi-agent system.

This module defines the tools available to each agent using LangChain's @tool decorator.
"""
import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_core.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Database Tools (for NL2SQL Agent)
# ============================================================================

def get_db_engine() -> Optional[Engine]:
    """Create database engine."""
    if not settings.DB_PASSWORD:
        logger.warning("DB_PASSWORD not set, skipping database connection")
        return None
    
    try:
        if settings.DB_TYPE == "postgres":
            url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        elif settings.DB_TYPE == "mysql":
            url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        else:
            url = f"sqlite:///{settings.DB_NAME}"
        
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Database connection established: {settings.DB_TYPE}://{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None


@tool
def execute_sql(query: str) -> str:
    """
    Execute a SQL query on the database and return results.
    
    Args:
        query: SQL query to execute (SELECT only for safety)
        
    Returns:
        Query results as JSON string or error message
    """
    # Safety check - only allow SELECT queries
    query = query.strip()
    if not query.upper().startswith("SELECT"):
        return json.dumps({"error": "Only SELECT queries are allowed for safety"})
    
    try:
        engine = get_db_engine()
        if not engine:
            return json.dumps({"error": "Database connection not available"})
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = [dict(row._mapping) for row in result.fetchall()]
            
            # Limit results to prevent huge outputs
            if len(rows) > 1000:
                rows = rows[:1000]
                rows.append({"_note": f"Truncated to 1000 rows, total: {len(rows)}"})
            
            return json.dumps(rows, default=str, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        return json.dumps({"error": str(e)})


@tool
def get_table_schema(tables: Optional[List[str]] = None) -> str:
    """
    Get database table schemas for reference.
    
    Args:
        tables: Optional list of table names. If None, returns all tables.
        
    Returns:
        Table schema information as JSON string
    """
    try:
        engine = get_db_engine()
        if not engine:
            return json.dumps({"error": "Database connection not available"})
        
        with engine.connect() as conn:
            # Get table list
            if settings.DB_TYPE == "postgres":
                table_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            else:
                table_query = text("SHOW TABLES")
            
            result = conn.execute(table_query)
            table_names = [row[0] for row in result.fetchall()]
            
            # Filter if specific tables requested
            if tables:
                table_names = [t for t in table_names if t in tables]
            
            # Get columns for each table
            schemas = {}
            for table in table_names:
                if settings.DB_TYPE == "postgres":
                    col_query = text("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = :table
                        ORDER BY ordinal_position
                    """)
                else:
                    col_query = text(f"DESCRIBE {table}")
                
                try:
                    cols = conn.execute(col_query, {"table": table})
                    schemas[table] = [dict(row._mapping) for row in cols.fetchall()]
                except:
                    schemas[table] = []
            
            return json.dumps(schemas, indent=2, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        return json.dumps({"error": str(e)})


# ============================================================================
# Web Search Tools (for Search Agent)
# ============================================================================

@tool
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for current information.
    
    Args:
        query: Search query
        max_results: Maximum number of results (default 5)
        
    Returns:
        Search results as JSON string
    """
    # Try Tavily first
    if settings.TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            results = client.search(query=query, max_results=max_results)
            return json.dumps([
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content", "")[:500],
                }
                for r in results.get("results", [])
            ], ensure_ascii=False)
        except ImportError:
            logger.warning("tavily package not installed")
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
    
    # Fallback to Brave Search via API
    if settings.BRAVE_API_KEY:
        try:
            async def brave_search():
                headers = {"Accept": "application/json", "X-Subscription-Token": settings.BRAVE_API_KEY}
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"https://api.search.brave.com/res/v1/web/search?q={query}&count={max_results}",
                        headers=headers
                    )
                    data = resp.json()
                    return [
                        {
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "content": r.get("description", ""),
                        }
                        for r in data.get("web", {}).get("results", [])
                    ]
            
            import asyncio
            results = asyncio.run(brave_search())
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Brave search failed: {e}")
    
    return json.dumps({"error": "No search API configured. Set TAVILY_API_KEY or BRAVE_API_KEY in environment."})


# ============================================================================
# File Tools (for File Agent)
# ============================================================================

import os
import aiofiles
from pathlib import Path


@tool
def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default utf-8)
        
    Returns:
        File content as string or error message
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return json.dumps({"error": f"File not found: {file_path}"})
        
        # Security: prevent reading sensitive files
        sensitive_patterns = ["/etc/", "/root/.ssh/", "/etc/passwd"]
        if any(pattern in str(path) for pattern in sensitive_patterns):
            return json.dumps({"error": "Access denied: sensitive path"})
        
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        
        # Limit content size
        if len(content) > 100000:
            content = content[:100000] + "\n... (truncated)"
        
        return content
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def write_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding (default utf-8)
        
    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        
        return json.dumps({"success": True, "file_path": str(path)})
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def list_files(directory: str = ".", pattern: str = "*") -> str:
    """
    List files in a directory.
    
    Args:
        directory: Directory to list
        pattern: File pattern to match (default *)
        
    Returns:
        File list as JSON string
    """
    try:
        path = Path(directory)
        if not path.exists():
            return json.dumps({"error": f"Directory not found: {directory}"})
        
        if not path.is_dir():
            return json.dumps({"error": f"Not a directory: {directory}"})
        
        files = [
            {
                "name": f.name,
                "type": "directory" if f.is_dir() else "file",
                "size": f.stat().st_size if f.is_file() else None,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            }
            for f in path.glob(pattern)
        ]
        
        return json.dumps(files, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# Data Analysis Tools (for Analysis Agent)
# ============================================================================

@tool
def analyze_data(data_json: str, analysis_type: str = "summary") -> str:
    """
    Analyze data and return insights.
    
    Args:
        data_json: Data in JSON format (list of dicts)
        analysis_type: Type of analysis - "summary", "trends", "correlations", "outliers"
        
    Returns:
        Analysis results as string
    """
    try:
        import pandas as pd
        
        data = json.loads(data_json)
        if not data:
            return json.dumps({"error": "No data provided"})
        
        df = pd.DataFrame(data)
        
        if analysis_type == "summary":
            result = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include='number').columns) > 0 else {},
                "missing_values": df.isnull().sum().to_dict(),
            }
        
        elif analysis_type == "trends":
            numeric_cols = df.select_dtypes(include='number').columns
            if len(numeric_cols) > 0:
                result = {
                    "trend_columns": list(numeric_cols),
                    "mean": df[numeric_cols].mean().to_dict(),
                    "std": df[numeric_cols].std().to_dict(),
                }
            else:
                result = {"error": "No numeric columns for trend analysis"}
        
        elif analysis_type == "correlations":
            numeric_df = df.select_dtypes(include='number')
            if len(numeric_df.columns) > 1:
                result = {"correlations": numeric_df.corr().to_dict()}
            else:
                result = {"error": "Need at least 2 numeric columns for correlation"}
        
        elif analysis_type == "outliers":
            numeric_cols = df.select_dtypes(include='number').columns
            outliers = {}
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outlier_rows = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
                outliers[col] = len(outlier_rows)
            result = {"outliers": outliers}
        
        else:
            result = {"error": f"Unknown analysis type: {analysis_type}"}
        
        return json.dumps(result, default=str, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def generate_chart_config(data_json: str, chart_type: str = "bar") -> str:
    """
    Generate chart configuration for visualization.
    
    Args:
        data_json: Data in JSON format
        chart_type: Type of chart - "bar", "line", "pie", "scatter"
        
    Returns:
        Chart.js configuration as JSON string
    """
    try:
        data = json.loads(data_json)
        if not data:
            return json.dumps({"error": "No data provided"})
        
        df = pd.DataFrame(data)
        
        # Try to detect x and y axes
        columns = list(df.columns)
        
        if chart_type == "bar":
            config = {
                "type": "bar",
                "data": {
                    "labels": df[columns[0]].astype(str).tolist() if len(columns) > 0 else [],
                    "datasets": [{
                        "label": columns[1] if len(columns) > 1 else "Value",
                        "data": df[columns[1]].tolist() if len(columns) > 1 else df[columns[0]].tolist(),
                    }]
                }
            }
        elif chart_type == "line":
            config = {
                "type": "line",
                "data": {
                    "labels": df[columns[0]].astype(str).tolist() if len(columns) > 0 else [],
                    "datasets": [{
                        "label": columns[1] if len(columns) > 1 else "Value",
                        "data": df[columns[1]].tolist() if len(columns) > 1 else df[columns[0]].tolist(),
                        "fill": False,
                    }]
                }
            }
        elif chart_type == "pie":
            config = {
                "type": "pie",
                "data": {
                    "labels": df[columns[0]].astype(str).tolist()[:10] if len(columns) > 0 else [],
                    "datasets": [{
                        "data": df[columns[1]].tolist()[:10] if len(columns) > 1 else df[columns[0]].tolist()[:10],
                    }]
                }
            }
        else:
            config = {"error": f"Unknown chart type: {chart_type}"}
        
        return json.dumps(config, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)})


# ============================================================================
# Tool Collections
# ============================================================================

# Database tools for NL2SQL agent
db_tools = [execute_sql, get_table_schema]

# Search tools
search_tools = [web_search]

# File tools
file_tools = [read_file, write_file, list_files]

# Analysis tools
analysis_tools = [analyze_data, generate_chart_config]

# All tools combined
all_tools = db_tools + search_tools + file_tools + analysis_tools


def get_tools_for_agent(agent_type: str) -> List:
    """Get tools for a specific agent type."""
    mapping = {
        "nl2sql": db_tools,
        "search": search_tools,
        "file": file_tools,
        "analysis": analysis_tools,
    }
    return mapping.get(agent_type.lower(), [])
