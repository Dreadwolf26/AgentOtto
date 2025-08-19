# duckduckgo_toolset.py
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.toolsets import FunctionToolset

# wrap DuckDuckGo in a Toolset
duckduckgo_toolset = FunctionToolset(tools=[duckduckgo_search_tool()])
