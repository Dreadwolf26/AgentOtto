# duckduckgo_toolset.py
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.toolsets import FunctionToolset

def duckduck_tools() -> FunctionToolset:
    """
    Returns a FunctionToolset that wraps DuckDuckGo search.
    Can be imported and plugged into your Agent.
    """
    return FunctionToolset(tools=[duckduckgo_search_tool()])