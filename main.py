# main.py
from agent.instantiate_agent_model import agent_model
from toolsets.duckduckgo_toolset import duckduck_tools

def build_agent():
    # get a base agent (your model + provider)
    agent = Agent(model, toolsets=[duckduck_tools()])

    return agent

if __name__ == "__main__":
    agent = build_agent()

    query = "What’s the latest on cybersecurity threats in 2025?"
    result = agent.run_sync(query)
    print(result.output)