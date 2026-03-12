"""
SQL Service - Text2SQL functionality.
"""
import json
import logging
from typing import Optional, Dict
from app.core.llm import get_client
from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_sql(
    message: str,
    metadata: str = "",
    model: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Generate SQL from natural language.
    
    Args:
        message: User's question
        metadata: Database schema/metadata
        model: Model name
        **kwargs: Additional parameters
        
    Returns:
        Generated SQL and explanation
    """
    client = get_client(model) if model else get_client()
    
    # Build system prompt with database schema
    system_prompt = f"""你是一个SQL生成专家。请根据用户的问题生成SQL查询。

数据库表结构:
{metadata or '未提供表结构'}

请按照以下格式返回:
1. 首先解释用户想要查询什么
2. 然后生成对应的SQL语句
3. SQL语句用```sql代码块包围

请只生成SELECT查询，不要生成INSERT、UPDATE、DELETE操作。"""
    
    result = client.chat(
        message=message,
        system_prompt=system_prompt,
        **kwargs
    )
    
    # Extract SQL from result
    sql = extract_sql(result)
    
    return {
        "message": message,
        "sql": sql,
        "explanation": result,
        "metadata": metadata
    }


async def generate_sql_v2(
    message: str,
    metadata: str = "",
    model: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Generate SQL V2 - Returns structured JSON.
    
    Args:
        message: User's question
        metadata: Database schema/metadata
        model: Model name
        **kwargs: Additional parameters
        
    Returns:
        Structured SQL response
    """
    client = get_client(model) if model else get_client()
    
    system_prompt = f"""你是一个SQL生成专家。请根据用户的问题生成SQL查询。

数据库表结构:
{metadata or '未提供表结构'}

请以JSON格式返回，包含以下字段:
- "intent": 用户查询意图
- "sql": 生成的SQL语句
- "explanation": 简要说明

只生成SELECT查询。"""
    
    result = client.chat(
        message=message,
        system_prompt=system_prompt,
        **kwargs
    )
    
    # Try to parse as JSON
    try:
        parsed = json.loads(result)
        return parsed
    except:
        # Fallback to simple extraction
        return {
            "intent": message,
            "sql": extract_sql(result),
            "explanation": result
        }


def extract_sql(text: str) -> str:
    """
    Extract SQL from response text.
    
    Args:
        text: Response text
        
    Returns:
        Extracted SQL
    """
    # Try to find SQL in code blocks
    if "```sql" in text:
        start = text.find("```sql") + 6
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()
    
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            return text[start:end].strip()
    
    # Return original text if no code block found
    return text.strip()


# Example metadata loader
async def load_metadata(path: str = "") -> str:
    """
    Load database metadata from file.
    
    Args:
        path: Metadata file path
        
    Returns:
        Metadata as string
    """
    metadata_path = path or settings.sql_metadata_path
    
    if not metadata_path:
        return ""
    
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Metadata file not found: {metadata_path}")
        return ""
    except Exception as e:
        logger.error(f"Failed to load metadata: {e}")
        return ""
