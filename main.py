# main.py
from agent.instantiate_agent_model import agent_model
from toolsets.duckduckgo_toolset import duckduck_tools

if __name__ == "__main__":
    agent = agent_model()  # bare agent
    toolset = duckduck_tools()

    query = "What's the latest on cybersecurity threats in 2025?"
    result = agent.run_sync(query, toolsets=[toolset])  # pass toolsets here
    print(result.output)