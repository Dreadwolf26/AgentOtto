# main.py  (4 spaces, no tabs)
from __future__ import annotations

import argparse
import json

from agent.instantiate_agent_model import agent_model

# toolsets as Toolsets (for agent-driven mode)
from toolsets.duckduckgo_toolset import duckduck_tools
from toolsets.nmap_toolset import nmap_tools
from toolsets.cve_toolset import cve_tools
from toolsets.prioritize_toolset import prioritize_tools

# tool functions (for pipeline mode)
from toolsets.nmap_toolset import nmap_scan
from toolsets.cve_toolset import cve_enrich
from toolsets.prioritize_toolset import prioritize


def get_toolsets(disable: bool = False):
    if disable:
        return []
    return [
        duckduck_tools(),
        nmap_tools(),
        cve_tools(),
        prioritize_tools(),
    ]


def run_agent_mode(query: str, target: str | None, nmap_args: str | None, disable_tools: bool):
    """
    Agent decides which tools to call. If target is provided, we nudge the model
    with a concise instruction, but STILL pass the actual toolsets per-run.
    """
    agent = agent_model()

    if target:
        # lightweight steering text; no system prompt involved
        extra = f"\n\nTask: run nmap_scan on target='{target}'"
        if nmap_args:
            extra += f" with args='{nmap_args}'"
        extra += ", then call cve_enrich on any CVEs, then prioritize the findings."
        query = f"{query.strip()}{extra}"

    result = agent.run_sync(query, toolsets=get_toolsets(disable_tools))
    print(result.output)


def run_pipeline_mode(target: str, nmap_args: str | None, summarize_with_agent: bool):
    """
    Deterministic pipeline: nmap -> enrich -> prioritize.
    Optionally ask the agent to summarize the final JSON (no toolsets needed for that).
    """
    args = nmap_args or "-sV --script vulners,vuln --top-ports 1000"

    # 1) collect
    scan = nmap_scan(target=target, args=args)
    findings = scan.get("findings", [])

    # unique list of CVE IDs across findings
    cves = sorted({cid for f in findings for cid in f.get("cves", [])})

    # 2) enrich
    meta = cve_enrich(cves) if cves else []

    # 3) prioritize
    flagged = prioritize(findings, meta)

    # print machine-friendly output
    print(json.dumps(
        {
            "target": target,
            "nmap_args": args,
            "findings": findings,
            "cves": cves,
            "enriched": meta,
            "prioritized": flagged,
        },
        indent=2
    ))

    # optional natural-language summary from the model
    if summarize_with_agent:
        agent = agent_model()
        prompt = (
            "Summarize the following prioritized findings for a bug-bounty report. "
            "Be concise and list high-severity issues first.\n\n"
            + json.dumps(flagged)
        )
        summary = agent.run_sync(prompt).output
        print("\n----- SUMMARY -----\n")
        print(summary)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="otto")
    p.add_argument("query", nargs="*", help="Question/task for the agent (agent mode).")
    p.add_argument("--target", help="Target host/domain/CIDR for nmap.")
    p.add_argument("--nmap-args", default=None, help="Extra nmap args (python-nmap).")
    p.add_argument("--no-tools", action="store_true", help="Agent mode: run without toolsets.")
    p.add_argument("--pipeline", action="store_true",
                   help="Run deterministic pipeline: nmap -> enrich -> prioritize (ignores query).")
    p.add_argument("--summarize", action="store_true",
                   help="After pipeline, ask the model to summarize the results.")
    return p.parse_args()


def main():
    args = parse_args()

    # PIPELINE MODE: requires a target
    if args.pipeline:
        if not args.target:
            raise SystemExit("Pipeline mode requires --target")
        run_pipeline_mode(target=args.target, nmap_args=args.nmap_args, summarize_with_agent=args.summarize)
        return

    # AGENT MODE
    q = " ".join(args.query).strip() or "Run a vuln scan and report key issues."
    run_agent_mode(query=q, target=args.target, nmap_args=args.nmap_args, disable_tools=args.no_tools)


if __name__ == "__main__":
    main()