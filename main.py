# main.py  (4 spaces everywhere)
from __future__ import annotations

import argparse

from agent.instantiate_agent_model import agent_model
from toolsets.duckduckgo_toolset import duckduck_tools


def get_toolsets(disable: bool = False):
    return [] if disable else [duckduck_tools()]


def main():
    parser = argparse.ArgumentParser(prog="otto")
    parser.add_argument("query", nargs="*", help="Question for the agent")
    parser.add_argument("--no-tools", action="store_true", help="Run without toolsets")
    args = parser.parse_args()

    q = " ".join(args.query).strip() or "What's new in cybersecurity this week?"

    agent = agent_model()  # bare agent (no system prompt passed)
    result = agent.run_sync(q, toolsets=get_toolsets(args.no_tools))
    print(result.output)


if __name__ == "__main__":
    main()