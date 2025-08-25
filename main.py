# main.py  (4 spaces everywhere, no tabs)
from __future__ import annotations

import argparse
from typing import List

from agent.instantiate_agent_model import agent_model
from toolsets.duckduckgo_toolset import duckduck_tools


def get_toolsets(disable_tools: bool = False):
    if disable_tools:
        return []
    # add more later (e.g., shodan_tools(), nmap_tools(), etc.)
    return [duckduck_tools()]


def render_output(text: str, plain: bool = False):
    """Pretty print if 'rich' is available; otherwise fall back to print."""
    if plain:
        print(text)
        return
    try:
        from rich.console import Console
        from rich.markdown import Markdown
        Console().print(Markdown(text))
    except Exception:
        print(text)


def run_query(query: str, system_prompt: str | None, disable_tools: bool, plain: bool):
    agent = agent_model(system_prompt=system_prompt)
    result = agent.run_sync(query, toolsets=get_toolsets(disable_tools))
    render_output(result.output.strip(), plain=plain)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="otto",
        description="Run Otto (your cybersecurity agent) with optional toolsets.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Question or task for Otto (e.g., 'top ransomware trends this week').",
    )
    parser.add_argument(
        "--prompt",
        dest="system_prompt",
        default="You are Otto, a concise cybersecurity research agent.",
        help="Override the system prompt passed to the agent.",
    )
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Run without any toolsets.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Plain text output (skip rich Markdown rendering).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    query = " ".join(args.query).strip() or "What's the latest on cybersecurity threats in 2025?"
    run_query(
        query=query,
        system_prompt=args.system_prompt,
        disable_tools=bool(args.no_tools),
        plain=bool(args.plain),
    )